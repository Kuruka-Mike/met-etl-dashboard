"""
Modern Add Asset Modal for Dash Mantine Dashboard

- Mantine-based modal UI for adding a new asset
- All callback logic for open/close, submit, notification, and reset
- Designed for clean integration into the assets dashboard
"""

import dash
import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State, no_update
import pandas as pd
from DBcontroller import DBcontoller
from projectAssetModal import create_project_asset_modal

dbc_instance = DBcontoller()

def create_add_asset_modal():
    """Mantine-styled modal for adding a new asset"""
    return dmc.Modal(
        title="Add New Asset - Step 1",
        id="add-asset-modal",
        size="md",
        centered=True,
        overlayProps={"background_color": "rgba(0, 0, 0, 0.55)", "blur": 3},
        children=[
            dmc.Stack(
                gap="md",
                children=[
                    # Client dropdown
                    dmc.Select(
                        label="Client",
                        id="asset-client-dropdown",
                        placeholder="Select a client",
                        data=[{"label": c, "value": c} for c in dbc_instance.getAllClients()],
                        required=True,
                        style={"width": "100%"}
                    ),
                    
                    # Project dropdown (will be populated based on client selection)
                    dmc.Select(
                        label="Project",
                        id="asset-project-dropdown",
                        placeholder="Select a project",
                        data=[],  # Empty initially, populated by callback
                        required=True,
                        style={"width": "100%"}
                    ),
                    
                    # Asset type dropdown
                    dmc.Select(
                        label="Asset Type",
                        id="asset-type-dropdown",
                        placeholder="Select asset type",
                        data=[
                            {"label": "Development Met Tower", "value": "1"},
                            {"label": "Lidar", "value": "2"},
                            {"label": "Sodar", "value": "3"}
                        ],
                        required=True,
                        style={"width": "100%"}
                    ),
                    
                    # Asset name input
                    dmc.TextInput(
                        label="Asset Name",
                        placeholder="Enter asset name",
                        id="asset-name-input",
                        required=True,
                        style={"width": "100%"}
                    ),
                    
                    # Step indicator
                    dmc.Group(
                        justify="center",
                        mb="md",
                        children=[
                            dmc.Badge("Step 1 of 4", color="blue", size="lg")
                        ]
                    ),
                    
                    # Action buttons
                    dmc.Group(
                        justify="flex-end",
                        mt="md",
                        children=[
                            dmc.Button(
                                "Cancel",
                                id="cancel-asset-btn",
                                variant="outline",
                                color="gray"
                            ),
                            dmc.Button(
                                "Add Asset",
                                id="add-asset-submit-btn",
                                color="blue"
                            ),
                            dmc.Button(
                                "Next",
                                id="next-to-project-asset-btn",
                                color="green",
                                disabled=True
                            )
                        ]
                    )
                ]
            ),
            dcc.Store(id="add-asset-notification-store"),
        ]
    )

# Callback to update project dropdown based on client selection
@callback(
    Output("asset-project-dropdown", "data"),
    Input("asset-client-dropdown", "value")
)
def update_project_dropdown(client_name):
    if not client_name:
        return []
    
    try:
        # Get client ID
        client_id = dbc_instance.getClientID(client_name)
        # Get projects for this client
        projects = dbc_instance.getProjects(client_id)
        # Format for dropdown
        return [{"label": project, "value": project} for project in projects]
    except Exception as e:
        print(f"Error updating project dropdown: {e}")
        return []

# Callback to handle modal open/close
@callback(
    Output("add-asset-modal", "opened"),
    [Input("add-asset-btn-v2", "n_clicks"),
     Input("cancel-asset-btn", "n_clicks"),
     Input("back-to-asset-btn", "n_clicks"),
     Input("next-to-project-asset-btn", "n_clicks")],
    [State("add-asset-modal", "opened")],
    prevent_initial_call=True
)
def toggle_add_asset_modal(open_clicks, cancel_clicks, back_clicks, next_clicks, is_open):
    from dash import ctx
    if ctx.triggered_id == "add-asset-btn-v2":
        return True
    elif ctx.triggered_id == "back-to-asset-btn":
        return True
    elif ctx.triggered_id in ["cancel-asset-btn", "next-to-project-asset-btn"]:
        return False
    return is_open

# Callback to handle adding a new asset
@callback(
    [Output("asset-name-input", "value"),
     Output("asset-client-dropdown", "value"),
     Output("asset-project-dropdown", "value"),
     Output("asset-type-dropdown", "value"),
     Output("add-asset-notification-store", "data"),
     Output("assets-dashboard-refresh-trigger-new", "data"),
     Output("notification-log-store", "data", allow_duplicate=True),
     Output("add-asset-submit-btn", "disabled"),
     Output("next-to-project-asset-btn", "disabled"),
     Output("current-project-asset-id-store", "data")],
    [Input("add-asset-submit-btn", "n_clicks")],
    [State("asset-client-dropdown", "value"),
     State("asset-project-dropdown", "value"),
     State("asset-type-dropdown", "value"),
     State("asset-name-input", "value"),
     State("assets-dashboard-refresh-trigger-new", "data"),
     State("notification-log-store", "data")],
    prevent_initial_call=True
)
def add_new_asset(n_clicks, client_name, project_name, asset_type_id, asset_name, refresh_trigger, log_data):
    if not n_clicks or not client_name or not project_name or not asset_type_id or not asset_name:
        return no_update, no_update, no_update, no_update, no_update, refresh_trigger, log_data or [], no_update, no_update, no_update
    
    try:
        print(f"Adding asset '{asset_name}' to project '{project_name}' with type ID {asset_type_id}...")
        
        # Insert directly into tbl_asset table
        new_asset_id = dbc_instance.addSimpleAsset(asset_name, int(asset_type_id))
        
        # Get project ID from project name and client name
        project_id = dbc_instance.getProjectIdByName(project_name, client_name)
        
        if project_id is None:
            raise ValueError(f"Could not find project ID for project '{project_name}' under client '{client_name}'")
        
        # Link the asset to the project in tbl_project_asset
        project_asset_id = dbc_instance.addProjectAsset(
            project_id=project_id,
            asset_name=asset_name,
            asset_type_id=int(asset_type_id),
            asset_id=new_asset_id
        )
        
        print(f"Asset added successfully. Asset ID: {new_asset_id}, Project Asset ID: {project_asset_id}")
        
        notification = {
            "id": f"success-{pd.Timestamp.now().timestamp()}",
            "title": "Success!",
            "message": f"Asset '{asset_name}' was added to project '{project_name}'.",
            "color": "green",
            "icon": "✅"
        }
        
        log = (log_data or []) + [{
            "type": "success",
            "message": f"Asset '{asset_name}' was added to project '{project_name}'.",
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }]
        
        # Disable the Add Asset button and enable the Next button
        # Also store the project_asset_id for the second modal
        return asset_name, client_name, project_name, asset_type_id, notification, (refresh_trigger or 0) + 1, log, True, False, project_asset_id
    
    except ValueError as e:
        print(f"ValueError adding asset: {e}")
        notification = {
            "id": f"warning-{pd.Timestamp.now().timestamp()}",
            "title": "Warning",
            "message": str(e),
            "color": "yellow",
            "icon": "⚠️"
        }
        
        log = (log_data or []) + [{
            "type": "warning",
            "message": str(e),
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }]
        
        return asset_name, client_name, project_name, asset_type_id, notification, refresh_trigger, log, False, True, None
    
    except Exception as e:
        print(f"Exception adding asset: {e}")
        notification = {
            "id": f"error-{pd.Timestamp.now().timestamp()}",
            "title": "Error",
            "message": f"Failed to add asset: {str(e)}",
            "color": "red",
            "icon": "❌"
        }
        
        log = (log_data or []) + [{
            "type": "error",
            "message": f"Failed to add asset: {str(e)}",
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }]
        
        return asset_name, client_name, project_name, asset_type_id, notification, refresh_trigger, log, False, True, None

# Callback to show notifications
@callback(
    Output("add-asset-notification-store", "data", allow_duplicate=True),
    Input("add-asset-notification-store", "data"),
    prevent_initial_call=True
)
def clientside_show_asset_notification(notification):
    if notification:
        return notification
    return no_update

# Reset form when modal is opened
@callback(
    [Output("asset-name-input", "value", allow_duplicate=True),
     Output("asset-client-dropdown", "value", allow_duplicate=True),
     Output("asset-project-dropdown", "value", allow_duplicate=True),
     Output("asset-type-dropdown", "value", allow_duplicate=True),
     Output("add-asset-submit-btn", "disabled", allow_duplicate=True),
     Output("next-to-project-asset-btn", "disabled", allow_duplicate=True)],
    [Input("add-asset-btn-v2", "n_clicks")],
    prevent_initial_call=True
)
def reset_form_on_open(n_clicks):
    return "", None, None, None, False, True

# Include the project asset modal
create_project_asset_modal()

# Callback to handle next button click - skip Step 2 for Met Towers
@callback(
    [Output("project-asset-modal", "opened", allow_duplicate=True),
     Output("project-asset-detail-modal", "opened", allow_duplicate=True)],
    [Input("next-to-project-asset-btn", "n_clicks")],
    [State("asset-type-dropdown", "value"),
     State("current-project-asset-id-store", "data")],
    prevent_initial_call=True
)
def handle_next_button_click(n_clicks, asset_type_id, project_asset_id):
    if not n_clicks or not project_asset_id:
        return no_update, no_update
    
    # For Met Towers (type 1), skip Step 2 and go directly to Step 3
    if asset_type_id == "1":
        return False, True
    
    # For Lidar/Sodar (type 2/3), go to Step 2 for pairing
    return True, False
