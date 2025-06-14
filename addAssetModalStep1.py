"""
Step 1: Basic Asset Information (Modular)
- Client selection
- Project selection
- Asset type selection
- Asset name input
"""

import dash_mantine_components as dmc
from dash import html, callback, Output, Input, State
from DBcontroller import DBcontoller

dbc_instance = DBcontoller()

def create_step1_layout():
    """Create the layout for Step 1: Basic Information"""
    return dmc.Stack(
        spacing="md",
        children=[
            dmc.Select(
                label="Client",
                id="modern-asset-client-dropdown",
                placeholder="Select a client",
                data=[],  # Lazy loaded
                required=True,
                style={"width": "100%"}
            ),
            dmc.Select(
                label="Project",
                id="modern-asset-project-dropdown",
                placeholder="Select a project",
                data=[],
                required=True,
                style={"width": "100%"}
            ),
            dmc.Select(
                label="Asset Type",
                id="modern-asset-type-dropdown",
                placeholder="Select asset type",
                data=[
                    {"label": "Development Met Tower", "value": 1},
                    {"label": "Lidar", "value": 2},
                    {"label": "Sodar", "value": 3}
                ],
                required=True,
                style={"width": "100%"}
            ),
            dmc.TextInput(
                label="Asset Name",
                placeholder="Enter asset name",
                id="modern-asset-name-input",
                required=True,
                style={"width": "100%"}
            ),
        ]
    )

@callback(
    Output("modern-asset-project-dropdown", "data"),
    Input("modern-asset-client-dropdown", "value"),
    prevent_initial_call=True,
)
def update_project_dropdown_step1(client_name):
    if not client_name:
        return []
    try:
        client_id = dbc_instance.getClientID(client_name)
        projects = dbc_instance.getProjects(client_id)
        if isinstance(projects, list):
            project_options = [{"label": str(p), "value": str(p)} for p in projects]
        else:
            project_options = []
        return project_options
    except Exception as e:
        print(f"Error updating project dropdown in Step 1: {e}")
        return []

def validate_step1_data(client_name, project_name, asset_type_id, asset_name):
    if not all([client_name, project_name, asset_type_id, asset_name]):
        return False, "All fields are required."
    if len(asset_name.strip()) < 2:
        return False, "Asset name must be at least 2 characters long."
    # Uniqueness check within project (tbl_project_asset)
    try:
        # Get ProjectID from project name and client name
        project_id = dbc_instance.getProjectIdByName(project_name, client_name)
        if project_id:
            # Query tbl_project_asset for this ProjectID and asset_name
            from sqlalchemy import text
            dal = dbc_instance.dal
            engine = dal.dev_conn._engine
            query = text("SELECT 1 FROM tbl_project_asset pa JOIN tbl_asset a ON pa.AssetID = a.AssetID WHERE pa.ProjectID = :project_id AND a.Name = :asset_name")
            with engine.connect() as connection:
                result = connection.execute(query, {"project_id": int(project_id), "asset_name": asset_name}).fetchone()
                if result:
                    return False, f"Asset '{asset_name}' already exists in project '{project_name}'. Please use a different name."
    except Exception as e:
        print(f"Error checking asset uniqueness in tbl_project_asset: {e}")
    return True, "Valid"
