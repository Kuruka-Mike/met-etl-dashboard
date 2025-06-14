"""
Step 3: Location Configuration (Modular)
- Latitude input
- Longitude input
- Elevation input
- Final submission to tbl_project_asset_detail
"""

import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State
from DBcontroller import DBcontoller
import pandas as pd
import os
from dotenv import load_dotenv
import plotly.graph_objects as go

load_dotenv() # Load environment variables
MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY")

dbc_instance = DBcontoller()

def create_step3_layout():
    """Create the layout for Step 3: Location Details"""
    return dmc.Stack(
        spacing="md",
        children=[
            dmc.Alert(
                "Project asset configured successfully! Now add location details.",
                title="Step 2 Complete",
                color="green",
                id="step3-success-alert",
                style={"display": "none"}
            ),
            dmc.Text(
                "Enter the geographic location and elevation for this asset. The map will update as you type.",
                size="sm", # Smaller text
                color="dimmed",
                mb="lg" # More bottom margin
            ),
            dmc.Grid(
                gutter="xl",
                children=[
                    dmc.Col( # Inputs Column - on the left
                        span=7,
                        children=[
                            dmc.Stack(
                                spacing="lg",
                                children=[
                                    dmc.NumberInput(
                                        label="Latitude",
                                        id="step3-latitude-input",
                                        placeholder="e.g., 40.7128",
                                        precision=6,
                                        step=0.000001,
                                        min=-90,
                                        max=90,
                                        required=True,
                                        style={"width": "100%"}
                                    ),
                                    dmc.NumberInput(
                                        label="Longitude",
                                        id="step3-longitude-input",
                                        placeholder="e.g., -74.0060",
                                        precision=6,
                                        step=0.000001,
                                        min=-180,
                                        max=180,
                                        required=True,
                                        style={"width": "100%"}
                                    ),
                                    dmc.NumberInput(
                                        label="Elevation (m)",
                                        id="step3-elevation-input",
                                        placeholder="e.g., 100",
                                        precision=2,
                                        step=0.01,
                                        min=-500,
                                        max=10000,
                                        required=True,
                                        style={"width": "100%"}
                                    )
                                ]
                            )
                        ]
                    ),
                    dmc.Col( # Map Column - on the right
                        span=5,
                        children=[
                            dmc.Paper(
                                shadow="sm",
                                p="md",
                                radius="md",
                                withBorder=True,
                                # Attempt to match height of 3 stacked inputs + spacing.
                                # Approx height of NumberInput is ~70-80px with label.
                                # 3 * 80px + 2 * lg_spacing (1.5rem ~ 24px) = 240 + 48 = ~288px.
                                # Let's use a fixed height that should be close.
                                style={"height": "290px", "background": "#1A1B1E"},
                                children=[
                                    dcc.Graph(
                                        id="step3-mapbox-map",
                                        style={"height": "100%", "width": "100%"},
                                        config={'displayModeBar': False}, # Hide mode bar for cleaner look
                                        figure=go.Figure(
                                            layout=go.Layout(
                                                mapbox_style="dark",
                                                mapbox_accesstoken=MAPBOX_API_KEY,
                                                mapbox_center={"lat": 39.8283, "lon": -98.5795}, # US Center
                                                mapbox_zoom=3,
                                                margin={"r":0,"t":0,"l":0,"b":0},
                                                paper_bgcolor="#1A1B1E",
                                                annotations=[dict(text="Mapbox API Key Missing. Please check .env file.", showarrow=False, font=dict(color="white"))] if MAPBOX_API_KEY is None else []
                                            )
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

# Callback to update Mapbox map based on Lat/Lon input
@callback(
    Output("step3-mapbox-map", "figure"),
    [Input("step3-latitude-input", "value"),
     Input("step3-longitude-input", "value")],
    [State("step3-mapbox-map", "figure")] # Keep existing figure state for smooth updates
)
def update_map_on_lat_lon_change(latitude, longitude, current_figure):
    if MAPBOX_API_KEY is None:
        # Return a placeholder or error message if API key is missing
        current_figure['layout']['annotations'] = [dict(text="Mapbox API Key Missing", showarrow=False)]
        return current_figure

    # Default view if lat or lon is not provided or invalid
    map_center_lat = 39.8283  # US Center
    map_center_lon = -98.5795
    map_zoom = 3
    markers = []

    if latitude is not None and longitude is not None:
        try:
            lat_val = float(latitude)
            lon_val = float(longitude)
            if -90 <= lat_val <= 90 and -180 <= lon_val <= 180:
                map_center_lat = lat_val
                map_center_lon = lon_val
                map_zoom = 10  # Zoom in when coordinates are valid
                markers = [go.Scattermapbox(
                    lat=[lat_val],
                    lon=[lon_val],
                    mode='markers',
                    marker=go.scattermapbox.Marker(
                        size=14,
                        color='red' 
                    ),
                    text=['Asset Location'],
                    hoverinfo='text'
                )]
        except ValueError:
            pass # Keep default view if conversion fails

    layout = go.Layout(
        mapbox_style="dark",
        mapbox_accesstoken=MAPBOX_API_KEY,
        mapbox_center={"lat": map_center_lat, "lon": map_center_lon},
        mapbox_zoom=map_zoom,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor="#1A1B1E", # Match paper background
        uirevision=' giữ nguyên ' # Preserve UI state like zoom on update
    )
    
    return {"data": markers, "layout": layout}

def validate_step3_data(latitude, longitude, elevation):
    if latitude is None or longitude is None or elevation is None:
        return False, "All location fields are required."
    if not (-90 <= latitude <= 90):
        return False, "Latitude must be between -90 and 90 degrees."
    if not (-180 <= longitude <= 180):
        return False, "Longitude must be between -180 and 180 degrees."
    if not (-500 <= elevation <= 10000):
        return False, "Elevation must be between -500 and 10,000 meters."
    return True, "Valid"

def process_step3_completion(latitude, longitude, elevation, step_data, asset_info):
    try:
        project_asset_id = step_data.get("project_asset_id")
        if not project_asset_id:
            raise ValueError("ProjectAssetID is missing from step data")
        success_count = 0
        if dbc_instance.add_project_asset_detail(project_asset_id, "Latitude", str(latitude)):
            success_count += 1
        if dbc_instance.add_project_asset_detail(project_asset_id, "Longitude", str(longitude)):
            success_count += 1
        if dbc_instance.add_project_asset_detail(project_asset_id, "Elevation", str(elevation)):
            success_count += 1
        notification = {
            "title": "Asset Configuration Complete!",
            "message": f"Asset '{asset_info.get('asset_name')}' has been fully configured with location details.",
            "color": "green",
            "icon": "✅"
        }
        log_entry = {
            "type": "success",
            "message": f"Completed asset configuration for '{asset_info.get('asset_name')}' (ProjectAssetID: {project_asset_id})",
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return notification, log_entry, None
    except Exception as e:
        error_msg = f"Failed to complete asset configuration: {str(e)}"
        notification = {
            "title": "Configuration Error",
            "message": error_msg + " Please restart the asset creation process.",
            "color": "red",
            "icon": "❌"
        }
        log_entry = {
            "type": "error",
            "message": error_msg,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return notification, log_entry, error_msg
