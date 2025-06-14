"""
Modern Add Project Modal for Dash Mantine Dashboard

- Mantine-based modal UI for adding a new project
- All callback logic for open/close, submit, notification, and reset
- Designed for clean integration into the projects dashboard
"""

import dash
import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State, ALL
import pandas as pd
from DBcontroller import DBcontoller

dbc_instance = DBcontoller()

def create_add_project_modal():
    """Mantine-styled modal for adding a new project"""
    return dmc.Modal(
        title="Add New Project",
        id="modern-add-project-modal",
        size="md",
        centered=True,
        overlayBlur=2,
        children=[
            dmc.Stack(
                spacing="md",
                children=[
                    dmc.Select(
                        label="Client",
                        id="modern-project-client-dropdown",
                        placeholder="Select a client",
                        data=[{"label": c, "value": c} for c in dbc_instance.getAllClients()],
                        required=True,
                        style={"width": "100%"}
                    ),
                    dmc.TextInput(
                        label="Project Name",
                        placeholder="Enter project name",
                        id="modern-project-name-input",
                        required=True,
                        style={"width": "100%"}
                    ),
                    dmc.Group(
                        position="right",
                        mt="md",
                        children=[
                            dmc.Button(
                                "Cancel",
                                id="modern-cancel-project-btn",
                                variant="outline",
                                color="gray"
                            ),
                            dmc.Button(
                                "Add Project",
                                id="modern-add-project-btn",
                                color="blue"
                            )
                        ]
                    )
                ]
            ),
            dcc.Store(id="add-project-notification-store"),
        ]
    )

@callback(
    Output("add-project-notification-store", "data", allow_duplicate=True),
    Input("add-project-notification-store", "data"),
    prevent_initial_call=True
)
def clientside_show_project_notification(notification):
    if notification:
        return notification
    return dash.no_update

@callback(
    Output("modern-add-project-modal", "opened"),
    [Input("quick-add-project-btn", "n_clicks"),
     Input({"type": "add-project-to-client-btn", "client": ALL}, "n_clicks")],
    [State("modern-add-project-modal", "opened")],
    prevent_initial_call=True,
)
def open_project_modal(quick_clicks, client_clicks, is_open):
    from dash import ctx
    if any(c is not None and c > 0 for c in client_clicks) or (quick_clicks is not None and quick_clicks > 0):
        return True
    return is_open

@callback(
    Output("modern-add-project-modal", "opened", allow_duplicate=True),
    [Input("modern-cancel-project-btn", "n_clicks"),
     Input("modern-add-project-btn", "n_clicks")],
    prevent_initial_call=True,
)
def close_project_modal(cancel_clicks, add_clicks):
    return False

@callback(
    Output("modern-project-client-dropdown", "value"),
    Input({"type": "add-project-to-client-btn", "client": ALL}, "n_clicks"),
    prevent_initial_call=True
)
def preselect_client_from_card(n_clicks):
    from dash import ctx, no_update
    if not any(n_clicks):
        return no_update
    
    triggered_id = ctx.triggered_id
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "add-project-to-client-btn":
        return triggered_id["client"]
    
    return no_update

@callback(
    [Output("modern-project-name-input", "value"),
     Output("modern-project-client-dropdown", "value", allow_duplicate=True),
     Output("add-project-notification-store", "data", allow_duplicate=True),
     Output("projects-dashboard-refresh-trigger", "data"),
     Output("notification-log-store", "data", allow_duplicate=True)],
    [Input("modern-add-project-btn", "n_clicks")],
    [State("modern-project-client-dropdown", "value"),
     State("modern-project-name-input", "value"),
     State("projects-dashboard-refresh-trigger", "data"),
     State("notification-log-store", "data")],
    prevent_initial_call=True
)
def add_new_project(n_clicks, client_name, project_name, refresh_trigger, log_data):
        if not n_clicks or not client_name or not project_name:
            return "", "", dash.no_update, refresh_trigger, log_data or []
        try:
            print(f"Adding project '{project_name}' to client '{client_name}'...")
            dbc_instance.addProject(project_name, client_name)
            print("Project added successfully.")
            notification = {
                "title": "Success!",
                "message": f"Project '{project_name}' was added to '{client_name}'.",
                "color": "green",
                "icon": "✅"
            }
            log = (log_data or []) + [{
                "type": "success",
                "message": f"Project '{project_name}' was added to '{client_name}'.",
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }]
            return "", "", notification, (refresh_trigger or 0) + 1, log
        except ValueError as e:
            print(f"ValueError adding project: {e}")
            notification = {
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
            return project_name, client_name, notification, refresh_trigger, log
        except Exception as e:
            print(f"Exception adding project: {e}")
            notification = {
                "title": "Error",
                "message": f"Failed to add project: {str(e)}",
                "color": "red",
                "icon": "❌"
            }
            log = (log_data or []) + [{
                "type": "error",
                "message": f"Failed to add project: {str(e)}",
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }]
            return project_name, client_name, notification, refresh_trigger, log
