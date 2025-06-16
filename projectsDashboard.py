"""
Projects Dashboard module for the modernized Dash app.

- Modern client-organized project management interface
- Database integration for client, project, and asset data
- Clean, professional UI components for project operations
- Add new project functionality with modal integration
"""

import dash
import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State
from DBcontroller import DBcontoller
from addProjectModal import create_add_project_modal

dbc_instance = DBcontoller()

def create_project_metrics_card(total_projects=0):
    """Create a modern metrics card showing total projects"""
    return dmc.Paper(
        radius="md",
        p="lg",
        style={
            "background": "linear-gradient(135deg, #2196F3 0%, #1976D2 100%)",
            "border": "1px solid #3a3d46",
            "width": "180px",
            "height": "180px",
            "color": "white",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center"
        },
        children=[
            dmc.Stack(
                gap="sm",
                align="center",
                children=[
                    dmc.Text("Total Projects", fz="md", fw=600, c="white", ta="center"),
                    dmc.Text(str(total_projects), fz="2xl", fw=700, c="white", ta="center"),
                    dmc.Text("In Database", fz="sm", c="rgba(255,255,255,0.8)", ta="center")
                ]
            )
        ]
    )

def create_project_actions_card():
    """Create action buttons card for project management"""
    return dmc.Paper(
        radius="md",
        p="lg",
        style={
            # "background": "#23262f", # Let theme handle
            # "border": "1px solid #3a3d46", # Let theme handle
            "width": "250px",
            "height": "180px",
        },
        children=[
            dmc.Stack(
                gap="sm",
                children=[
                    dmc.Text("Quick Actions", fz="md", fw=600, mb="xs"), # Removed c="white"
                    dmc.Button(
                        "Add New Project",
                        id="quick-add-project-btn",
                        leftSection="➕",
                        color="blue",
                        size="sm",
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Refresh Data",
                        id="refresh-projects-btn",
                        leftSection="🔄",
                        color="gray",
                        variant="light",
                        size="sm",
                        fullWidth=True
                    )
                ]
            )
        ]
    )

def create_projects_dashboard_layout():
    """Create the complete projects dashboard layout"""
    return html.Div(
        style={"padding": "20px", "maxWidth": "1200px", "margin": "0 auto"},
        children=[
            dcc.Store(id="projects-dashboard-refresh-trigger", data=0),
            create_add_project_modal(),
            # Header Section
            dmc.Stack(
                gap="xs",
                mb="lg",
                children=[
                    dmc.Title("Project Management", order=2), # Removed c="white"
                    dmc.Text("Organize and manage projects by client", c="dimmed", fz="md")
                ]
            ),
            # Metrics Row
            dmc.Group(
                gap="md",
                mb="lg",
                align="flex-start",
                children=[
                    create_project_actions_card(),
                    html.Div(id="project-metrics-container")
                ]
            ),
            # Client-organized project cards
            html.Div(id="projects-list-container"),
            # Notification area
            html.Div(id="projects-notification-area"),
        ]
    )

@callback(
    Output("projects-dashboard-refresh-trigger", "data", allow_duplicate=True),
    Input("refresh-projects-btn", "n_clicks"),
    State("projects-dashboard-refresh-trigger", "data"),
    prevent_initial_call=True
)
def refresh_projects_data(n_clicks, current_trigger):
    if n_clicks:
        return (current_trigger or 0) + 1
    return current_trigger

@callback(
    [Output("project-metrics-container", "children"),
     Output("projects-list-container", "children")],
    Input("projects-dashboard-refresh-trigger", "data")
)
def update_projects_dashboard(refresh_trigger):
    # Fetch all client-project-asset data
    data = dbc_instance.getClientsProjectsAssets()
    # Organize by client
    clients = {}
    for row in data:
        client = row["ClientName"] or "No Client"
        if client not in clients:
            clients[client] = []
        if row["ProjectID"] is not None:
            clients[client].append(row)
    total_projects = dbc_instance.getTotalProjectCount()

    cards = []
    for client, projects in clients.items():
        card = dmc.Paper(
            radius="md",
            p="lg",
            # style={"background": "#23262f", "border": "1px solid #3a3d46"}, # Let theme handle
            children=[
                dmc.Group(
                    justify="space-between",
                    mb="md",
                    children=[
                        dmc.Title(client, order=4, c="blue.5"),
                        dmc.Tooltip(
                            label="Add New Project",
                            withArrow=True,
                            children=[
                                dmc.ActionIcon(
                                    "➕",
                                    id={"type": "add-project-to-client-btn", "client": client},
                                    variant="light",
                                    color="blue",
                                    size="lg"
                                )
                            ]
                        )
                    ]
                ),
                dmc.Table(
                    striped=True,
                    highlightOnHover=True,
                    withTableBorder=True,
                    withColumnBorders=True,
                    withRowBorders=True,
                    # style={"backgroundColor": "#23262f"}, # Let theme handle
                    children=[
                            dmc.TableThead([
                                dmc.TableTr([
                                    dmc.TableTh("Project Name", style={"width": "300px"}),
                                    dmc.TableTh("Assets", style={"width": "100px", "textAlign": "center"}),
                                    dmc.TableTh("Actions", style={"width": "200px"}),
                                ])
                            ]),
                            dmc.TableTbody([
                                dmc.TableTr([
                                    dmc.TableTd(
                                        project["ProjectName"] or "No Project",
                                        style={
                                            "fontWeight": "600",
                                            "overflow": "hidden",
                                            "textOverflow": "ellipsis",
                                            "whiteSpace": "nowrap",
                                            "maxWidth": 0,
                                        }
                                    ),
                                    dmc.TableTd(
                                        str(project["AssetCount"] or 0),
                                        style={"textAlign": "center"}
                                    ),
                                    dmc.TableTd(
                                        dmc.Group(
                                        gap="xs",
                                        children=[
                                            dmc.Button("View", size="xs", variant="light", color="blue"),
                                            dmc.Button("Edit", size="xs", variant="outline", color="gray"),
                                            dmc.Button("Add Asset", size="xs", variant="outline", color="green"),
                                        ]
                                    )
                                    # style={"padding": "4px"} # Padding handled by dmc.Table spacing or CSS
                                )
                            ]) for project in projects
                        ])
                    ]
                )
            ]
        )
        cards.append(card)

    project_cards = dmc.Stack(gap="xl", children=cards)
    return create_project_metrics_card(total_projects), project_cards
