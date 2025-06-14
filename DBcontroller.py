"""
Database controller module for the Dash app.
Responsibilities:
- Acts as an interface between the Dash app and the database access layer.
- Provides methods to fetch and modify data using the `DataAccessLayer`.
- Simplifies database operations for the app by providing higher-level methods.

Modify this file to add new database operations or modify existing ones.
"""
from sqlalchemy import text
from DataAccessLayer import DataAccessLayer as DAL


class DBcontoller(object):
    def __init__(self):
        """
        Initializes the DBcontroller with a single DataAccessLayer instance.
        """
        self.dal = DAL()

    def getTotalProjectCount(self):
        """
        Returns the total number of projects.
        """
        return self.dal.get_total_project_count()
    def getClientsProjectsAssets(self):
        """
        Returns a list of dicts: [{ClientName, ProjectID, ProjectName, AssetCount}, ...]
        """
        df = self.dal.get_clients_projects_assets()
        return df.to_dict(orient="records")
    def getClientsWithProjectCounts(self):
        """
        Returns a list of dicts: [{ClientName: str, ProjectCount: int}, ...]
        """
        df = self.dal.get_clients_with_project_counts()
        # Convert DataFrame to list of dicts for easy use in Dash
        return df.to_dict(orient="records")
    def getAllUsers(self):
        return self.dal.get_all_users()["username"].values.tolist()

    def addUser(self, username):
        return self.dal.add_user(username)

    def getUserID(self, username):
        return self.dal.get_user_id(username)

    def getAllClients(self, username=None):
        if username is None:
            return self.dal.get_all_clients()["Name"].values.tolist()
        else:
            return self.dal.get_all_clients(username)["Name"].values.tolist()

    def getClientID(self, clientName):
        return self.dal.get_client_id(clientName)

    def addClient(self, clientName, userID):
        return self.dal.add_client(clientName, userID)

    def editClient(self, newClientName, oldClientName):
        return self.dal.edit_client(newClientName, oldClientName)

    def getAllProjects(self):
        return self.dal.get_project_list()["Name"].values.tolist()

    def getProjects(self, clientID):
        return self.dal.get_project_list(clientID)["Name"].values.tolist()

    def addProject(self, projectName, clientName): 
        clientID = self.getClientID(clientName)  # Get ClientID using client name
        return self.dal.add_project(projectName, clientID)

    def getProjectAssets(self, projectName):
        return self.dal.get_project_assets(projectName)["Name"].values.tolist()

    def addAsset(self, projectName, assetName, typeID):
        return self.dal.add_asset(projectName, assetName, typeID)

    def getAllParamGroups(self):
        return (
            self.dal.get_all_param_groups()["Param_Group"].drop_duplicates().values.tolist()
        )

    def getCurrentMappings(self, projectName, assetName):
        return self.dal.get_project_asset_params(projectName, assetName)

    def getAddableMappings(self, projectName, assetName, pgName):
        return self.dal.get_addable_asset_params(projectName, assetName, pgName)[
            "column_name"
        ].values.tolist()

    def addParamColMapping(self, projectName, assetName, pgName, colName):
        return self.dal.add_param_group_col_mapping(projectName, assetName, pgName, colName)

    def delParamColMapping(self, projectName, assetName, pgName, colName):
        return self.dal.del_param_group_col_mapping(projectName, assetName, pgName, colName)

    def getAllDetails(self, projectName, assetName):
        details = self.dal.get_raw_details(projectName, assetName)
        # print("Details fetched from DB:", details)
        return details

    def addRawDataDetail(self, projectName, assetName, detailProperty, detailValue):
        return self.dal.add_raw_data_detail(
            projectName, assetName, detailProperty, detailValue
        )

    def updateOrAddRawDataDetail(
        self, projectName, assetName, detailProperty, detailValue
    ):
        # Check if the property exists
        details = self.dal.get_raw_details(projectName, assetName)
        if detailProperty in details["property"].values:
            return self.dal.update_raw_data_detail(
                projectName, assetName, detailProperty, detailValue
            )
        else:
            return self.dal.add_raw_data_detail(
                projectName, assetName, detailProperty, detailValue
            )

    def delRawDataDetail(self, projectName, assetName, detailProperty):
        return self.dal.del_raw_data_detail(projectName, assetName, detailProperty)

    def getAllSensorDetails(self, projectName, assetName):
        return self.dal.get_all_sensor_details(projectName, assetName)

    def updateSensorDetails(self, componentID, col, value):
        self.dal.update_sensor_details(componentID, col, value)
        return

    def getAssetTypes(self):
        df = self.dal.get_asset_types()
        if not df.empty:
            # Format for Dash dropdown: [{'label': 'AssetType Name [AssetTypeId]', 'value': AssetTypeId}, ...]
            return [{'label': f"{row['AssetType']} [{row['AssetTypeId']}]", 'value': row['AssetTypeId']} for index, row in df.iterrows()]
        return []

    def isBaseSenderConfigured(self, entered_base_sender: str) -> bool:
        """
        Checks if the provided base_sender_string exists in the distinct base senders
        from tbl_ingest_config.
        """
        df_base_senders = self.dal.get_distinct_base_senders()
        if not df_base_senders.empty:
            return entered_base_sender in df_base_senders['base_sender'].values
        return False

    def getAssetCounts(self):
        """
        Returns the total number of assets, met towers, and lidars.
        """
        return self.dal.get_asset_counts()

    def get_project_id_by_name(self, client_name, project_name):
        client_id = self.getClientID(client_name)
        if client_id is None:
            # print(f"Client ID not found for client: {client_name}")
            return None
        # Assumes dal.get_project_list(client_id) returns a DataFrame with 'Name' and 'ProjectID'
        # This method in DAL needs to exist and return ProjectID.
        # For now, let's assume get_projects returns a list of names, and we need a way to get ID.
        # A more direct dal.get_project_id(client_id, project_name) would be ideal.
        # Placeholder: if getProjects returns df with ID:
        df_projects = self.dal.get_project_list(client_id) # Removed include_ids=True, as DAL now always includes ProjectID
        if not df_projects.empty and 'ProjectID' in df_projects.columns and project_name in df_projects['Name'].values:
            project_id_series = df_projects[df_projects['Name'] == project_name]['ProjectID']
            if not project_id_series.empty:
                return project_id_series.iloc[0]
        # print(f"Project ID not found for project: {project_name} under client: {client_name}")
        return None # Fallback if ProjectID column is not there or project not found

    def create_new_asset_with_project_link(self, asset_name: str, asset_type_id: int, project_name: str, paired_met_project_asset_id: int = None, existing_asset_id: int = None):
        """
        Orchestrates the creation of a new asset in tbl_asset and its link in tbl_project_asset
        by calling the DAL method that executes the sp_create_asset_and_project_asset stored procedure.
        Accepts an optional existing_asset_id.
        Returns a dictionary with NewAssetID and NewProjectAssetID.
        """
        try:
            result_ids = self.dal.create_asset_and_project_asset(
                asset_name=asset_name,
                asset_type_id=asset_type_id,
                project_name=project_name,
                paired_met_project_asset_id=paired_met_project_asset_id,
                existing_asset_id=existing_asset_id # Pass it to the DAL method
            )
            return result_ids
        except Exception as e:
            # Log error or handle as appropriate for the controller layer
            print(f"Error in DBcontroller creating new asset: {e}")
            raise # Re-raise to be handled by the callback or calling function

    def add_project_asset_file_map(self, map_key: str, project_asset_id: int):
        """
        Calls the DAL method to insert an entry into tbl_project_asset_file_map.
        """
        try:
            self.dal.add_project_asset_file_map_entry(map_key, project_asset_id)
            # print(f"Successfully added file map entry: {map_key}, {project_asset_id}") # Optional: for logging
        except Exception as e:
            print(f"Error in DBcontroller adding file map entry: {e}")
            raise # Re-raise to be handled by the callback

    def get_assets_by_project_and_type(self, project_id, asset_type_id):
        # Assumes a new method in DAL: get_assets_by_project_and_type(project_id, asset_type_id)
        # This DAL method should return a DataFrame with 'ProjectAssetID' and 'Name'
        df_assets = self.dal.get_assets_by_project_and_type(project_id, asset_type_id)
        if not df_assets.empty:
            return [{'label': row['Name'], 'value': row['ProjectAssetID']} for index, row in df_assets.iterrows()]
        return []

    def add_project_asset_detail(self, project_asset_id: int, property_name: str, property_value: str) -> bool:
        """
        Adds a detail entry (e.g., Latitude, Longitude, Elevation) for a given ProjectAssetID
        to the tbl_project_asset_detail table.
        Args:
            project_asset_id (int): The ID of the project asset.
            property_name (str): The name of the property.
            property_value (str): The value of the property.
        Returns:
            bool: True if successful, False otherwise.
        """
        if not all([project_asset_id, property_name, property_value is not None]):
            print("DBController: Missing required arguments for add_project_asset_detail.")
            return False
        try:
            return self.dal.add_project_asset_detail(project_asset_id, property_name, str(property_value))
        except Exception as e:
            print(f"Error in DBcontroller.add_project_asset_detail: {e}")
            return False

    def getClientsProjectsAssetsDetailed(self):
        """
        Returns detailed asset information organized by client and project.
        Includes asset pairing information for Lidars.
        Returns:
            list: List of dicts with asset details including pairing information
        """
        df = self.dal.get_clients_projects_assets_detailed()
        return df.to_dict(orient="records")

    def addSimpleAsset(self, asset_name: str, asset_type_id: int) -> int:
        """
        Simple method to add an asset directly to tbl_asset table.
        Args:
            asset_name (str): The name of the asset
            asset_type_id (int): The AssetTypeID from tbl_asset_type
        Returns:
            int: The newly created AssetID
        """
        return self.dal.add_simple_asset(asset_name, asset_type_id)

    def addProjectAsset(self, project_id: int, asset_name: str, asset_type_id: int, asset_id: int, pair_project_asset_id: int = None) -> int:
        """
        Add an asset to a project in tbl_project_asset.
        Generates ProjectAssetId by fetching MAX(ProjectAssetId) + 1.
        Args:
            project_id (int): The ProjectID from tbl_project
            asset_name (str): The name for this project asset
            asset_type_id (int): The AssetTypeID
            asset_id (int): The AssetID from tbl_asset
            pair_project_asset_id (int, optional): ProjectAssetID to pair with (for Lidar/Sodar)
        Returns:
            int: The newly created ProjectAssetID
        """
        next_project_asset_id = self.dal.get_next_project_asset_id()
        return self.dal.add_project_asset(next_project_asset_id, project_id, asset_name, asset_type_id, asset_id, pair_project_asset_id)

    def getMetTowersByProjectName(self, project_name: str, client_name: str = None):
        """
        Get all Met Towers for a specific project by project name.
        Args:
            project_name (str): The name of the project
            client_name (str, optional): The client name for disambiguation
        Returns:
            list: List of dicts with 'label' and 'value' for dropdown
        """
        try:
            # Get project ID
            if client_name:
                project_id = self.get_project_id_by_name(client_name, project_name)
            else:
                # Try to find project by name alone (may be ambiguous)
                df_projects = self.dal.get_project_list()
                matching_projects = df_projects[df_projects['Name'] == project_name]
                if matching_projects.empty:
                    return []
                project_id = matching_projects.iloc[0]['ProjectID']
            
            if project_id is None:
                return []
            
            # Get Met Towers for this project
            df_met_towers = self.dal.get_met_towers_by_project_id(project_id)
            if not df_met_towers.empty:
                return [{'label': row['Name'], 'value': row['ProjectAssetID']} for index, row in df_met_towers.iterrows()]
            return []
        except Exception as e:
            print(f"Error getting Met Towers for project {project_name}: {e}")
            return []

    def getProjectIdByName(self, project_name: str, client_name: str = None) -> int:
        """
        Get ProjectID by project name, optionally filtered by client.
        Args:
            project_name (str): The name of the project
            client_name (str, optional): The client name for disambiguation
        Returns:
            int: The ProjectID or None if not found
        """
        if client_name:
            return self.get_project_id_by_name(client_name, project_name)
        else:
            # Try to find project by name alone
            df_projects = self.dal.get_project_list()
            matching_projects = df_projects[df_projects['Name'] == project_name]
            if not matching_projects.empty:
                return matching_projects.iloc[0]['ProjectID']
            return None


if __name__ == "__main__":
    dbc = DBcontoller()
    allCPs = dbc.updateSensorDetails("4884", "Height", "59")
