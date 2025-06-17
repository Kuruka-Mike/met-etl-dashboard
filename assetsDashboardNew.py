"""
Assets Dashboard module for the modernized Dash app (New Version).

Responsibilities:
- Modern asset management interface organized by client and project
- Database integration for asset data across multiple tables
- Clean, professional UI components for asset operations
- Add new asset functionality with wizard integration
"""

import dash
import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State, no_update
from DBcontroller import DBcontoller
from addAssetModal import create_add_asset_modal
from projectAssetModal import create_project_asset_modal
from projectAssetDetailModal import create_project_asset_detail_modal


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
            "height": "200px",  # Increased to match quick actions card
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
                    dmc.Text(title, fz="md", fw=600, c="white", ta="center"),
                    dmc.Text(str(value), fz="2xl", fw=700, c="white", ta="center"),
                    dmc.Text("Active assets", fz="sm", c="rgba(255,255,255,0.8)", ta="center")
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
            "width": "250px",
            "height": "200px",  # Increased height to fit all buttons
        },
        children=[
            dmc.Stack(
                gap="xs",  # Reduced gap between elements
                children=[
                    dmc.Text("Quick Actions", fz="md", fw=600, mb="0"),
                    dmc.Button(
                        "Add New Asset",
                        id="add-asset-btn-v2",
                        leftSection="➕",
                        color="blue",
                        size="sm",  # Back to original size
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Move Lidar",
                        id="move-lidar-btn-new",
                        leftSection="↔️",
                        color="gray",
                        variant="light",
                        size="sm",  # Back to original size
                        fullWidth=True
                    ),
                    dmc.Button(
                        "Refresh Data",
                        id="refresh-assets-btn-new",
                        leftSection="🔄",
                        color="gray",
                        variant="light",
                        size="sm",  # Back to original size
                        fullWidth=True
                    )
                ]
            )
        ]
    )

def create_asset_table_for_project(assets_data, project_id):
    """Create an asset table for a specific project"""
    if not assets_data or len(assets_data) == 0:
        return dmc.Paper(
            radius="md",
            p="lg",
            # style={"background": "#2a2d36", "border": "1px solid #3a3d46", "textAlign": "center"}, # Let theme handle
            style={"textAlign": "center"}, # Keep textAlign
            children=[
                dmc.Stack(
                    gap="md",
                    align="center",
                    children=[
                        dmc.Text("No assets found", fz="lg", fw=600),
                        dmc.Text("There are no assets associated with this project.", fz="sm", c="dimmed"),
                    ]
                )
            ]
        )
    
    # Create asset table rows
    table_rows = []
    for i, asset in enumerate(assets_data):
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
        
        asset_name = asset.get("AssetName", "Unknown")
        asset_id = f"asset-{project_id}-{i}"  # Generate a unique ID for each asset
        
        table_rows.append(
            dmc.TableTr([
                dmc.TableTd(
                    asset_name, 
                    style={"fontWeight": "600"} # Keep fontWeight, remove color and padding
                ),
                dmc.TableTd(
                    type_and_pairing
                    # Removed style={"color": "white", "padding": "8px"}
                ),
                dmc.TableTd(
                    dmc.Badge(status_text, color=status_color, variant="light", size="sm")
                    # Removed style={"padding": "8px"}
                ),
                dmc.TableTd(
                    dmc.Group(
                        gap="xs",
                        children=[
                            dmc.Button("View", id=f"view-asset-btn-{asset_id}", size="xs", variant="light", color="blue"),
                            dmc.Button("Edit", id=f"edit-asset-btn-{asset_id}", size="xs", variant="outline", color="gray"),
                            dmc.Button("Config", id=f"config-asset-btn-{asset_id}", size="xs", variant="outline", color="green")
                        ]
                    )
                    # Removed style={"padding": "8px"}
                )
            ])
        )
    
    return dmc.Table(
        striped=True,
        highlightOnHover=True,
        withTableBorder=True,
        withColumnBorders=True,
        withRowBorders=True,
        # style={"backgroundColor": "#23262f"}, # Let theme handle
        children=[
            dmc.TableThead([
                dmc.TableTr([
                    dmc.TableTh("Asset Name"), # Removed style
                    dmc.TableTh("Type & Pairing"), # Removed style
                    dmc.TableTh("Status"), # Removed style
                    dmc.TableTh("Actions"), # Removed style
                ])
            ]),
            dmc.TableTbody(table_rows)
        ]
    )

def create_assets_dashboard_layout():
    """Create the complete assets dashboard layout."""
    return html.Div(
        style={"padding": "20px", "maxWidth": "1200px", "margin": "0 auto"},
        children=[
            dcc.Store(id="assets-dashboard-refresh-trigger-new", data=0),
            dcc.Store(id="current-project-asset-id-store", data=None),
            
            # Header Section
            dmc.Stack(
                gap="xs",
                mb="lg",
                children=[
                    dmc.Title("Asset Management", order=2), # Removed c="white"
                    dmc.Text("Manage assets by client and project", c="dimmed", fz="md")
                ]
            ),
            
            # Metrics Row
            dmc.Group(
                gap="md",
                mb="lg",
                align="flex-start",
                children=[
                    create_asset_actions_card(),
                    html.Div(id="total-assets-card-new"),  
                    html.Div(id="met-towers-card-new"),    
                    html.Div(id="lidars-card-new")        
                    
                ]
            ),
            
            # Client-organized asset cards
            html.Div(id="assets-list-container-new"),  # Changed ID to avoid conflicts
            
            # Notification area
            html.Div(id="assets-notification-area-new"),  # Changed ID to avoid conflicts
            
            # Add the modals
            create_add_asset_modal(),
            create_project_asset_modal(),
            create_project_asset_detail_modal(),
        ]
    )

# Callback to handle refresh button clicks
@callback(
    Output("assets-dashboard-refresh-trigger-new", "data", allow_duplicate=True),
    Input("refresh-assets-btn-new", "n_clicks"),
    State("assets-dashboard-refresh-trigger-new", "data"),
    prevent_initial_call=True
)
def refresh_assets_data(n_clicks, current_trigger):
    if n_clicks:
        return (current_trigger or 0) + 1
    return current_trigger

@callback(
    [Output("total-assets-card-new", "children"),
     Output("met-towers-card-new", "children"),
     Output("lidars-card-new", "children"),
     Output("assets-list-container-new", "children")],
    Input("assets-dashboard-refresh-trigger-new", "data")
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
            client_name = asset.get("ClientName", "Unknown")
            project_name = asset.get("ProjectName", "Unknown")
            
            # Ensure client_name and project_name are strings
            client_name = str(client_name) if client_name is not None else "Unknown"
            project_name = str(project_name) if project_name is not None else "Unknown"
            
            # Initialize client if not exists
            if client_name not in organized_data:
                organized_data[client_name] = {}
            
            # Initialize project if not exists
            if project_name not in organized_data[client_name]:
                organized_data[client_name][project_name] = []
            
            # Add asset to project
            asset_info = {
                "AssetName": asset.get("AssetName", "Unknown"),
                "AssetType": asset.get("AssetType", "Unknown"),
                "Status": "Active",  # Placeholder status for now
                "PairedMET": asset.get("PairedMET", None)
            }
            
            organized_data[client_name][project_name].append(asset_info)
        
        return organized_data
        
    except Exception as e:
        print(f"Error getting assets data: {e}")
        # Return empty dict on error
        return {}

def create_client_project_asset_cards(assets_data):
    """Create asset cards organized by client and project"""
    if not assets_data or len(assets_data) == 0:
        return dmc.Paper(
            radius="md",
            p="lg",
            # style={"background": "#23262f", "border": "1px solid #3a3d46", "textAlign": "center"}, # Let theme handle
            style={"textAlign": "center"}, # Keep textAlign
            children=[
                dmc.Stack(
                    gap="md",
                    align="center",
                    children=[
                        dmc.Text("No assets found", fz="lg", fw=600),
                        dmc.Text("There are no assets in the system.", fz="sm", c="dimmed"),
                    ]
                )
            ]
        )
    
    cards = []
    client_project_counter = 0  # Counter to generate unique IDs
    
    for client_name, projects in assets_data.items():
        for project_name, project_assets in projects.items():
            client_project_counter += 1
            project_id = f"project-{client_project_counter}"  # Generate a unique ID for each project
            asset_count = len(project_assets)
            
            card = dmc.Paper(
                radius="md",
                p="lg",
                # style={"background": "#23262f", "border": "1px solid #3a3d46"}, # Let theme handle
                children=[
                    dmc.Group(
                        justify="space-between",
                        mb="md",
                        children=[
                            dmc.Stack(
                                gap="xs",
                                children=[
                                    dmc.Title(client_name, order=4, c="blue.5"),
                                    dmc.Text(f"{project_name} ({asset_count} assets)", fz="md", fw=600) # Removed c="white"
                                ]
                            )
                        ]
                    ),
                    create_asset_table_for_project(project_assets, project_id)
                ]
            )
            cards.append(card)
    
    return dmc.Stack(gap="xl", children=cards)

# The callback for toggling the asset modal is now handled in addAssetModal.py
