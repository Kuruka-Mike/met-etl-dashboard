"""
Clients Dashboard module for the modernized Dash app.

Responsibilities:
- Modern client management interface
- Database integration for client data (tbl_clients)
- Clean, professional UI components for client operations
- Add new client functionality with modal integration
"""

import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State
from DBcontroller import DBcontoller
from addClientModal import create_add_client_modal

# Initialize database controller
dbc_instance = DBcontoller()

def create_client_metrics_card(total_clients=0):
    """Create a modern metrics card showing total clients"""
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
                    dmc.Text("Total Clients", fz="md", fw=600, c="white", ta="center"),
                    dmc.Text(str(total_clients), fz="2xl", fw=700, c="white", ta="center"),
                    dmc.Text("In Database", fz="sm", c="rgba(255,255,255,0.8)", ta="center")
                ]
            )
        ]
    )

def create_client_actions_card():
    """Create action buttons card for client management"""
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
                        "Add New Client",
                        id="open-modern-add-client-btn",
                        leftSection="➕",
                        color="blue",
                        size="sm",
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Refresh Data",
                        id="refresh-clients-btn",
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

def create_simple_clients_table(clients_data=None):
    """Create a simple, fast-loading clients table"""
    if not clients_data:
        # Empty state
        return dmc.Paper(
            radius="md",
            p="lg",
            # style={"background": "#23262f", "border": "1px solid #3a3d46", "textAlign": "center"}, # Let theme handle
            style={"textAlign": "center"},
            children=[
                dmc.Stack(
                    gap="md",
                    align="center",
                    children=[
                        dmc.ThemeIcon(
                            children="📋",
                            size="lg",
                            radius="md",
                            color="gray",
                            variant="light"
                        ),
                        dmc.Text("No clients found", fz="lg", fw=600), # Removed c="white"
                        dmc.Text("Get started by adding your first client", fz="sm"), # Removed c="dimmed"
                        dmc.Button(
                            "Add First Client",
                            id="add-first-client-btn",
                            color="blue",
                            size="md"
                        )
                    ]
                )
            ]
        )
    
    # Create simple table rows
    table_rows = []
    for i, (client_name, project_count) in enumerate(clients_data, 1):
        table_rows.append(
            dmc.TableTr([
                dmc.TableTd(str(i)),
                dmc.TableTd(client_name, style={"fontWeight": "600"}),
                dmc.TableTd(str(project_count)),
                dmc.TableTd(
                    dmc.Badge("Active", color="green", variant="light", size="sm")
                ),
                dmc.TableTd(
                    dmc.Group(
                        gap="xs",
                        children=[
                            dmc.Button("View", size="xs", variant="light", color="blue"),
                            dmc.Button("Edit", size="xs", variant="outline", color="gray")
                        ]
                    )
                )
            ])
        )
    
    return dmc.Paper(
        radius="md",
        p="md",
        # style={"background": "#23262f", "border": "1px solid #3a3d46"}, # Let theme handle
        children=[
            dmc.Group(
                justify="space-between",
                mb="md",
                children=[
                    dmc.Text("Client Directory", fz="lg", fw=700), # Removed c="white"
                    dmc.TextInput(
                        placeholder="Search clients...",
                        leftSection="🔍",
                        style={"width": "200px"},
                        size="sm"
                    )
                ]
            ),
            dmc.Table(
                striped=True,
                highlightOnHover=True,
                withTableBorder=True,
                withColumnBorders=True,
                withRowBorders=True,
                children=[
                    dmc.TableThead([
                        dmc.TableTr([
                            dmc.TableTh("#", style={"textAlign": "left"}),
                            dmc.TableTh("Client Name", style={"textAlign": "left"}),
                            dmc.TableTh("Projects", style={"textAlign": "left"}),
                            dmc.TableTh("Status", style={"textAlign": "left"}),
                            dmc.TableTh("Actions", style={"textAlign": "left"}),
                        ])
                    ]),
                    dmc.TableTbody(table_rows)
                ]
            )
        ]
    )

def create_modern_add_client_modal():
    """Create a modern add client modal using Mantine components"""
    return dmc.Modal(
        title="Add New Client",
        id="modern-add-client-modal",
        size="md",
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
            )
        ]
    )
    

def create_clients_dashboard_layout():
    """Create a simple, fast-loading clients dashboard layout"""
    return html.Div(
        style={"padding": "20px", "maxWidth": "1200px", "margin": "0 auto"},
        children=[
            # Header Section
            dmc.Group(
                justify="space-between",
                mb="lg",
                children=[
                    dmc.Stack(
                        gap="xs",
                        children=[
                            dmc.Title("Client Management", order=2), # Removed c="white"
                            dmc.Text("Manage your client accounts", fz="md") # Removed c="dimmed"
                        ]
                    ),
                ]
            ),
            # Metrics Row
            dmc.Group(
                gap="md",
                mb="lg",
                align="flex-start",
                children=[
                    create_client_actions_card(),
                    html.Div(id="client-metrics-container"),
                ]
            ),
            
            # Main Content - Clients Table
            html.Div(id="clients-table-container"),
            
            # Add the modern modal (now replaced with the new modular version)
            create_add_client_modal(),

            # Notification area
            html.Div(id="clients-notification-area"),
            
            # Hidden components
            html.Div([
                dcc.Store(id="clients-refresh-trigger", data=0),
                dcc.Store(id="clients-data-store", data=[])
            ], style={"display": "none"})
        ]
    )

# Callback to handle refresh button clicks
@callback(
    Output("clients-refresh-trigger", "data", allow_duplicate=True),
    Input("refresh-clients-btn", "n_clicks"),
    State("clients-refresh-trigger", "data"),
    prevent_initial_call=True
)
def refresh_clients_data(n_clicks, current_trigger):
    if n_clicks:
        return (current_trigger or 0) + 1
    return current_trigger

# Callback to load client data efficiently
@callback(
    [Output("clients-data-store", "data"),
     Output("client-metrics-container", "children"),
     Output("clients-table-container", "children")],
    Input("clients-refresh-trigger", "data"),
    prevent_initial_call=False
)
def load_clients_data(trigger):
    try:
        # Use the optimized method to get all clients and their project counts in one call
        clients_data = dbc_instance.getClientsWithProjectCounts()
        if not clients_data:
            return [], create_client_metrics_card(0), create_simple_clients_table()
        # clients_data is a list of dicts: [{ClientName: ..., ProjectCount: ...}, ...]
        total_clients = len(clients_data)
        metrics_card = create_client_metrics_card(total_clients)
        # Convert to list of tuples for the table: (client_name, project_count)
        table_data = [(row["ClientName"], row["ProjectCount"]) for row in clients_data]
        table = create_simple_clients_table(table_data)
        return clients_data, metrics_card, table
    except Exception as e:
        print(f"Error loading clients data: {e}")
        error_msg = dmc.Alert(
            "Error loading client data. Please check database connection.",
            title="Database Error",
            color="red"
        )
        return [], create_client_metrics_card(0), error_msg

# (Removed duplicate modal open/close and add client callbacks - now handled in addClientModal.py)
