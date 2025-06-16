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
        gap="md",
        children=[
            dmc.Select(
                label="Client",
                id="modern-asset-client-dropdown-new", # ID Updated
                placeholder="Select a client",
                data=[],  # Lazy loaded
                required=True,
                style={"width": "100%"}
            ),
            dmc.Select(
                label="Project",
                id="modern-asset-project-dropdown-new", # ID Updated
                placeholder="Select a project",
                data=[],
                required=True,
                style={"width": "100%"}
            ),
            dmc.Select(
                label="Asset Type",
                id="modern-asset-type-dropdown-new", # ID Updated
                placeholder="Select asset type",
                data=[
                    {"label": "Development Met Tower", "value": "1"},
                    {"label": "Lidar", "value": "2"},
                    {"label": "Sodar", "value": "3"}
                ],
                required=True,
                style={"width": "100%"}
            ),
            dmc.TextInput(
                label="Asset Name",
                placeholder="Enter asset name",
                id="modern-asset-name-input-new", # ID Updated
                required=True,
                style={"width": "100%"}
            ),
            dmc.Alert(
                id="step1-alert-message-new",
                title="Input Error!",
                color="red",
                hide=True,
                withCloseButton=True,
                children="",
                mt="md"
            )
        ]
    )

@callback(
    Output("modern-asset-project-dropdown-new", "data"), # ID Updated
    Input("modern-asset-client-dropdown-new", "value"), # ID Updated
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
    error_messages = []
    if not client_name:
        error_messages.append("Client selection is required.")
    if not project_name:
        error_messages.append("Project selection is required.")
    if not asset_type_id:
        error_messages.append("Asset type selection is required.")
    if not asset_name:
        error_messages.append("Asset name is required.")
    elif len(asset_name.strip()) < 2:
        error_messages.append("Asset name must be at least 2 characters long.")

    if error_messages:
        return False, " ".join(error_messages)

    # Uniqueness check within project (tbl_project_asset)
    try:
        project_id = dbc_instance.getProjectIdByName(project_name, client_name)
        if project_id is None: # Project might not exist under that client, or name is wrong
             return False, f"Project '{project_name}' not found for client '{client_name}'. Please check selection."

        from sqlalchemy import text
        dal = dbc_instance.dal
        engine = dal.dev_conn._engine
        # Check if asset name exists for this project_id
        query_check = text("""
            SELECT 1 FROM tbl_asset a
            JOIN tbl_project_asset pa ON a.AssetID = pa.AssetID
            WHERE a.Name = :asset_name AND pa.ProjectID = :project_id
        """)
        with engine.connect() as connection:
            result = connection.execute(query_check, {"asset_name": asset_name, "project_id": project_id}).fetchone()
            if result:
                return False, f"Asset '{asset_name}' already exists in project '{project_name}'. Please use a different name."
    except Exception as e:
        print(f"Error checking asset uniqueness: {e}")
        return False, "An error occurred while validating asset name. Please try again."

    # If all checks pass
    validated_data = {
        "client_name": client_name,
        "project_name": project_name,
        "asset_type_id": asset_type_id,
        "asset_name": asset_name.strip()
    }
    return True, validated_data
