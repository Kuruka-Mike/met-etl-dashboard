"""
Modern Add Client Modal for Dash Mantine Dashboard

- Mantine-based modal UI for adding a new client
- All callback logic for open/close, submit, notification, and reset
- Designed for clean integration into the dashboard
"""

import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State
import pandas as pd
from DBcontroller import DBcontoller

dbc_instance = DBcontoller()

def create_add_client_modal():
    """Mantine-styled modal for adding a new client"""
    return dmc.Modal(
        title="Add New Client",
        id="modern-add-client-modal",
        size="md",
        centered=True,
        overlayProps={"background_color": "rgba(0, 0, 0, 0.55)", "blur": 3},
        children=[
            dmc.Stack(
                gap="md",
                children=[
                    dmc.TextInput(
                        label="Client Name",
                        placeholder="Enter client name (e.g., WindTech Solutions)",
                        id="modern-client-name-input",
                        required=True,
                        style={"width": "100%"}
                    ),
                    dmc.Group(
                        justify="flex-end",
                        mt="md",
                        children=[
                            dmc.Button(
                                "Cancel",
                                id="modern-cancel-client-btn",
                                variant="outline",
                                color="gray"
                            ),
                            dmc.Button(
                                "Add Client",
                                id="modern-add-client-btn",
                                color="blue"
                            )
                        ]
                    )
                ]
            ),
            dcc.Store(id="add-client-notification-store"),
        ]
    )

# Callback to handle modal open/close
@callback(
    Output("add-client-notification-store", "data", allow_duplicate=True),
    Input("add-client-notification-store", "data"),
    prevent_initial_call=True
)
def clientside_show_notification(notification):
    # This is a placeholder for a clientside callback in assets/ that will call window.dash_mantine_components.showNotification
    return notification

# Callback to handle modal open/close
@callback(
    Output("modern-add-client-modal", "opened"),
    [Input("open-modern-add-client-btn", "n_clicks"),
     Input("modern-cancel-client-btn", "n_clicks"),
     Input("modern-add-client-btn", "n_clicks")],
    [State("modern-add-client-modal", "opened")],
    prevent_initial_call=True
)
def toggle_add_client_modal(open_sidebar, cancel, add, is_open):
    from dash import ctx
    if ctx.triggered_id == "open-modern-add-client-btn":
        return True
    elif ctx.triggered_id in ["modern-cancel-client-btn", "modern-add-client-btn"]:
        return False
    return is_open

# Callback to handle adding a new client
@callback(
    [Output("modern-client-name-input", "value"),
     Output("add-client-notification-store", "data"),
     Output("notification-log-store", "data", allow_duplicate=True),
     Output("clients-refresh-trigger", "data")],
    [Input("modern-add-client-btn", "n_clicks")],
    [State("modern-client-name-input", "value"),
     State("add-client-notification-store", "data"),
     State("notification-log-store", "data"),
     State("clients-refresh-trigger", "data")],
    prevent_initial_call=True
)
def add_new_client(n_clicks, client_name, toast_data, log_data, current_trigger):
    if not n_clicks or not client_name:
        return "", {}, log_data or [], current_trigger
    try:
        dbc_instance.addClient(client_name, "1")
        notification = {
            "id": f"success-{pd.Timestamp.now().timestamp()}",
            "title": "Success!",
            "message": f"Client '{client_name}' has been added successfully.",
            "color": "green",
            "icon": "✅"
        }
        log = (log_data or []) + [{
            "type": "success",
            "message": f"Client '{client_name}' was added successfully.",
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }]
        return "", notification, log, current_trigger + 1
    except ValueError as e:
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
        return client_name, notification, log, current_trigger
    except Exception as e:
        notification = {
            "id": f"error-{pd.Timestamp.now().timestamp()}",
            "title": "Error",
            "message": f"Failed to add client: {str(e)}",
            "color": "red",
            "icon": "❌"
        }
        log = (log_data or []) + [{
            "type": "error",
            "message": f"Failed to add client: {str(e)}",
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }]
        return client_name, notification, log, current_trigger
