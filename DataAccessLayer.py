# Modularized Scripts 6/20/2024
""" WORKING UP TILL EDIT DETAILS w/ Map
Data access layer module for the Dash app.
This has been modified from the original dal

Responsibilities:
- Handles direct interactions with the SQL Server database.
- Provides methods for executing queries and managing transactions.
- Uses SQLAlchemy to manage database connections and execute SQL commands.

Modify this file to update the database schema interactions or add new queries.
"""

import pandas as pd
import scipy.stats as ss
import urllib, urllib.parse
import numpy as np
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.sql import text


class DataAccessLayer:

    def __init__(self, client=None, project=None, force_platform=None):
        self.client = client
        self.clientID = None
        self.project = project
        self.db_conn = MSSQLRepository()
        self.dev_conn = MSSQLRepository(database="DevDB_stage")
        self._cnn = None

    @property
    def cnn(self):
        if self._cnn is None:
            self._cnn = self.dev_conn.connect()
        return self._cnn

    def get_all_users(self):
        query = f"select username from tbl_user"
        engine = self.dev_conn._engine
        allUsers = pd.read_sql(
            query,
            con=engine,
        )

        return allUsers

    def add_user(self, username):
        query = f"insert into tbl_user values ('{username}')"
        conn = self.cnn.connect().begin()
        self.cnn.connect().execute(query)
        conn.commit()
        conn.close()

        return self.get_all_users()

    def get_user_id(self, username):
        userID = self.cnn.execute(
            f"select top 1 UserID from tbl_user where username like '{username}'",
        ).scalar()

        return userID

    def get_all_clients(self, username=None):
        if username is None:
            query = f"select Name from tbl_client"
        else:
            query = f"select Name from tbl_client inner join tbl_client_user on UserID = (select UserID from tbl_user where username='{username}') and tbl_client.ClientID = tbl_client_user.ClientID"
        engine = self.dev_conn._engine
        allClients = pd.read_sql(
            query,
            con=engine,
        )
        allClients = allClients.sort_values("Name")
        return allClients

    def get_client_id(self, client: str) -> int:
        """
        Returns client ID for the client name.
        Args:
            client (str): the name of the client. must match database entry exactly.
        Returns:
            int: Client ID if found, otherwise raises an exception.
        """
        query = text("SELECT ClientID FROM tbl_client WHERE name = :client")
        result = self.cnn.execute(query, {"client": client}).fetchone()
        
        if result is None:
            raise ValueError(f"Client '{client}' not found in the database.")
        
        return result.ClientID


    def add_client(self, client_name, user_ID):
        query = text("exec sp_add_client_remote :client_name, :user_ID")

        # Verify the client before addition
        existing_clients = self.get_all_clients()
        if client_name in existing_clients["Name"].values:
            raise ValueError(f"Client '{client_name}' already exists in the database.")

        with self.cnn.begin() as transaction:
            try:
                self.cnn.execute(
                    query, {"client_name": client_name, "user_ID": user_ID}
                )
                transaction.commit()
            except Exception as e:
                transaction.rollback()
                raise e

        # Verify the client was added by querying the database
        added_clients = self.get_all_clients()
        if client_name not in added_clients["Name"].values:
            raise RuntimeError(
                f"Client '{client_name}' not found in the database after addition."
            )

        return added_clients

    def edit_client(self, new_client_name, old_client_name):
        query = f"exec sp_update_client_remote '{new_client_name}', '{old_client_name}'"
        conn = self.cnn.connect().begin()
        self.cnn.connect().execute(query)
        conn.commit()
        conn.close()

        return self.get_all_clients()

    def get_project_list(self, clientID=None) -> pd.DataFrame:
        """
        return list of project names for given client id
        or all project names if no client id passed
        Args:
            clientID(int): id to limit project list by. None returns all projects in the db
        Returns:
            DataFrame: consisting of one column -- 'Name'
        """
        engine = self.dev_conn._engine
        if clientID is None:
            # This case might need to fetch ProjectID as well if used by a method needing IDs
            query = text("SELECT ProjectID, Name FROM tbl_project ORDER BY Name")
            project_list_frame = pd.read_sql(query, con=engine)
        else:
            # Ensure ProjectID is selected for use in DBcontroller.get_project_id_by_name
            query = text("SELECT ProjectID, Name FROM tbl_project WHERE ClientID = :client_id ORDER BY Name")
            project_list_frame = pd.read_sql(query, con=engine, params={"client_id": clientID})
        return project_list_frame
        
    def get_project_by_id(self, project_id: int) -> pd.DataFrame:
        """
        Get project information by project ID.
        
        Args:
            project_id (int): The ID of the project
            
        Returns:
            pd.DataFrame: DataFrame with project information including client name and project name
        """
        engine = self.dev_conn._engine
        query = text("""
            SELECT p.ProjectID, p.Name AS ProjectName, c.Name AS ClientName, c.ClientID
            FROM tbl_project p
            JOIN tbl_client c ON p.ClientID = c.ClientID
            WHERE p.ProjectID = :project_id
        """)
        try:
            project_df = pd.read_sql(query, con=engine, params={"project_id": project_id})
            return project_df
        except Exception as e:
            print(f"Error getting project by ID {project_id}: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error

    def add_project(self, project_name, clientID):
        # Check if the project already exists
        existing_projects_df = self.get_project_list(clientID) # This now returns ProjectID and Name
        existing_projects = existing_projects_df["Name"].values.tolist() # Keep extracting only names for the check
        if project_name in existing_projects:
            raise ValueError(f"Project '{project_name}' already exists for client ID '{clientID}'.")

        query = text("exec sp_add_project_remote :project_name, :client_id")
        conn = self.cnn  # Use the existing connection

        with conn.begin() as transaction:
            try:
                conn.execute(query, {"project_name": project_name, "client_id": clientID})
                transaction.commit()
            except Exception as e:
                transaction.rollback()
                raise e

        return self.get_project_list(clientID)
    
    def get_project_assets(self, project_name):
        sql_str = f"select [Name] FROM [dbo].[tbl_project_asset] WHERE ProjectId = (Select [ProjectId] FROM [dbo].[tbl_project] WHERE [dbo].[tbl_project].Name='{project_name}')"
        engine = self.dev_conn._engine
        assets_frame = pd.read_sql(
            sql_str,
            con=engine,
        )
        return assets_frame

    def add_asset(self, project_name, asset_name, typeID):
        existing_assets = self.get_project_assets(project_name)
        if asset_name in existing_assets["Name"].values:
            raise ValueError(f"Asset '{asset_name}' already exists in project '{project_name}'.")

        query = text("exec sp_add_asset_remote :project_name, :asset_name, :type_id")
        conn = self.cnn  # Use the existing connection

        with conn.begin() as transaction:
            try:
                conn.execute(query, {"project_name": project_name, "asset_name": asset_name, "type_id": typeID})
                transaction.commit()
            except Exception as e:
                transaction.rollback()
                raise e

        return self.get_project_assets(project_name)

    def get_asset_types(self) -> pd.DataFrame:
        """
        Returns all asset types from tbl_asset_type.
        Returns:
            DataFrame: consisting of AssetTypeId and AssetType columns.
        """
        query = text("SELECT AssetTypeId, AssetType FROM tbl_asset_type ORDER BY AssetTypeId")
        engine = self.dev_conn._engine # Use the dev_conn for DevDB_stage
        asset_types_frame = pd.read_sql(query, con=engine)
        return asset_types_frame

    def get_distinct_base_senders(self) -> pd.DataFrame:
        """
        Returns a DataFrame with a single column 'base_sender' containing unique base sender strings
        extracted from the 'sender' column of tbl_ingest_config.
        The base sender is the part of the string before the first '|' character, or the whole string if no '|' is present.
        """
        # SQL Server specific query to extract base sender
        query = text("""
            SELECT DISTINCT
                CASE
                    WHEN CHARINDEX('|', sender) > 0 THEN LEFT(sender, CHARINDEX('|', sender) - 1)
                    ELSE sender
                END AS base_sender
            FROM tbl_ingest_config
            WHERE sender IS NOT NULL AND sender != '';
        """)
        engine = self.dev_conn._engine 
        base_senders_frame = pd.read_sql(query, con=engine)
        return base_senders_frame

    def create_asset_and_project_asset(self, asset_name: str, asset_type_id: int, project_name: str, paired_met_project_asset_id: int = None, existing_asset_id: int = None):
        """
        Executes the sp_create_asset_and_project_asset stored procedure.
        Now accepts an optional existing_asset_id.
        Returns a dictionary containing NewAssetID and NewProjectAssetID.
        """
        engine = self.dev_conn._engine
        
        params = {
            'asset_name': asset_name,
            'asset_type_id': asset_type_id,
            'project_name': project_name,
            'selected_paired_met_project_asset_id': paired_met_project_asset_id, # SP handles NULL if None
            'existing_asset_id': existing_asset_id # Pass this to the SP
        }

        sql_query = text("EXEC dbo.sp_create_asset_and_project_asset "
                         "@asset_name=:asset_name, "
                         "@asset_type_id=:asset_type_id, "
                         "@project_name=:project_name, "
                         "@selected_paired_met_project_asset_id=:selected_paired_met_project_asset_id, "
                         "@existing_asset_id=:existing_asset_id")

        try:
            with engine.connect() as connection:
                with connection.begin() as transaction: # Start an explicit transaction
                    result = connection.execute(sql_query, params)
                    row = result.fetchone()
                    if row:
                        transaction.commit() # Commit if SP execution was successful and returned row
                        return {"NewAssetID": row.NewAssetID, "NewProjectAssetID": row.NewProjectAssetID}
                    else:
                        transaction.rollback() # Rollback if SP didn't return expected IDs
                        raise Exception("Stored procedure sp_create_asset_and_project_asset did not return the expected IDs.")
        except Exception as e:
            # The transaction should have been rolled back by the 'with' block if an error occurred
            print(f"Error executing sp_create_asset_and_project_asset: {e}")
            raise

    def add_project_asset_file_map_entry(self, map_key: str, project_asset_id: int):
        """
        Inserts a new entry into tbl_project_asset_file_map.
        MapID is assumed to be an identity column.
        """
        engine = self.dev_conn._engine
        sql_query = text("""
            INSERT INTO dbo.tbl_project_asset_file_map (MapKey, ProjectAssetID)
            VALUES (:map_key, :project_asset_id)
        """)
        params = {
            'map_key': map_key,
            'project_asset_id': project_asset_id
        }
        try:
            with engine.connect() as connection:
                connection.execute(sql_query, params)
                connection.commit()
        except Exception as e:
            print(f"Error inserting into tbl_project_asset_file_map: {e}")
            raise # Re-raise the exception

    def get_assets_by_project_and_type(self, project_id: int, asset_type_id: int) -> pd.DataFrame:
        """
        Returns a DataFrame of assets (ProjectAssetID, Name) for a given project_id and asset_type_id.
        Args:
            project_id (int): The ID of the project.
            asset_type_id (int): The ID of the asset type.
        Returns:
            pd.DataFrame: DataFrame with 'ProjectAssetID' and 'Name' columns.
        """
        engine = self.dev_conn._engine
        query = text("""
            SELECT pa.ProjectAssetID, a.Name
            FROM tbl_project_asset pa
            JOIN tbl_asset a ON pa.AssetID = a.AssetID
            WHERE pa.ProjectID = :project_id AND pa.AssetTypeID = :asset_type_id
            ORDER BY a.Name
        """)
        # Ensure parameters are standard Python integers for pyodbc compatibility
        params = {"project_id": int(project_id), "asset_type_id": int(asset_type_id)}
        assets_df = pd.read_sql(query, con=engine, params=params)
        return assets_df

    def get_project_asset_params(self, project_name, asset_name):
        """
        returns listing of ui default params. is a replacement for hard coded ASSET_TEMPLATE_PARAMS
        Args:
            project_name (str): name of the project to return asset params for
        Returns:
            DataFrame: asset name| param | tuple of column names
        """
        project_name = project_name.replace("_", " ")
        asset_name = asset_name.replace("_", " ")
        engine = self.dev_conn._engine

        sql_str = f"exec sp_get_asset_params '{project_name}', '{asset_name}'"
        # print('data repo 174 ',sql_str)
        assets_frame = pd.read_sql(
            sql_str,
            con=engine,
        )

        # assemble dict from

        param_dict = {}
        for param in assets_frame.param.unique():

            column_list = []
            for column in assets_frame[
                assets_frame["param"] == param
            ].column_name.unique():
                column_list = column_list + [column]

            param_dict[param] = tuple(column_list)

        return param_dict

    def get_addable_asset_params(self, project_name, asset_name, param_group_name):
        query = f"sp_get_addable_asset_params '{project_name}', '{asset_name}', '{param_group_name}'"
        engine = self.dev_conn._engine
        addable = pd.read_sql(
            query,
            con=engine,
        )
        return addable

    def add_param_group_col_mapping(
        self, project_name, asset_name, param_group_name, column_name
    ):
        query = text(
            "exec sp_add_asset_params :project_name, :asset_name, :param_group_name, :column_name"
        )
        with self.cnn.begin() as transaction:
            self.cnn.execute(
                query,
                {
                    "project_name": project_name,
                    "asset_name": asset_name,
                    "param_group_name": param_group_name,
                    "column_name": column_name,
                },
            )
        return self.get_project_asset_params(project_name, asset_name)

    def del_param_group_col_mapping(
        self, project_name, asset_name, param_group_name, column_name
    ):
        query = text(
            "exec sp_del_asset_params :project_name, :asset_name, :param_group_name, :column_name"
        )
        with self.cnn.begin() as transaction:
            self.cnn.execute(
                query,
                {
                    "project_name": project_name,
                    "asset_name": asset_name,
                    "param_group_name": param_group_name,
                    "column_name": column_name,
                },
            )
        return self.get_project_asset_params(project_name, asset_name)

    def get_all_param_groups(self):
        query = f"select Param_Group from tbl_project_asset_attr_set_data_types"
        engine = self.dev_conn._engine
        allPGs = pd.read_sql(
            query,
            con=engine,
        )

        return allPGs

    def get_raw_details(self, project_name, asset_name):
        query = f"exec sp_get_raw_data_details '{project_name}', '{asset_name}'"
        engine = self.dev_conn._engine
        allDetails = pd.read_sql(query, con=engine)
        # print("Raw details from DB:", allDetails)

        return allDetails

    def add_raw_data_detail(self, project_name, asset_name, prop, value):
        query = text(
            "exec sp_add_raw_data_detail :project_name, :asset_name, :prop, :value"
        )
        with self.cnn.begin() as transaction:
            self.cnn.execute(
                query,
                {
                    "project_name": project_name,
                    "asset_name": asset_name,
                    "prop": prop,
                    "value": value,
                },
            )
        return self.get_raw_details(project_name, asset_name)

    def update_raw_data_detail(self, project_name, asset_name, prop, value):
        query = text(
            "exec sp_update_raw_data_detail :project_name, :asset_name, :prop, :value"
        )
        with self.cnn.begin() as transaction:
            self.cnn.execute(
                query,
                {
                    "project_name": project_name,
                    "asset_name": asset_name,
                    "prop": prop,
                    "value": value,
                },
            )
        return self.get_raw_details(project_name, asset_name)

    # I altered the SQL in the db as well, but the SQL's functionality for previous apps is still fully functionaable
    def del_raw_data_detail(self, project_name, asset_name, prop):
        query = text("exec sp_delete_raw_data_detail :project_name, :asset_name, :prop")
        with self.cnn.begin() as transaction:
            self.cnn.execute(
                query,
                {"project_name": project_name, "asset_name": asset_name, "prop": prop},
            )
        return self.get_raw_details(project_name, asset_name)

    def get_all_sensor_details(self, project_name, asset_name):
        query = f"exec sp_get_all_sensors_details '{project_name}', '{asset_name}'"
        engine = self.dev_conn._engine
        sensorsDF = pd.read_sql(
            query,
            con=engine,
        )

        return sensorsDF

    def update_sensor_details(self, componentID, col, value):
        query = f"exec sp_update_sensors_details '{componentID}', '{col}', '{value}'"
        conn = self.cnn.connect().begin()
        self.cnn.connect().execute(query)
        conn.commit()
        conn.close()

        return

    def get_clients_projects_assets(self):
        """
        Returns a DataFrame with columns: ClientName, ProjectID, ProjectName, AssetCount
        """
        query = """
            SELECT
                c.Name AS ClientName,
                p.ProjectID,
                p.Name AS ProjectName,
                COUNT(pa.ProjectAssetID) AS AssetCount
            FROM tbl_client c
            LEFT JOIN tbl_project p ON c.ClientID = p.ClientID
            LEFT JOIN tbl_project_asset pa ON p.ProjectID = pa.ProjectID
            GROUP BY c.ClientID, c.Name, p.ProjectID, p.Name
            ORDER BY c.Name, p.Name
        """
        engine = self.dev_conn._engine
        df = pd.read_sql(query, con=engine)
        return df

    def get_clients_with_project_counts(self):
        """
        Returns a DataFrame with each client and the number of projects they have.
        Columns: ClientName, ProjectCount
        """
        query = """
            SELECT c.Name AS ClientName, COUNT(p.ProjectID) AS ProjectCount
            FROM tbl_client c
            LEFT JOIN tbl_project p ON c.ClientID = p.ClientID
            GROUP BY c.ClientID, c.Name
            ORDER BY c.Name
        """
        engine = self.dev_conn._engine
        df = pd.read_sql(query, con=engine)
        return df

    def get_total_project_count(self):
        """
        Returns the total number of projects in tbl_project.
        """
        query = "SELECT COUNT(ProjectID) FROM tbl_project"
        engine = self.dev_conn._engine
        total_projects = pd.read_sql(query, con=engine).iloc[0, 0]
        return total_projects

    def get_asset_counts(self):
        """
        Returns the total number of assets, met towers, and lidars.
        """
        query = """
            SELECT
                (SELECT COUNT(*) FROM tbl_asset) AS TotalAssets,
                (SELECT COUNT(*) FROM tbl_asset WHERE AssetTypeID = 1) AS MetTowers,
                (SELECT COUNT(*) FROM tbl_asset WHERE AssetTypeID = 2) AS Lidars
        """
        engine = self.dev_conn._engine
        df = pd.read_sql(query, con=engine)
        return df.iloc[0]

    def get_next_project_asset_id(self) -> int:
        """
        Retrieves the next available ProjectAssetId from tbl_project_asset
        by finding the current maximum ID and adding 1.
        Returns:
            int: The next ProjectAssetId to be used.
        """
        engine = self.dev_conn._engine
        query = text("SELECT ISNULL(MAX(ProjectAssetId), 0) + 1 AS NextId FROM tbl_project_asset")
        with engine.connect() as connection:
            result = connection.execute(query)
            next_id = result.scalar_one()
            return int(next_id)

    def get_clients_projects_assets_detailed(self):
        """
        Returns detailed asset information organized by client and project.
        Includes asset pairing information for Lidars.
        Uses the Name from tbl_project_asset (not tbl_asset) to get specific asset names like ZX300-1168A, ZX300-1168B, etc.
        """
        query = """
            SELECT
                c.Name AS ClientName,
                p.Name AS ProjectName,
                pa.ProjectAssetID,
                pa.Name AS AssetName,
                at.AssetType,
                pa.PairProjectAssetID,
                paired_pa.Name AS PairedAssetName,
                CASE 
                    WHEN pa.PairProjectAssetID IS NOT NULL THEN paired_pa.Name
                    ELSE NULL
                END AS PairedMET
            FROM tbl_client c
            LEFT JOIN tbl_project p ON c.ClientID = p.ClientID
            LEFT JOIN tbl_project_asset pa ON p.ProjectID = pa.ProjectID
            LEFT JOIN tbl_asset_type at ON pa.AssetTypeID = at.AssetTypeID
            LEFT JOIN tbl_project_asset paired_pa ON pa.PairProjectAssetID = paired_pa.ProjectAssetID
            WHERE pa.ProjectAssetID IS NOT NULL
            ORDER BY c.Name, p.Name, pa.Name
        """
        engine = self.dev_conn._engine
        df = pd.read_sql(query, con=engine)
        return df

    def add_simple_asset(self, asset_name: str, asset_type_id: int) -> int:
        """
        Simple method to insert directly into tbl_asset table.
        Args:
            asset_name (str): The name of the asset
            asset_type_id (int): The AssetTypeID from tbl_asset_type
        Returns:
            int: The newly created AssetID
        """
        # Insert new asset without global uniqueness check
        insert_query = text("""
            INSERT INTO tbl_asset (name, AssetTypeID) 
            OUTPUT INSERTED.AssetID
            VALUES (:asset_name, :asset_type_id)
        """)
        engine = self.dev_conn._engine
        
        with engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    result = connection.execute(insert_query, {
                        "asset_name": asset_name, 
                        "asset_type_id": asset_type_id
                    })
                    new_asset_id = result.fetchone().AssetID
                    transaction.commit()
                    print(f"DEBUG: Successfully inserted asset '{asset_name}' with ID {new_asset_id}")
                    return new_asset_id
                except Exception as e:
                    transaction.rollback()
                    print(f"DEBUG: Error inserting asset: {e}")
                    raise

    def add_project_asset(self, project_asset_id: int, project_id: int, asset_name: str, asset_type_id: int, asset_id: int, pair_project_asset_id: int = None) -> int:
        """
        Insert into tbl_project_asset table.
        Args:
            project_asset_id (int): The ProjectAssetID for the new record.
            project_id (int): The ProjectID from tbl_project
            asset_name (str): The name for this project asset
            asset_type_id (int): The AssetTypeID
            asset_id (int): The AssetID from tbl_asset
            pair_project_asset_id (int, optional): ProjectAssetID to pair with (for Lidar/Sodar)
        Returns:
            int: The newly created ProjectAssetID
        """
        engine = self.dev_conn._engine
        
        insert_query = text("""
            INSERT INTO tbl_project_asset (ProjectAssetId, ProjectID, Name, AssetTypeID, AssetID, PairProjectAssetID)
            OUTPUT INSERTED.ProjectAssetID
            VALUES (:project_asset_id, :project_id, :asset_name, :asset_type_id, :asset_id, :pair_project_asset_id)
        """)
        
        # Convert all parameters to standard Python types to avoid numpy/pandas type issues
        params = {
            "project_asset_id": int(project_asset_id),
            "project_id": int(project_id),
            "asset_name": str(asset_name),
            "asset_type_id": int(asset_type_id),
            "asset_id": int(asset_id),
            "pair_project_asset_id": int(pair_project_asset_id) if pair_project_asset_id is not None else None
        }
        
        print(f"DEBUG: Inserting project asset with params: {params}")
        
        with engine.connect() as connection:
            with connection.begin() as transaction:
                try:
                    result = connection.execute(insert_query, params)
                    new_project_asset_id = result.fetchone().ProjectAssetID
                    transaction.commit()
                    print(f"DEBUG: Successfully inserted project asset '{asset_name}' with ProjectAssetID {new_project_asset_id}")
                    return new_project_asset_id
                except Exception as e:
                    transaction.rollback()
                    print(f"DEBUG: Error inserting project asset: {e}")
                    raise

    def get_met_towers_by_project_id(self, project_id: int) -> pd.DataFrame:
        """
        Get all Met Towers (AssetTypeID = 1) for a specific project.
        Args:
            project_id (int): The ProjectID
        Returns:
            pd.DataFrame: DataFrame with 'ProjectAssetID' and 'Name' columns
        """
        return self.get_assets_by_project_and_type(project_id, 1)  # 1 = Met Tower

load_dotenv()
class MSSQLRepository:
    def __init__(
        self,
        server=None,
        database=None,
        uid=None,
        pwd=None,
    ):
        self._server = server or os.getenv('DB_SERVER')
        self._database = database or os.getenv('DB_DATABASE')
        self._UID = uid or os.getenv('DB_UID')
        self._pwd = pwd or os.getenv('DB_PWD')
        self.cnn = None

        if all(x is not None for x in [self._server, self._database, self._UID, self._pwd]):
            params = urllib.parse.quote_plus(
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self._server};DATABASE={self._database};UID={self._UID};PWD={self._pwd}"
            )
            conn_str = f"mssql+pyodbc:///?odbc_connect={params}"
            self._engine = create_engine(conn_str)
        else:
            raise ValueError(
                "MSSQLRepository: must provide server, database, uid, and pwd to create an instance"
            )
        
    def connect(self):
        connection = self._engine.connect()

        return connection

    def add_project_asset_detail(self, project_asset_id: int, property_name: str, property_value: str):
        """
        Inserts a new record into tbl_project_asset_detail.
        ProjectAssetDetailID is an IDENTITY column and will be auto-generated.
        Args:
            project_asset_id (int): The ID of the project asset.
            property_name (str): The name of the property (e.g., "Latitude", "Longitude", "Elevation").
            property_value (str): The value of the property.
        Returns:
            bool: True if insertion was successful, False otherwise.
        """
        sql_query = text("""
            INSERT INTO dbo.tbl_project_asset_detail (ProjectAssetID, property, value)
            VALUES (:project_asset_id, :property_name, :property_value)
        """)
        params = {
            'project_asset_id': project_asset_id,
            'property_name': property_name,
            'property_value': str(property_value) # Ensure value is a string
        }
        try:
            with self.cnn.begin() as transaction: # Use self.cnn which is the DevDB_stage connection
                self.cnn.execute(sql_query, params)
                transaction.commit()
            return True
        except Exception as e:
            print(f"Database error in add_project_asset_detail: {e}")
            # Consider logging the error more formally
            # If a transaction was active and an error occurred, 'with self.cnn.begin()' handles rollback.
            return False
