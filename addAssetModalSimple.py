"""
Simple Add Asset Modal - Fallback version for testing
"""

import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State, ctx
import pandas as pd
from DBcontroller import DBcontoller

dbc_instance = DBcontoller()

def create_add_asset_modal():
    """Simple asset modal for testing"""
    return dmc.Modal(
        title="Add New Asset",
        id="modern-add-asset-modal",
        size="md",
        centered=True,
        overlayBlur=2,
        opened=False,
        closeOnClickOutside=False,
        closeOnEscape=False,
        children=[
            dmc.Stack(
                spacing="md",
                children=[
                    dmc.Select(
                        label="Client",
                        id="modern-asset-client-dropdown",
                        placeholder="Select a client",
                        data=[],
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
                    dmc.Group(
                        position="right",
                        mt="md",
                        children=[
                            dmc.Button(
                                "Cancel",
                                id="modern-cancel-asset-btn",
                                variant="outline",
                                color="gray"
                            ),
                            dmc.Button(
                                "Add Asset",
                                id="modern-add-asset-btn",
                                color="blue"
                            )
                        ]
                    )
                ]
            ),
            dcc.Store(id="add-asset-notification-store"),
        ]
    )

# Load client data when modal opens
@callback(
    Output("modern-asset-client-dropdown", "data"),
    Input("modern-add-asset-modal", "opened"),
    prevent_initial_call=True
)
def load_client_data_on_modal_open(is_opened):
    if is_opened:
        try:
            clients = dbc_instance.getAllClients()
            return [{"label": c, "value": c} for c in clients]
        except Exception as e:
            print(f"Error loading client data: {e}")
            return []
    return []

# Update project dropdown
@callback(
    Output("modern-asset-project-dropdown", "data"),
    Input("modern-asset-client-dropdown", "value"),
    prevent_initial_call=True,
)
def update_project_dropdown(client_name):
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
        print(f"Error updating project dropdown: {e}")
        return []

# Modal control
@callback(
    Output("modern-add-asset-modal", "opened"),
    [
        Input("quick-add-asset-btn", "n_clicks"),
        Input("modern-cancel-asset-btn", "n_clicks"),
        Input("modern-add-asset-btn", "n_clicks")
    ],
    State("modern-add-asset-modal", "opened"),
    prevent_initial_call=True
)
def toggle_add_asset_modal(open_btn, cancel_btn, add_btn, is_open):
    if ctx.triggered_id == "quick-add-asset-btn" and open_btn and open_btn > 0:
        return True
    elif ctx.triggered_id in ["modern-cancel-asset-btn", "modern-add-asset-btn"]:
        return False
    return is_open

# Add asset
@callback(
    [
        Output("modern-asset-name-input", "value"),
        Output("modern-asset-client-dropdown", "value", allow_duplicate=True),
        Output("modern-asset-project-dropdown", "value", allow_duplicate=True),
        Output("modern-asset-type-dropdown", "value", allow_duplicate=True),
        Output("add-asset-notification-store", "data", allow_duplicate=True),
        Output("assets-dashboard-refresh-trigger", "data", allow_duplicate=True),
        Output("notification-log-store", "data", allow_duplicate=True),
        Output("modern-add-asset-modal", "opened", allow_duplicate=True)
    ],
    Input("modern-add-asset-btn", "n_clicks"),
    State("modern-asset-client-dropdown", "value"),
    State("modern-asset-project-dropdown", "value"),
    State("modern-asset-type-dropdown", "value"),
    State("modern-asset-name-input", "value"),
    State("assets-dashboard-refresh-trigger", "data"),
    State("notification-log-store", "data"),
    prevent_initial_call=True
)
def add_new_asset(n_clicks, client_name, project_name, asset_type_id, asset_name, refresh_trigger, log_data):
    if not n_clicks or not client_name or not project_name or not asset_type_id or not asset_name:
        notification = {
            "title": "Warning",
            "message": "All fields are required.",
            "color": "yellow",
            "icon": "⚠️"
        }
        return (
            asset_name, client_name, project_name, asset_type_id,
            notification, refresh_trigger, log_data or [], True
        )
    try:
        # Simple asset creation for testing
        new_asset_id = dbc_instance.addSimpleAsset(asset_name, int(asset_type_id))
        
        notification = {
            "title": "Success!",
            "message": f"Asset '{asset_name}' was created with ID {new_asset_id}.",
            "color": "green",
            "icon": "✅"
        }
        log = (log_data or []) + [{
            "type": "success",
            "message": f"Asset '{asset_name}' was created with ID {new_asset_id}.",
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }]
        return (
            "", "", "", "",
            notification, (refresh_trigger or 0) + 1, log, False
        )
    except Exception as e:
        notification = {
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
        return (
            asset_name, client_name, project_name, asset_type_id,
            notification, refresh_trigger, log, True
        )
