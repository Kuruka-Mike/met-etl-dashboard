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
import dash_bootstrap_components as dbc
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
                spacing="sm",
                align="center",
                children=[
                    dmc.Text("Total Clients", size="md", weight=600, color="white", align="center"),
                    dmc.Text(str(total_clients), size="2xl", weight=700, color="white", align="center"),
                    dmc.Text("In Database", size="sm", color="rgba(255,255,255,0.8)", align="center")
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
            "background": "#23262f",
            "border": "1px solid #3a3d46",
            "width": "250px",
            "height": "180px",
        },
        children=[
            dmc.Stack(
                spacing="sm",
                children=[
                    dmc.Text("Quick Actions", size="md", weight=600, color="white", mb="xs"),
                    dmc.Button(
                        "Add New Client",
                        id="open-modern-add-client-btn",
                        leftIcon="➕",
                        color="blue",
                        size="sm",
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Refresh Data",
                        id="refresh-clients-btn",
                        leftIcon="🔄",
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
            style={"background": "#23262f", "border": "1px solid #3a3d46", "textAlign": "center"},
            children=[
                dmc.Stack(
                    spacing="md",
                    align="center",
                    children=[
                        dmc.ThemeIcon(
                            children="📋",
                            size="lg",
                            radius="md",
                            color="gray",
                            variant="light"
                        ),
                        dmc.Text("No clients found", size="lg", weight=600, color="white"),
                        dmc.Text("Get started by adding your first client", size="sm", color="dimmed"),
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
            html.Tr([
                html.Td(str(i), style={"color": "white", "padding": "8px"}),
                html.Td(client_name, style={"color": "white", "padding": "8px", "fontWeight": "600"}),
                html.Td(str(project_count), style={"color": "white", "padding": "8px"}),
                html.Td(
                    dmc.Badge("Active", color="green", variant="light", size="sm"),
                    style={"padding": "8px"}
                ),
                html.Td(
                    dmc.Group(
                        spacing="xs",
                        children=[
                            dmc.Button("View", size="xs", variant="light", color="blue"),
                            dmc.Button("Edit", size="xs", variant="outline", color="gray")
                        ]
                    ),
                    style={"padding": "8px"}
                )
            ])
        )
    
    return dmc.Paper(
        radius="md",
        p="md",
        style={"background": "#23262f", "border": "1px solid #3a3d46"},
        children=[
            dmc.Group(
                position="apart",
                mb="md",
                children=[
                    dmc.Text("Client Directory", size="lg", weight=700, color="white"),
                    dmc.TextInput(
                        placeholder="Search clients...",
                        icon="🔍",
                        style={"width": "200px"},
                        size="sm"
                    )
                ]
            ),
            dmc.Table(
                striped=True,
                highlightOnHover=True,
                style={"backgroundColor": "#23262f"},
                children=[
                    html.Thead([
                        html.Tr([
                            html.Th("#", style={"color": "white", "backgroundColor": "#2a2d36", "padding": "8px"}),
                            html.Th("Client Name", style={"color": "white", "backgroundColor": "#2a2d36", "padding": "8px"}),
                            html.Th("Projects", style={"color": "white", "backgroundColor": "#2a2d36", "padding": "8px"}),
                            html.Th("Status", style={"color": "white", "backgroundColor": "#2a2d36", "padding": "8px"}),
                            html.Th("Actions", style={"color": "white", "backgroundColor": "#2a2d36", "padding": "8px"}),
                        ])
                    ]),
                    html.Tbody(table_rows)
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
                spacing="md",
                children=[
                    dmc.TextInput(
                        label="Client Name",
                        placeholder="Enter client name (e.g., WindTech Solutions)",
                        id="modern-client-name-input",
                        required=True,
                        style={"width": "100%"}
                    ),
                    dmc.Group(
                        position="right",
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
                position="apart",
                mb="lg",
                children=[
                    dmc.Stack(
                        spacing="xs",
                        children=[
                            dmc.Title("Client Management", order=2, color="white"),
                            dmc.Text("Manage your client accounts", color="dimmed", size="md")
                        ]
                    ),
                ]
            ),
            # Metrics Row
            dmc.Group(
                spacing="md",
                mb="lg",
                align="flex-start",
                children=[
                    html.Div(id="client-metrics-container"),
                    create_client_actions_card()
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
