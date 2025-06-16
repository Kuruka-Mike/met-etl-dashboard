"""
Step 2: Project Asset Configuration (Modular)
- Project selection (editable, defaults to Step 1)
- Conditional "Pair with Met Tower" dropdown (only for Lidar/Sodar)
- Display created asset information
"""

import dash_mantine_components as dmc
from dash import html, callback, Output, Input, State
from DBcontroller import DBcontoller

dbc_instance = DBcontoller()

def create_step2_layout():
    """Create the layout for Step 2: Project Configuration"""
    return dmc.Stack(
        gap="md",
        children=[
            dmc.Alert(
                "Base asset record created! Now configure its project-specific details.", # Updated message
                title="Step 1 Complete!",
                color="green",
                id="step2-success-alert-new", # ID Updated
                hide=True, # Initially hidden, shown by callback
                withCloseButton=True
                # children="" # Removed redundant children prop
            ),
            dmc.SimpleGrid(
                cols=2,
                spacing="md",
                children=[
                    dmc.TextInput( # Added for Client Name display
                        label="Client",
                        id="step2-client-name-display-new", # New ID
                        disabled=True,
                        style={"width": "100%"}
                    ),
                    dmc.Select( # Project might still be selectable/confirmable here
                        label="Project",
                        id="step2-project-dropdown-new", # ID Updated
                        placeholder="Confirm or select project",
                        data=[], # To be populated by callback based on Step 1 client
                        required=True,
                        style={"width": "100%"}
                    ),
                    dmc.TextInput(
                        label="Asset Name",
                        id="step2-asset-name-display-new", # ID Updated
                        disabled=True,
                        style={"width": "100%"}
                    ),
                    dmc.TextInput(
                        label="Asset Type",
                        id="step2-asset-type-display-new", # ID Updated
                        disabled=True,
                        style={"width": "100%"}
                    ),
                    dmc.TextInput(
                        label="Asset ID (from tbl_asset)",
                        id="step2-asset-id-display-new", # ID Updated
                        disabled=True,
                        style={"width": "100%"}
                    )
                ]
            ),
            html.Div(
                id="met-tower-pairing-section-new", # ID Updated
                style={"display": "none"}, # Conditional visibility handled by callback
                children=[
                    dmc.Select(
                        label="Pair with Met Tower (Optional, if Lidar/Sodar)",
                        id="step2-met-tower-dropdown-new", # ID Updated
                        placeholder="Select a Met Tower to pair with",
                        data=[], # To be populated by callback
                        clearable=True,
                        style={"width": "100%"}
                    )
                ]
            ),
            dmc.Alert(
                id="step2-alert-message-new", # New alert for Step 2 errors
                title="Input Error!",
                color="red",
                hide=True,
                withCloseButton=True,
                children="",
                mt="md"
            )
        ]
    )

def validate_step2_data(project_name, asset_info):
    if not project_name:
        return False, "Project selection is required."
    if not asset_info:
        return False, "Asset information is missing. Please restart the process."
    return True, "Valid"

def process_step2_to_step3(project_name, met_tower_pair_id, asset_info):
    try:
        client_name = asset_info.get("client_name")
        asset_name = asset_info.get("asset_name")
        asset_type_id = asset_info.get("asset_type_id")
        asset_id = asset_info.get("asset_id")
        
        print(f"DEBUG: process_step2_to_step3 called with project_name='{project_name}', asset_id={asset_id}")
        
        project_id = dbc_instance.getProjectIdByName(project_name, client_name)
        if not project_id:
            raise ValueError(f"Could not find ProjectID for project '{project_name}'")
        
        # Convert met_tower_pair_id from "standalone" to None if needed
        if met_tower_pair_id == "standalone":
            pair_project_asset_id = None
        else:
            pair_project_asset_id = met_tower_pair_id if met_tower_pair_id else None
        
        # Use the DataAccessLayer method directly to create project asset
        new_project_asset_id = dbc_instance.addProjectAsset(
            project_id=project_id,
            asset_name=asset_name,
            asset_type_id=asset_type_id,
            asset_id=asset_id,
            pair_project_asset_id=pair_project_asset_id
        )
        return new_project_asset_id, None
    except Exception as e:
        error_msg = f"Failed to create project asset: {str(e)}"
        print(f"DEBUG: Error in process_step2_to_step3: {error_msg}")
        return None, error_msg
