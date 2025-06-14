"""
Assets Dashboard module for the modernized Dash app.

Responsibilities:
- Modern asset management interface organized by client and project
- Database integration for asset data across multiple tables
- Clean, professional UI components for asset operations
- Add new asset functionality with wizard integration
"""

import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State
from DBcontroller import DBcontoller
from addAssetModal import create_add_asset_modal

dbc_instance = DBcontoller()

def create_asset_metrics_card(title, value):
    """Create a modern metrics card for assets (consistent with other dashboards)"""
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
                    dmc.Text(title, size="md", weight=600, color="white", align="center"),
                    dmc.Text(str(value), size="2xl", weight=700, color="white", align="center"),
                    dmc.Text("Active assets", size="sm", color="rgba(255,255,255,0.8)", align="center")
                ]
            )
        ]
    )

def create_asset_actions_card():
    """Create action buttons card for asset management"""
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
                        "Add New Asset",
                        id="quick-add-asset-btn",
                        leftIcon="➕",
                        color="blue",
                        size="sm",
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Refresh Data",
                        id="refresh-assets-btn",
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

def create_asset_table_for_project(assets_data):
    """Create an asset table for a specific project"""
    if not assets_data:
        return dmc.Paper(
            radius="md",
            p="lg",
            style={"background": "#2a2d36", "border": "1px solid #3a3d46", "textAlign": "center"},
            children=[
                dmc.Stack(
                    spacing="md",
                    align="center",
                    children=[
                        dmc.Text("No assets found", size="lg", weight=600, color="white"),
                        dmc.Text("Get started by adding your first asset to this project", size="sm", color="dimmed"),
                        dmc.Button(
                            "Add First Asset",
                            id={"type": "add-first-asset-btn", "project": "placeholder"},
                            color="blue",
                            size="md"
                        )
                    ]
                )
            ]
        )
    
    # Create asset table rows
    table_rows = []
    for asset in assets_data:
        # Determine asset type display
        asset_type = asset.get("AssetType", "Unknown")
        
        # Handle MET pairing for Lidars - Enhanced Type & Pairing display
        if asset_type.upper() == "LIDAR":
            paired_met = asset.get("PairedMET")
            if paired_met:
                type_and_pairing = f"Lidar (→ {paired_met})"
            else:
                type_and_pairing = "Lidar (Standalone)"
        else:
            # For MET Towers and other asset types, just show the type
            type_and_pairing = asset_type
        
        # Placeholder status (will be replaced with ClickUp integration later)
        status_color = "green" if asset.get("Status", "Active") == "Active" else "yellow"
        status_text = asset.get("Status", "Active")
        
        table_rows.append(
            html.Tr([
                html.Td(
                    asset.get("AssetName", "Unknown"), 
                    style={"color": "white", "padding": "8px", "fontWeight": "600"}
                ),
                html.Td(
                    type_and_pairing, 
                    style={"color": "white", "padding": "8px"}
                ),
                html.Td(
                    dmc.Badge(status_text, color=status_color, variant="light", size="sm"),
                    style={"padding": "8px"}
                ),
                html.Td(
                    dmc.Group(
                        spacing="xs",
                        children=[
                            dmc.Button("View", size="xs", variant="light", color="blue"),
                            dmc.Button("Edit", size="xs", variant="outline", color="gray"),
                            dmc.Button("Config", size="xs", variant="outline", color="green")
                        ]
                    ),
                    style={"padding": "8px"}
                )
            ])
        )
    
    return dmc.Table(
        striped=True,
        highlightOnHover=True,
        style={"backgroundColor": "#23262f"},
        children=[
            html.Thead([
                html.Tr([
                    html.Th("Asset Name", style={"color": "white", "backgroundColor": "#2a2d36", "padding": "8px"}),
                    html.Th("Type & Pairing", style={"color": "white", "backgroundColor": "#2a2d36", "padding": "8px"}),
                    html.Th("Status", style={"color": "white", "backgroundColor": "#2a2d36", "padding": "8px"}),
                    html.Th("Actions", style={"color": "white", "backgroundColor": "#2a2d36", "padding": "8px"}),
                ])
            ]),
            html.Tbody(table_rows)
        ]
    )

def create_assets_dashboard_layout():
    """Create the complete assets dashboard layout."""
    return html.Div(
        style={"padding": "20px", "maxWidth": "1200px", "margin": "0 auto"},
        children=[
            create_add_asset_modal(),
            dcc.Store(id="assets-dashboard-refresh-trigger", data=0),
            
            # Header Section
            dmc.Stack(
                spacing="xs",
                mb="lg",
                children=[
                    dmc.Title("Asset Management", order=2, color="white"),
                    dmc.Text("Manage assets by client and project", color="dimmed", size="md")
                ]
            ),
            
            # Metrics Row
            dmc.Group(
                spacing="md",
                mb="lg",
                align="flex-start",
                children=[
                    html.Div(id="total-assets-card"),
                    html.Div(id="met-towers-card"),
                    html.Div(id="lidars-card"),
                    create_asset_actions_card()
                ]
            ),
            
            # Client-organized asset cards
            html.Div(id="assets-list-container"),
            
            # Notification area
            html.Div(id="assets-notification-area"),
        ]
    )

# Callback to handle refresh button clicks
@callback(
    Output("assets-dashboard-refresh-trigger", "data", allow_duplicate=True),
    Input("refresh-assets-btn", "n_clicks"),
    State("assets-dashboard-refresh-trigger", "data"),
    prevent_initial_call=True
)
def refresh_assets_data(n_clicks, current_trigger):
    if n_clicks:
        return (current_trigger or 0) + 1
    return current_trigger

@callback(
    [Output("total-assets-card", "children"),
     Output("met-towers-card", "children"),
     Output("lidars-card", "children"),
     Output("assets-list-container", "children")],
    Input("assets-dashboard-refresh-trigger", "data")
)
def update_assets_dashboard(refresh_trigger):
    # Get asset counts for metrics
    try:
        counts = dbc_instance.getAssetCounts()
        total_assets = counts["TotalAssets"]
        met_towers = counts["MetTowers"]
        lidars = counts["Lidars"]
    except Exception as e:
        print(f"Error getting asset counts: {e}")
        total_assets = met_towers = lidars = 0
    
    # Create metrics cards (consistent styling, no emojis)
    total_assets_card = create_asset_metrics_card("Total Assets", total_assets)
    met_towers_card = create_asset_metrics_card("MET Towers", met_towers)
    lidars_card = create_asset_metrics_card("Lidars", lidars)
    
    # Get hierarchical asset data (Client -> Project -> Assets)
    try:
        # This will need a new database method - for now, let's create a placeholder
        assets_data = get_assets_by_client_and_project()
        asset_cards = create_client_project_asset_cards(assets_data)
    except Exception as e:
        print(f"Error getting assets data: {e}")
        asset_cards = dmc.Alert(
            "Error loading asset data. Please check database connection.",
            title="Database Error",
            color="red"
        )
    
    return total_assets_card, met_towers_card, lidars_card, asset_cards

def get_assets_by_client_and_project():
    """Get assets organized by client and project from database"""
    try:
        # Get detailed asset data from database
        assets_data = dbc_instance.getClientsProjectsAssetsDetailed()
        
        # Organize data by client and project
        organized_data = {}
        
        for asset in assets_data:
            client_name = asset["ClientName"]
            project_name = asset["ProjectName"]
            
            # Initialize client if not exists
            if client_name not in organized_data:
                organized_data[client_name] = {}
            
            # Initialize project if not exists
            if project_name not in organized_data[client_name]:
                organized_data[client_name][project_name] = []
            
            # Add asset to project
            asset_info = {
                "AssetName": asset["AssetName"],
                "AssetType": asset["AssetType"],
                "Status": "Active",  # Placeholder status for now
                "PairedMET": asset["PairedMET"]
            }
            
            organized_data[client_name][project_name].append(asset_info)
        
        return organized_data
        
    except Exception as e:
        print(f"Error getting assets data: {e}")
        # Return empty dict on error
        return {}

def create_client_project_asset_cards(assets_data):
    """Create asset cards organized by client and project"""
    if not assets_data:
        return dmc.Paper(
            radius="md",
            p="lg",
            style={"background": "#23262f", "border": "1px solid #3a3d46", "textAlign": "center"},
            children=[
                dmc.Stack(
                    spacing="md",
                    align="center",
                    children=[
                        dmc.Text("No assets found", size="lg", weight=600, color="white"),
                        dmc.Text("Get started by adding your first asset", size="sm", color="dimmed"),
                        dmc.Button(
                            "Add First Asset",
                            id="add-first-asset-global-btn",
                            color="blue",
                            size="md"
                        )
                    ]
                )
            ]
        )
    
    cards = []
    for client_name, projects in assets_data.items():
        for project_name, project_assets in projects.items():
            asset_count = len(project_assets)
            
            card = dmc.Paper(
                radius="md",
                p="lg",
                style={"background": "#23262f", "border": "1px solid #3a3d46"},
                children=[
                    dmc.Group(
                        position="apart",
                        mb="md",
                        children=[
                            dmc.Stack(
                                spacing="xs",
                                children=[
                                    dmc.Title(client_name, order=4, color="blue"),
                                    dmc.Text(f"{project_name} ({asset_count} assets)", size="md", color="white", weight=600)
                                ]
                            ),
                            dmc.Tooltip(
                                label="Add Asset to Project",
                                withArrow=True,
                                children=[
                                    dmc.ActionIcon(
                                        "➕",
                                        id={"type": "add-asset-to-project-btn", "client": client_name, "project": project_name},
                                        variant="light",
                                        color="blue",
                                        size="lg"
                                    )
                                ]
                            )
                        ]
                    ),
                    create_asset_table_for_project(project_assets)
                ]
            )
            cards.append(card)
    
    return dmc.Stack(spacing="xl", children=cards)
