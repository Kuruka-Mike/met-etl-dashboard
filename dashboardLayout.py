"""
Mantine-style dashboard layout using dash-mantine-components (dmc).

- Modern sidebar with navigation icons
- Sleek topbar with search and branding
- Main dashboard grid with analytics cards and charts
- Enterprise-ready responsive design
"""

import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd

def create_navigation_sidebar(active_page=None):
    """Create the icon-based navigation sidebar"""
    
    def create_nav_icon(icon_emoji, href, label, is_active=False):
        return dcc.Link(
            dmc.Tooltip(
                dmc.ActionIcon(
                    children=icon_emoji,
                    variant="filled" if is_active else "light",
                    color="blue" if is_active else "gray",
                    size="lg",
                    radius="md",
                    style={
                        "transition": "all 0.2s ease",
                        "transform": "scale(1.1)" if is_active else "scale(1)",
                        "cursor": "pointer"
                    }
                ),
                label=label,
                position="right",
                withArrow=True
            ),
            href=href,
            style={"textDecoration": "none"}
        )
    
    return dmc.Paper(
        shadow="sm",
        radius=0,
        p="md",
        style={
            "background": "#181A1B",
            "borderRight": "1px solid #23262f",
            "minHeight": "100vh",
            "width": 100,
            "display": "flex",
            "flexDirection": "column",
            "alignItems": "center",
            "paddingTop": "24px",
            "position": "fixed",
            "left": 0,
            "top": 0,
            "zIndex": 100
        },
        children=[
            # Logo/Brand area
            html.Img(
                src="/assets/trendline-icon.png",
                height="48px",
                width="48px",
                style={
                    "marginBottom": "24px",
                    "borderRadius": "8px",
                    "transition": "transform 0.2s ease",
                    "cursor": "pointer"
                }
            ),
            
            dmc.Stack(
                spacing="lg",
                align="center",
                children=[
                    create_nav_icon("🏠", "/", "Dashboard", active_page == "dashboard"),
                    create_nav_icon("👥", "/clients", "Clients", active_page == "clients"),
                    create_nav_icon("💼", "/projects", "Projects", active_page == "projects"),
                    create_nav_icon("🗄️", "/assets", "Assets", active_page == "assets"),
                    create_nav_icon("⚙️", "/admin", "Admin", active_page == "admin"),
                ]
            ),
            
            # Bottom section
            html.Div(
                style={"marginTop": "auto", "marginBottom": "20px"},
                children=[
                    dmc.ThemeIcon(
                        children="❓",
                        variant="light",
                        color="gray",
                        size="md",
                        radius="md"
                    )
                ]
            )
        ]
    )

def create_modern_topbar():
    """Create the modern topbar with search and user info"""
    return dmc.Header(
        height=80,
        px="xl",
        style={
            "background": "linear-gradient(135deg, #23262f 0%, #2a2d36 100%)",
            "borderBottom": "1px solid #3a3d46",
            "marginLeft": "90px"
        },
        children=[
            dmc.Group(
                position="apart",
                align="center",
                style={"height": "100%"},
                children=[
                    dmc.Text(
                        "Met ETL Management Dashboard",
                        weight=700,
                        size="xl",
                        color="gray.0",
                        style={"letterSpacing": "0.02em"}
                    ),
                    dmc.Group(
                        spacing="md",
                        children=[
                            dmc.TextInput(
                                placeholder="Search assets, projects, clients...",
                                radius="md",
                                size="md",
                                style={
                                    "width": 320,
                                    "background": "#181A1B"
                                },
                                styles={
                                    "input": {
                                        "backgroundColor": "#181A1B",
                                        "borderColor": "#3a3d46",
                                        "color": "#F5F5F5"
                                    }
                                }
                            ),
                            dmc.Menu(
                                id="notification-menu",
                                position="bottom-end",
                                shadow="md",
                                withArrow=True,
                                trigger="click",
                                children=[
                                    dmc.MenuTarget(
                                        dmc.ActionIcon(
                                            id="notification-bell",
                                            children=[
                                                dmc.ThemeIcon(
                                                    children="🔔",
                                                    variant="light",
                                                    color="gray",
                                                    size="lg",
                                                    radius="md"
                                                ),
                                                dmc.Badge(
                                                    id="notification-badge",
                                                    children="0",
                                                    color="green",
                                                    size="xs",
                                                    variant="filled",
                                                    style={"position": "absolute", "top": 2, "right": 2, "pointerEvents": "none", "zIndex": 10, "fontSize": 10, "padding": "0 4px"}
                                                )
                                            ],
                                            variant="subtle",
                                            size="lg",
                                            style={"position": "relative"}
                                        )
                                    ),
                                    dmc.MenuDropdown(
                                        dmc.Stack(
                                            id="notification-log-list",
                                            spacing="xs",
                                            style={"minWidth": 260, "maxHeight": 320, "overflowY": "auto", "padding": 8}
                                        )
                                    )
                                ]
                            ),
                            dmc.Avatar(
                                radius="xl",
                                color="blue",
                                size="md",
                                style={"cursor": "pointer"}
                            )
                        ]
                    )
                ]
            )
        ]
    )

def create_main_dashboard_content():
    """Create the main dashboard analytics content"""
    
    # Sample data for the main dashboard
    df_performance = pd.DataFrame({
        'Date': pd.date_range('2024-01-01', periods=30, freq='D'),
        'Assets_Online': [85, 87, 86, 88, 89, 87, 90, 88, 89, 91, 90, 92, 91, 89, 90, 
                         88, 89, 91, 92, 90, 89, 91, 93, 92, 90, 89, 91, 92, 94, 93],
        'Data_Quality': [94, 95, 93, 96, 97, 95, 98, 96, 97, 98, 97, 99, 98, 96, 97,
                        95, 96, 98, 99, 97, 96, 98, 99, 98, 97, 96, 98, 99, 99, 98]
    })
    
    performance_chart = dcc.Graph(
        figure=px.line(
            df_performance, x='Date', y=['Assets_Online', 'Data_Quality'],
            title="System Performance Trends",
            labels={'value': 'Percentage', 'variable': 'Metric'}
        ).update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_color='white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        ).update_traces(
            line=dict(width=3)
        ),
        config={'displayModeBar': False},
        style={'height': '300px'}
    )
    
    return dmc.Container(
        fluid=True,
        px=0,
        children=[
            # Main analytics grid from original design
            dmc.Grid(
                gutter="xl",
                children=[
                    dmc.Col(
                        span=9,
                        children=[
                            dmc.Paper(
                                radius="md",
                                p="xl",
                                style={
                                    "background": "linear-gradient(135deg, #23262f 0%, #2a2d36 100%)",
                                    "border": "1px solid #3a3d46"
                                },
                                children=[
                                    dmc.Group(
                                        position="apart",
                                        mb="lg",
                                        children=[
                                            dmc.Stack(
                                                spacing="xs",
                                                children=[
                                                    dmc.Text("Executive Overview", weight=700, size="xl", color="gray.0"),
                                                    dmc.Text("Real-time insights into your asset portfolio", size="sm", color="gray.5"),
                                                ]
                                            ),
                                            dmc.Badge("Live", color="green", variant="dot")
                                        ]
                                    ),
                                    
                                    # KPI Cards
                                    dmc.Grid(
                                        gutter="md",
                                        mb="xl",
                                        children=[
                                            dmc.Col(
                                                dmc.Paper(
                                                    p="md",
                                                    radius="md",
                                                    style={
                                                        "background": "linear-gradient(135deg, #4CAF50 0%, #45a049 100%)",
                                                        "color": "white",
                                                        "textAlign": "center"
                                                    },
                                                    children=[
                                                        dmc.Text("Total Assets", size="sm", weight=500),
                                                        dmc.Text("88", size="2rem", weight=700),
                                                        dmc.Text("+12% vs last month", size="xs")
                                                    ]
                                                ),
                                                span=3
                                            ),
                                            dmc.Col(
                                                dmc.Paper(
                                                    p="md",
                                                    radius="md",
                                                    style={
                                                        "background": "linear-gradient(135deg, #2196F3 0%, #1976D2 100%)",
                                                        "color": "white",
                                                        "textAlign": "center"
                                                    },
                                                    children=[
                                                        dmc.Text("Active Projects", size="sm", weight=500),
                                                        dmc.Text("24", size="2rem", weight=700),
                                                        dmc.Text("+8% vs last month", size="xs")
                                                    ]
                                                ),
                                                span=3
                                            ),
                                            dmc.Col(
                                                dmc.Paper(
                                                    p="md",
                                                    radius="md",
                                                    style={
                                                        "background": "linear-gradient(135deg, #FF9800 0%, #F57C00 100%)",
                                                        "color": "white",
                                                        "textAlign": "center"
                                                    },
                                                    children=[
                                                        dmc.Text("Data Points", size="sm", weight=500),
                                                        dmc.Text("2.4M", size="2rem", weight=700),
                                                        dmc.Text("+15% vs last month", size="xs")
                                                    ]
                                                ),
                                                span=3
                                            ),
                                            dmc.Col(
                                                dmc.Paper(
                                                    p="md",
                                                    radius="md",
                                                    style={
                                                        "background": "linear-gradient(135deg, #9C27B0 0%, #7B1FA2 100%)",
                                                        "color": "white",
                                                        "textAlign": "center"
                                                    },
                                                    children=[
                                                        dmc.Text("Uptime", size="sm", weight=500),
                                                        dmc.Text("99.2%", size="2rem", weight=700),
                                                        dmc.Text("+0.3% vs last month", size="xs")
                                                    ]
                                                ),
                                                span=3
                                            ),
                                        ]
                                    ),
                                    
                                    # Performance Chart
                                    dmc.Paper(
                                        p="md",
                                        radius="md",
                                        style={"background": "#181A1B"},
                                        children=[performance_chart]
                                    ),
                                ]
                            ),
                            
                            dmc.Space(h="xl"),
                            
                            # Secondary metrics
                            dmc.Grid(
                                gutter="md",
                                children=[
                                    dmc.Col(
                                        dmc.Paper(
                                            p="lg",
                                            radius="md",
                                            style={"background": "#23262f", "border": "1px solid #3a3d46"},
                                            children=[
                                                dmc.Text("Recent Deployments", weight=600, size="lg", color="gray.0", mb="md"),
                                                dmc.Stack(
                                                    spacing="sm",
                                                    children=[
                                                        dmc.Group(
                                                            position="apart",
                                                            children=[
                                                                dmc.Text("MET-0779 • Site Alpha", size="sm", color="white"),
                                                                dmc.Badge("Deployed", color="green", size="sm")
                                                            ]
                                                        ),
                                                        dmc.Group(
                                                            position="apart",
                                                            children=[
                                                                dmc.Text("LDR-1168 • Site Beta", size="sm", color="white"),
                                                                dmc.Badge("Testing", color="yellow", size="sm")
                                                            ]
                                                        ),
                                                        dmc.Group(
                                                            position="apart",
                                                            children=[
                                                                dmc.Text("SDR-2234 • Site Gamma", size="sm", color="white"),
                                                                dmc.Badge("Planned", color="blue", size="sm")
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
                                            p="lg",
                                            radius="md",
                                            style={"background": "#23262f", "border": "1px solid #3a3d46"},
                                            children=[
                                                dmc.Text("Data Processing", weight=600, size="lg", color="gray.0", mb="md"),
                                                dmc.Stack(
                                                    spacing="md",
                                                    children=[
                                                        dmc.Group(
                                                            position="apart",
                                                            children=[
                                                                dmc.Text("Files Processed Today", size="sm", color="white"),
                                                                dmc.Text("1,247", size="sm", weight=600, color="green")
                                                            ]
                                                        ),
                                                        dmc.Group(
                                                            position="apart",
                                                            children=[
                                                                dmc.Text("Processing Queue", size="sm", color="white"),
                                                                dmc.Text("23", size="sm", weight=600, color="blue")
                                                            ]
                                                        ),
                                                        dmc.Group(
                                                            position="apart",
                                                            children=[
                                                                dmc.Text("Failed Processes", size="sm", color="white"),
                                                                dmc.Text("2", size="sm", weight=600, color="red")
                                                            ]
                                                        ),
                                                    ]
                                                )
                                            ]
                                        ),
                                        span=6
                                    ),
                                ]
                            ),
                        ]
                    ),
                    dmc.Col(
                        span=3,
                        children=[
                            dmc.Paper(
                                radius="md",
                                p="lg",
                                style={"background": "#23262f", "border": "1px solid #3a3d46"},
                                children=[
                                    dmc.Text("System Health", weight=600, size="lg", color="gray.0", mb="md"),
                                    
                                    # System status indicators
                                    dmc.Stack(
                                        spacing="md",
                                        children=[
                                            dmc.Group(
                                                position="apart",
                                                children=[
                                                    dmc.Text("API Services", size="sm", color="white"),
                                                    dmc.Badge("Operational", color="green", size="sm")
                                                ]
                                            ),
                                            dmc.Group(
                                                position="apart",
                                                children=[
                                                    dmc.Text("Database", size="sm", color="white"),
                                                    dmc.Badge("Operational", color="green", size="sm")
                                                ]
                                            ),
                                            dmc.Group(
                                                position="apart",
                                                children=[
                                                    dmc.Text("Email Processing", size="sm", color="white"),
                                                    dmc.Badge("Operational", color="green", size="sm")
                                                ]
                                            ),
                                            dmc.Group(
                                                position="apart",
                                                children=[
                                                    dmc.Text("File Storage", size="sm", color="white"),
                                                    dmc.Badge("Warning", color="yellow", size="sm")
                                                ]
                                            ),
                                        ]
                                    ),
                                    
                                    dmc.Divider(my="md"),
                                    
                                    dmc.Text("Quick Actions", weight=500, size="md", color="gray.3", mb="sm"),
                                    dmc.Stack(
                                        spacing="xs",
                                        children=[
                                            dmc.Button("System Backup", variant="light", size="sm", fullWidth=True),
                                            dmc.Button("Generate Report", variant="light", size="sm", fullWidth=True),
                                            dmc.Button("View Logs", variant="light", size="sm", fullWidth=True),
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

# Notification badge and log callbacks
@callback(
    Output("notification-badge", "children"),
    Output("notification-badge", "style"),
    Input("notification-log-store", "data"),
)
def update_notification_badge(log):
    count = len(log) if log else 0
    style = {
        "position": "absolute", "top": 2, "right": 2, "pointerEvents": "none", "zIndex": 10, "fontSize": 10, "padding": "0 4px"
    }
    if count == 0:
        style["display"] = "none"
    else:
        style["display"] = "inline-block"
    return str(count), style

@callback(
    Output("notification-log-list", "children"),
    Input("notification-log-store", "data"),
)
def update_notification_log_list(log):
    if not log:
        return [dmc.Text("No notifications yet.", color="gray", size="sm")]
    items = []
    for n in reversed(log[-20:]):  # Show last 20 notifications, newest first
        color = {"success": "green", "warning": "yellow", "error": "red"}.get(n.get("type"), "gray")
        items.append(
            dmc.Paper(
                p="xs",
                radius="md",
                style={"background": "#23262f", "marginBottom": 4},
                children=[
                    dmc.Text(n.get("message", ""), color=color, size="sm"),
                    dmc.Text(n.get("timestamp", ""), color="gray", size="xs"),
                ]
            )
        )
    return items

# No need for popover toggle callback with dmc.Menu; it handles open/close automatically.

def dashboard_layout(show_sidebar=True, active_page="dashboard"):
    """Main dashboard layout function"""
    return html.Div(
        style={"display": "flex", "height": "100vh", "background": "#181A1B"},
        children=[
            create_navigation_sidebar(active_page),
            html.Div(
                style={"flex": 1, "display": "flex", "flexDirection": "column"},
                children=[
                    create_modern_topbar(),
                    dmc.ScrollArea(
                        create_main_dashboard_content(),
                        style={"flex": 1, "padding": "20px", "marginLeft": "100px"}
                    )
                ]
            )
        ]
    )
