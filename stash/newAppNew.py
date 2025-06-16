"""
New main application script for the modernized Dash app (New Version).

- Uses dash-mantine-components for modern UI
- Creates a sleek BI-style dashboard with proper routing
- Enterprise-ready architecture
- Responsive design for all screen sizes
"""

from dash import _dash_renderer
_dash_renderer._set_react_version("18.2.0")

import dash
import dash_mantine_components as dmc
from dash import html, dcc, Output, Input, callback
from dashboardLayout import dashboard_layout, create_navigation_sidebar, create_modern_topbar, create_main_dashboard_content
from stash.newComponentsNew import (  # Import from new components module
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
    Output("notification-container", "sendNotifications", allow_duplicate=True),
    Input("add-asset-notification-store", "data"),
    prevent_initial_call=True
)

# Main app layout with routing
app.layout = dmc.MantineProvider(
    theme={
        "colorScheme": "dark",
        "primaryColor": "blue",
        "fontFamily": "Inter, sans-serif",
    },
    children=[
        dmc.NotificationContainer(
            id="notification-container",
            position="top-right",
            zIndex=2077
        ),
        dcc.Location(id="url", refresh=False),
        dcc.Store(id="notification-log-store", data=[]),
        html.Div(id="page-content")
    ]
)


# Main routing callback
@callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname == "/clients":
        return dashboard_layout(create_clients_page(), active_page="clients")
    elif pathname == "/projects":
        return dashboard_layout(create_projects_page(), active_page="projects")
    elif pathname == "/assets":
        return dashboard_layout(create_assets_page(), active_page="assets")
    elif pathname == "/admin":
        return dashboard_layout(create_admin_page(), active_page="admin")
    else:
        return dashboard_layout(create_main_dashboard_content(), active_page="dashboard")

# Callbacks are registered automatically by importing the modules
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
