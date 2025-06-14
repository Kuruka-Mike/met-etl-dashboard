"""
Modern UI components module for the modernized Dash app.

Defines:
- create_kpi_card(): Modern KPI card component
- create_chart_card(): Chart container component
- create_dashboard_overview(): Main dashboard overview page
- create_clients_page(): Client management page
- create_projects_page(): Project portfolio page
- create_assets_page(): Asset monitoring page
- create_admin_page(): System administration page
"""

import dash_mantine_components as dmc
from dash import html, dcc
import plotly.express as px
import pandas as pd
from clientsDashboard import create_clients_dashboard_layout
from projectsDashboard import create_projects_dashboard_layout
from assetsDashboard import create_assets_dashboard_layout

def create_kpi_card(title, value, change, icon, color):
    """Create a modern KPI card component"""
    return dmc.Paper(
        radius="md",
        p="lg",
        style={
            "background": "linear-gradient(135deg, #23262f 0%, #2a2d36 100%)",
            "border": "1px solid #3a3d46",
            "minHeight": "120px"
        },
        children=[
            dmc.Group(
                position="apart",
                align="flex-start",
                children=[
                    dmc.Stack(
                        spacing="xs",
                        children=[
                            dmc.Text(title, size="sm", color="dimmed", weight=500),
                            dmc.Text(value, size="xl", weight=700, color="white"),
                            dmc.Group(
                                spacing="xs",
                                children=[
                                    dmc.Text(change, size="sm", color=color, weight=500),
                                    dmc.Text("vs last month", size="xs", color="dimmed")
                                ]
                            )
                        ]
                    ),
                    dmc.ThemeIcon(
                        icon,
                        size="lg",
                        radius="md",
                        color=color,
                        variant="light"
                    )
                ]
            )
        ]
    )

def create_chart_card(title, chart_component):
    """Create a chart card container"""
    return dmc.Paper(
        radius="md",
        p="lg",
        style={
            "background": "#23262f",
            "border": "1px solid #3a3d46",
            "minHeight": "300px"
        },
        children=[
            dmc.Text(title, size="lg", weight=600, color="white", mb="md"),
            chart_component
        ]
    )

def create_dashboard_overview():
    """Create the main dashboard overview page"""
    # Sample data for charts
    df_revenue = pd.DataFrame({
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'Revenue': [45000, 52000, 48000, 61000, 55000, 67000]
    })
    
    revenue_chart = dcc.Graph(
        figure=px.line(
            df_revenue, x='Month', y='Revenue',
            title="Revenue Trend"
        ).update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='white'
        ),
        config={'displayModeBar': False},
        style={'height': '250px'}
    )
    
    # Asset distribution pie chart
    asset_data = pd.DataFrame({
        'Type': ['MET Towers', 'Lidars', 'Sodars', 'Other'],
        'Count': [45, 23, 12, 8]
    })
    
    asset_chart = dcc.Graph(
        figure=px.pie(
            asset_data, values='Count', names='Type',
            title="Asset Distribution"
        ).update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='white'
        ),
        config={'displayModeBar': False},
        style={'height': '250px'}
    )
    
    return dmc.Container(
        fluid=True,
        px="xl",
        py="xl",
        children=[
            # KPI Cards Row
            dmc.Grid(
                gutter="xl",
                children=[
                    dmc.Col(create_kpi_card("Total Assets", "88", "+12%", "📊", "green"), span=3),
                    dmc.Col(create_kpi_card("Active Projects", "24", "+8%", "💼", "blue"), span=3),
                    dmc.Col(create_kpi_card("Total Clients", "15", "+3%", "👥", "orange"), span=3),
                    dmc.Col(create_kpi_card("Data Points", "2.4M", "+15%", "📈", "purple"), span=3),
                ]
            ),
            
            dmc.Space(h="xl"),
            
            # Charts Row
            dmc.Grid(
                gutter="xl",
                children=[
                    dmc.Col(create_chart_card("Revenue Overview", revenue_chart), span=8),
                    dmc.Col(create_chart_card("Asset Distribution", asset_chart), span=4),
                ]
            ),
            
            dmc.Space(h="xl"),
            
            # Recent Activity and Status
            dmc.Grid(
                gutter="xl",
                children=[
                    dmc.Col(
                        dmc.Paper(
                            radius="md",
                            p="lg",
                            style={"background": "#23262f", "border": "1px solid #3a3d46"},
                            children=[
                                dmc.Text("Recent Activity", size="lg", weight=600, color="white", mb="md"),
                                dmc.Stack(
                                    spacing="sm",
                                    children=[
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("New MET tower deployed - Site 0779", size="sm", color="white"),
                                                dmc.Badge("2 hours ago", color="green", variant="light")
                                            ]
                                        ),
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Data ingestion completed - Project Alpha", size="sm", color="white"),
                                                dmc.Badge("4 hours ago", color="blue", variant="light")
                                            ]
                                        ),
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Client onboarding - WindTech Solutions", size="sm", color="white"),
                                                dmc.Badge("1 day ago", color="orange", variant="light")
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),
                        span=6
                    ),
                    dmc.Col(
                        dmc.Paper(
                            radius="md",
                            p="lg",
                            style={"background": "#23262f", "border": "1px solid #3a3d46"},
                            children=[
                                dmc.Text("System Status", size="lg", weight=600, color="white", mb="md"),
                                dmc.Stack(
                                    spacing="md",
                                    children=[
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Data Pipeline", size="sm", color="white"),
                                                dmc.Badge("Operational", color="green")
                                            ]
                                        ),
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Email Processing", size="sm", color="white"),
                                                dmc.Badge("Operational", color="green")
                                            ]
                                        ),
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Database", size="sm", color="white"),
                                                dmc.Badge("Operational", color="green")
                                            ]
                                        ),
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("API Services", size="sm", color="white"),
                                                dmc.Badge("Maintenance", color="yellow")
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        ),
                        span=6
                    ),
                ]
            )
        ]
    )

def create_clients_page():
    """Create the clients management page using the dedicated clients dashboard"""
    return create_clients_dashboard_layout()

def create_projects_page():
    """Create the projects management page using the new dashboard layout"""
    return create_projects_dashboard_layout()

def create_assets_page():
    """Create the assets management page using the dedicated assets dashboard"""
    return create_assets_dashboard_layout()

def create_admin_page():
    """Create the admin and overview page"""
    return dmc.Container(
        fluid=True,
        px="xl",
        py="xl",
        children=[
            dmc.Title("System Administration", order=2, color="white", mb="xl"),
            
            dmc.Grid(
                gutter="xl",
                children=[
                    dmc.Col(
                        dmc.Paper(
                            radius="md",
                            p="lg",
                            style={"background": "#23262f", "border": "1px solid #3a3d46"},
                            children=[
                                dmc.Text("User Management", size="lg", weight=600, color="white", mb="md"),
                                dmc.Stack(
                                    spacing="sm",
                                    children=[
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Active Users", size="sm", color="white"),
                                                dmc.Text("24", size="sm", weight=600, color="blue")
                                            ]
                                        ),
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Admin Users", size="sm", color="white"),
                                                dmc.Text("3", size="sm", weight=600, color="orange")
                                            ]
                                        ),
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Pending Invites", size="sm", color="white"),
                                                dmc.Text("2", size="sm", weight=600, color="yellow")
                                            ]
                                        ),
                                    ]
                                ),
                                dmc.Button("Manage Users", mt="md", variant="light", fullWidth=True)
                            ]
                        ),
                        span=4
                    ),
                    dmc.Col(
                        dmc.Paper(
                            radius="md",
                            p="lg",
                            style={"background": "#23262f", "border": "1px solid #3a3d46"},
                            children=[
                                dmc.Text("System Health", size="lg", weight=600, color="white", mb="md"),
                                dmc.Stack(
                                    spacing="sm",
                                    children=[
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("CPU Usage", size="sm", color="white"),
                                                dmc.Text("45%", size="sm", weight=600, color="green")
                                            ]
                                        ),
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Memory Usage", size="sm", color="white"),
                                                dmc.Text("62%", size="sm", weight=600, color="yellow")
                                            ]
                                        ),
                                        dmc.Group(
                                            position="apart",
                                            children=[
                                                dmc.Text("Disk Usage", size="sm", color="white"),
                                                dmc.Text("78%", size="sm", weight=600, color="orange")
                                            ]
                                        ),
                                    ]
                                ),
                                dmc.Button("View Details", mt="md", variant="light", fullWidth=True)
                            ]
                        ),
                        span=4
                    ),
                    dmc.Col(
                        dmc.Paper(
                            radius="md",
                            p="lg",
                            style={"background": "#23262f", "border": "1px solid #3a3d46"},
                            children=[
                                dmc.Text("Configuration", size="lg", weight=600, color="white", mb="md"),
                                dmc.Stack(
                                    spacing="sm",
                                    children=[
                                        dmc.Button("Email Settings", variant="light", fullWidth=True),
                                        dmc.Button("Database Config", variant="light", fullWidth=True),
                                        dmc.Button("API Settings", variant="light", fullWidth=True),
                                        dmc.Button("Backup & Recovery", variant="light", fullWidth=True),
                                    ]
                                )
                            ]
                        ),
                        span=4
                    ),
                ]
            )
        ]
    )
