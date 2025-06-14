"""
New main application script for the modernized Dash app.

- Uses dash-mantine-components for modern UI
- Creates a sleek BI-style dashboard with proper routing
- Enterprise-ready architecture
- Responsive design for all screen sizes
"""

import dash
import dash_mantine_components as dmc
from dash import html, dcc, Output, Input, callback
from dashboardLayout import dashboard_layout, create_navigation_sidebar, create_modern_topbar
from newComponents import (
    create_dashboard_overview,
    create_clients_page,
    create_projects_page,
    create_assets_page,
    create_admin_page
)
import addProjectModal

# Initialize the Dash app with enterprise-ready configuration
app = dash.Dash(
    __name__,
    external_stylesheets=["/assets/style.css"],
    suppress_callback_exceptions=True,
    title="Met ETL Management Dashboard",
    update_title="Loading...",
)

# Clientside callback for Mantine notifications
app.clientside_callback(
    "window.dash_clientside.clients_notification.show",
    Output("add-asset-notification-store", "data", allow_duplicate=True),
    Input("add-asset-notification-store", "data"),
    prevent_initial_call=True
)

# Main app layout with routing
app.layout = dmc.NotificationsProvider(
    position="top-right",
    zIndex=2077,
    children=[
        dmc.MantineProvider(
            theme={
                "colorScheme": "dark",
                "primaryColor": "blue",
                "fontFamily": "Inter, sans-serif",
            },
            children=[
                dcc.Location(id="url", refresh=False),
                dcc.Store(id="notification-log-store", data=[]),
                html.Div(id="page-content")
            ]
        )
    ]
)


# Main routing callback
@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname == "/" or pathname is None:
        return dashboard_layout()
    elif pathname == "/clients":
        return html.Div(
            style={"display": "flex", "height": "100vh", "background": "#181A1B"},
            children=[
                create_navigation_sidebar("clients"),
                html.Div(
                    style={"flex": 1, "display": "flex", "flexDirection": "column"},
                    children=[
                        create_modern_topbar(),
                        dmc.ScrollArea(
                            create_clients_page(),
                            style={"flex": 1, "padding": "20px", "marginLeft": "100px"}
                        )
                    ]
                )
            ]
        )
    elif pathname == "/projects":
        return html.Div(
            style={"display": "flex", "height": "100vh", "background": "#181A1B"},
            children=[
                create_navigation_sidebar("projects"),
                html.Div(
                    style={"flex": 1, "display": "flex", "flexDirection": "column"},
                    children=[
                        create_modern_topbar(),
                        dmc.ScrollArea(
                            create_projects_page(),
                            style={"flex": 1, "padding": "20px", "marginLeft": "100px"}
                        )
                    ]
                )
            ]
        )
    elif pathname == "/assets":
        return html.Div(
            style={"display": "flex", "height": "100vh", "background": "#181A1B"},
            children=[
                create_navigation_sidebar("assets"),
                html.Div(
                    style={"flex": 1, "display": "flex", "flexDirection": "column"},
                    children=[
                        create_modern_topbar(),
                        dmc.ScrollArea(
                            create_assets_page(),
                            style={"flex": 1, "padding": "20px"}
                        )
                    ]
                )
            ]
        )
    elif pathname == "/admin":
        return html.Div([
            dashboard_layout(show_sidebar=True, active_page="admin"),
            html.Div(
                create_admin_page(),
                style={"marginLeft": "100px", "background": "#181A1B", "minHeight": "100vh"}
            )
        ])
    else:
        return dashboard_layout()

# Callbacks are registered automatically by importing the modules
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
