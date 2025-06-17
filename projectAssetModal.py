"""
Project Asset Modal for Dash Mantine Dashboard

- Mantine-based modal UI for adding project asset details
- All callback logic for open/close, submit, notification, and reset
- Designed for clean integration into the assets dashboard
"""

import dash
import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State, no_update
import pandas as pd
from DBcontroller import DBcontoller

dbc_instance = DBcontoller()

def create_project_asset_modal():
    """Mantine-styled modal for pairing Lidar/Sodar with Met Tower"""
    return dmc.Modal(
        title="Asset Pairing",
        id="project-asset-modal",
        size="md",
        centered=True,
        overlayProps={"background_color": "rgba(0, 0, 0, 0.55)", "blur": 3},
        children=[
            dmc.Stack(
                gap="md",
                children=[
                    # Step indicator
                    dmc.Group(
                        justify="center",
                        mb="md",
                        children=[
                            dmc.Badge("Step 2 of 4", color="blue", size="lg")
                        ]
                    ),
                    
                    # Dynamic message based on asset type
                    dmc.Text(
                        "You've added a Lidar/Sodar asset. Would you like to pair it with a Met Tower or keep it as standalone?",
                        id="pairing-message",
                        size="md",
                        mb="md"
                    ),
                    
                    # Pairing dropdown
                    dmc.Select(
                        label="Select Pairing Option",
                        id="pair-project-asset-dropdown",
                        placeholder="Select a Met Tower or Standalone",
                        data=[],  # Will be populated based on project
                        style={"width": "100%"}
                    ),
                    
                    # Hidden inputs to store data
                    html.Div(
                        style={"display": "none"},
                        children=[
                            dmc.TextInput(id="project-asset-id-input"),
                            dmc.TextInput(id="project-id-input"),
                            dmc.TextInput(id="project-dropdown"),
                            dmc.TextInput(id="asset-name-details-input"),
                            dmc.TextInput(id="asset-type-id-input"),
                            dmc.TextInput(id="asset-id-input"),
                        ]
                    ),
                    
                    # Action buttons
                    dmc.Group(
                        justify="flex-end",
                        mt="md",
                        children=[
                            dmc.Button(
                                "Back",
                                id="back-to-asset-btn",
                                variant="outline",
                                color="gray"
                            ),
                            dmc.Button(
                                "Save",
                                id="save-project-asset-btn",
                                color="blue"
                            ),
                            dmc.Button(
                                "Next",
                                id="next-to-coordinates-btn",
                                color="green",
                                disabled=True
                            )
                        ]
                    )
                ]
            ),
            dcc.Store(id="project-asset-notification-store"),
        ]
    )

# Callback to update the pairing message based on asset type
@callback(
    Output("pairing-message", "children"),
    Input("asset-type-id-input", "value")
)
def update_pairing_message(asset_type_id):
    if asset_type_id == "2":
        return "You've added a Lidar asset. Would you like to pair it with a Met Tower or keep it as standalone?"
    elif asset_type_id == "3":
        return "You've added a Sodar asset. Would you like to pair it with a Met Tower or keep it as standalone?"
    return "Would you like to pair this asset with a Met Tower or keep it as standalone?"

# Callback to update paired assets dropdown based on project selection
@callback(
    Output("pair-project-asset-dropdown", "data"),
    [Input("project-dropdown", "value"),
     Input("asset-type-id-input", "value")]
)
def update_paired_assets_dropdown(project_name, asset_type_id):
    if not project_name or asset_type_id not in ["2", "3"]:  # Only for Lidar or Sodar
        return []
    
    try:
        # Add a "Standalone" option
        standalone_option = [{"label": "Standalone (No Pairing)", "value": "standalone"}]
        
        # Get Met Towers for this project (assuming asset type 1 is Met Tower)
        met_towers = dbc_instance.getMetTowersByProjectName(project_name)
        
        # Ensure all values are strings (Mantine requires string values)
        if met_towers:
            for tower in met_towers:
                if 'value' in tower and tower['value'] is not None:
                    tower['value'] = str(tower['value'])
        
        # Combine standalone option with met towers
        return standalone_option + (met_towers or [])
    except Exception as e:
        print(f"Error updating paired assets dropdown: {e}")
        return [{"label": "Standalone (No Pairing)", "value": "standalone"}]

# Callback to handle modal open/close
@callback(
    Output("project-asset-modal", "opened"),
    [Input("next-to-project-asset-btn", "n_clicks"),
     Input("back-to-asset-btn", "n_clicks"),
     Input("next-to-coordinates-btn", "n_clicks")],
    [State("project-asset-modal", "opened")],
    prevent_initial_call=True
)
def toggle_project_asset_modal(next_clicks, back_clicks, next_to_coord_clicks, is_open):
    from dash import ctx
    if ctx.triggered_id == "next-to-project-asset-btn":
        return True
    elif ctx.triggered_id in ["back-to-asset-btn", "next-to-coordinates-btn"]:
        return False
    return is_open

# Callback to load project asset data when the modal is opened
@callback(
    [Output("project-asset-id-input", "value", allow_duplicate=True),
     Output("project-id-input", "value", allow_duplicate=True),
     Output("project-dropdown", "value", allow_duplicate=True),
     Output("asset-name-details-input", "value", allow_duplicate=True),
     Output("asset-type-id-input", "value", allow_duplicate=True),
     Output("asset-id-input", "value", allow_duplicate=True)],
    [Input("project-asset-modal", "opened")],
    [State("current-project-asset-id-store", "data")],
    prevent_initial_call=True
)
def load_project_asset_data(is_open, project_asset_id):
    if not is_open or project_asset_id is None:
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    try:
        # Fetch the project asset data from the database
        project_asset_data = get_project_asset_data(project_asset_id)
        
        if project_asset_data:
            return (
                str(project_asset_data.get("ProjectAssetID", "")),
                str(project_asset_data.get("ProjectID", "")),
                project_asset_data.get("ProjectName", ""),
                project_asset_data.get("AssetName", ""),
                str(project_asset_data.get("AssetTypeID", "")),
                str(project_asset_data.get("AssetID", ""))
            )
        
        return no_update, no_update, no_update, no_update, no_update, no_update
    
    except Exception as e:
        print(f"Error loading project asset data: {e}")
        return no_update, no_update, no_update, no_update, no_update, no_update

def get_project_asset_data(project_asset_id):
    """
    Fetch project asset data from the database using the ProjectAssetID.
    """
    if project_asset_id is None:
        return None
    
    try:
        # Query to get the project asset record
        query = f"""
            SELECT 
                pa.ProjectAssetID, 
                pa.ProjectID, 
                p.Name as ProjectName,
                pa.Name as AssetName, 
                pa.AssetTypeID, 
                pa.AssetID,
                pa.PairProjectAssetID
            FROM tbl_project_asset pa
            JOIN tbl_project p ON pa.ProjectID = p.ProjectID
            WHERE pa.ProjectAssetID = {project_asset_id}
        """
        
        # Execute the query
        result = dbc_instance.dal.cnn.execute(query).fetchone()
        
        if result:
            # Convert the result to a dictionary
            project_asset_data = {
                "ProjectAssetID": result.ProjectAssetID,
                "ProjectID": result.ProjectID,
                "ProjectName": result.ProjectName,
                "AssetName": result.AssetName,
                "AssetTypeID": result.AssetTypeID,
                "AssetID": result.AssetID,
                "PairProjectAssetID": result.PairProjectAssetID
            }
            return project_asset_data
        return None
    except Exception as e:
        print(f"Error fetching project asset data: {e}")
        return None

# Callback to handle saving project asset details
@callback(
    [Output("project-asset-id-input", "value", allow_duplicate=True),
     Output("project-id-input", "value", allow_duplicate=True),
     Output("project-dropdown", "value", allow_duplicate=True),
     Output("asset-name-details-input", "value", allow_duplicate=True),
     Output("asset-type-id-input", "value", allow_duplicate=True),
     Output("asset-id-input", "value", allow_duplicate=True),
     Output("pair-project-asset-dropdown", "value", allow_duplicate=True),
     Output("project-asset-notification-store", "data", allow_duplicate=True),
     Output("assets-dashboard-refresh-trigger-new", "data", allow_duplicate=True),
     Output("save-project-asset-btn", "disabled", allow_duplicate=True),
     Output("next-to-coordinates-btn", "disabled", allow_duplicate=True)],
    [Input("save-project-asset-btn", "n_clicks")],
    [State("project-asset-id-input", "value"),
     State("project-id-input", "value"),
     State("project-dropdown", "value"),
     State("asset-name-details-input", "value"),
     State("asset-type-id-input", "value"),
     State("asset-id-input", "value"),
     State("pair-project-asset-dropdown", "value"),
     State("assets-dashboard-refresh-trigger-new", "data")],
    prevent_initial_call=True
)
def save_project_asset_details(
    n_clicks, 
    project_asset_id, 
    project_id, 
    project_name, 
    asset_name, 
    asset_type_id, 
    asset_id, 
    pair_project_asset_id, 
    refresh_trigger
):
    if not n_clicks or not project_asset_id:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, refresh_trigger
    
    try:
        # Convert project_asset_id to integer
        project_asset_id = int(project_asset_id)
        
        # If the user selected a paired asset (not "standalone"), update the PairProjectAssetID
        if pair_project_asset_id and pair_project_asset_id != "standalone":
            # Convert pair_project_asset_id to integer if it's a string
            pair_id = int(pair_project_asset_id)
            
            print(f"DEBUG: Pairing asset {project_asset_id} with Met Tower {pair_id}")
            
            # Update the PairProjectAssetID in the database
            update_query = f"""
                UPDATE tbl_project_asset
                SET PairProjectAssetID = {pair_id}
                WHERE ProjectAssetID = {project_asset_id}
            """
            
            print(f"DEBUG: Executing query: {update_query}")
            
            # Execute the query using a transaction context manager
            with dbc_instance.dal.cnn.begin() as transaction:
                dbc_instance.dal.cnn.execute(update_query)
                print(f"DEBUG: Transaction committed")
            
            print(f"DEBUG: Asset paired successfully")
            
            message = f"Asset paired successfully with ProjectAssetID {pair_project_asset_id}."
        else:
            # If "standalone" was selected, set PairProjectAssetID to NULL
            update_query = f"""
                UPDATE tbl_project_asset
                SET PairProjectAssetID = NULL
                WHERE ProjectAssetID = {project_asset_id}
            """
            
            print(f"DEBUG: Setting asset {project_asset_id} as standalone")
            
            # Execute the query using a transaction context manager
            with dbc_instance.dal.cnn.begin() as transaction:
                dbc_instance.dal.cnn.execute(update_query)
                print(f"DEBUG: Transaction committed")
            
            print(f"DEBUG: Asset set as standalone successfully")
            
            message = "Asset set as standalone (no pairing)."
        
        notification = {
            "id": f"success-{pd.Timestamp.now().timestamp()}",
            "title": "Success!",
            "message": message,
            "color": "green",
            "icon": "✅"
        }
        
        # Clear all fields and update button states
        return "", "", "", "", "", "", "", notification, (refresh_trigger or 0) + 1, True, False
    
    except Exception as e:
        print(f"Error saving project asset details: {e}")
        notification = {
            "id": f"error-{pd.Timestamp.now().timestamp()}",
            "title": "Error",
            "message": f"Failed to save project asset details: {str(e)}",
            "color": "red",
            "icon": "❌"
        }
        
        # Keep the entered values and button states
        return project_asset_id, project_id, project_name, asset_name, asset_type_id, asset_id, pair_project_asset_id, notification, refresh_trigger, False, True

# Callback to show notifications
@callback(
    Output("project-asset-notification-store", "data", allow_duplicate=True),
    Input("project-asset-notification-store", "data"),
    prevent_initial_call=True
)
def clientside_show_project_asset_notification(notification):
    if notification:
        return notification
    return no_update

# Callback to open coordinates modal when Next button is clicked
@callback(
    [Output("project-asset-detail-modal", "opened", allow_duplicate=True),
     Output("project-asset-modal", "opened", allow_duplicate=True)],
    Input("next-to-coordinates-btn", "n_clicks"),
    prevent_initial_call=True
)
def open_coordinates_modal(n_clicks):
    if n_clicks:
        # Close the pairing modal and open the coordinates modal
        return True, False
    return no_update, no_update
