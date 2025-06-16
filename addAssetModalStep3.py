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
        gap="md",
        children=[
            dmc.Alert(
                "Project asset configured! Now add location details.", # Slightly updated message
                title="Step 2 Complete!",
                color="green",
                id="step3-success-alert-new", # ID Updated
                hide=True, # Initially hidden, shown by callback
                withCloseButton=True
                # children="" # Removed redundant children prop
            ),
            # Context display
            dmc.SimpleGrid(
                cols=2,
                spacing="md",
                mb="md",
                children=[
                    dmc.TextInput(label="Asset Name:", id="step3-asset-name-display-new", disabled=True, style={"width": "100%"}),
                    dmc.TextInput(label="Project:", id="step3-project-name-display-new", disabled=True, style={"width": "100%"}),
                ]
            ),
            dmc.Text(
                "Enter the geographic location and elevation for this asset. The map will update as you type.",
                fz="sm", 
                c="dimmed", # This is theme-aware
                mb="lg"
            ),
            dmc.Grid(
                gutter="xl",
                children=[
                    dmc.GridCol( # Inputs Column - on the left
                        span=7,
                        children=[
                            dmc.Stack(
                                gap="lg",
                                children=[
                                    dmc.NumberInput(
                                        label="Latitude",
                                        id="step3-latitude-input-new", # ID Updated
                                        placeholder="e.g., 40.7128",
                                        decimalScale=6,
                                        step=0.000001,
                                        min=-90,
                                        max=90,
                                        required=True,
                                        style={"width": "100%"}
                                    ),
                                    dmc.NumberInput(
                                        label="Longitude",
                                        id="step3-longitude-input-new", # ID Updated
                                        placeholder="e.g., -74.0060",
                                        decimalScale=6,
                                        step=0.000001,
                                        min=-180,
                                        max=180,
                                        required=True,
                                        style={"width": "100%"}
                                    ),
                                    dmc.NumberInput(
                                        label="Elevation (m)",
                                        id="step3-elevation-input-new", # ID Updated
                                        placeholder="e.g., 100",
                                        decimalScale=2,
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
                    dmc.GridCol( # Map Column - on the right
                        span=5,
                        children=[
                            html.Div(
                                style={"position": "relative"},
                                children=[
                                    dmc.LoadingOverlay(
                                        id="step3-map-loading-overlay-new", # ID Updated
                                        visible=False,
                                        overlayProps={"blur": 2},
                                        loaderProps={"color": "blue", "variant": "bars"}
                                    ),
                                    dmc.Paper(
                                        shadow="sm",
                                        p="md",
                                        radius="md",
                                        withBorder=True,
                                        # style={"height": "290px", "background": "#1A1B1E"}, # Removed background
                                        style={"height": "290px"},
                                        children=[
                                            dcc.Graph(
                                                id="step3-mapbox-map-new", # ID Updated
                                                style={"height": "100%", "width": "100%"},
                                                config={'displayModeBar': False},
                                                figure=go.Figure(
                                                    layout=go.Layout(
                                                        mapbox_style="streets", # Default, can be themed
                                                        mapbox_accesstoken=MAPBOX_API_KEY,
                                                        mapbox_center={"lat": 39.8283, "lon": -98.5795},
                                                        mapbox_zoom=3,
                                                        margin={"r":0,"t":0,"l":0,"b":0},
                                                        # paper_bgcolor="#1A1B1E", # Let theme handle or set transparent
                                                        paper_bgcolor='rgba(0,0,0,0)', # Transparent to inherit Paper bg
                                                        plot_bgcolor='rgba(0,0,0,0)', # Transparent plot area
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
            ),
            dmc.Alert(
                id="step3-alert-message-new", # New alert for Step 3 errors
                title="Input Error!",
                color="red",
                hide=True,
                withCloseButton=True,
                children="",
                mt="md"
            )
        ]
    )

# Callback to update Mapbox map based on Lat/Lon input
@callback(
    Output("step3-mapbox-map-new", "figure"), # ID Updated
    [Input("step3-latitude-input-new", "value"), # ID Updated
     Input("step3-longitude-input-new", "value")], # ID Updated
    [State("step3-mapbox-map-new", "figure")] # ID Updated
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
                map_zoom = 7  # Zoomed out more to show roads/labels
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

    # Determine map style based on current theme (this requires a clientside callback or a trigger)
    # For now, let's default to a common light style and assume dark mode will be handled by mapbox if it supports it.
    # A more robust solution would involve passing theme to this callback or using clientside update.
    # map_style = "light-v10" # Example, can be "dark-v10", "streets-v11", etc.
    
    # The mapbox_style in go.Layout can be 'open-street-map', 'white-bg', 'carto-positron', 
    # 'carto-darkmatter', 'stamen-terrain', 'stamen-toner', 'stamen-watercolor' or a custom URL.
    # For theme-awareness, 'carto-positron' (light) and 'carto-darkmatter' (dark) are good.
    # However, changing this dynamically based on theme from a server-side callback is tricky without a page refresh or specific trigger.
    # For now, we'll keep "streets" and rely on the transparent paper_bgcolor.
    
    layout = go.Layout(
        mapbox_style="streets", 
        mapbox_accesstoken=MAPBOX_API_KEY,
        mapbox_center={"lat": map_center_lat, "lon": map_center_lon},
        mapbox_zoom=map_zoom,
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        uirevision=' giữ nguyên ' # Preserve UI state like zoom on update
    )
    # Update annotations color based on theme (this part is tricky without knowing the theme in this callback)
    # For now, if API key is missing, the annotation color is hardcoded to white.
    # This might need a clientside callback for full theme-aware annotation color.
    if MAPBOX_API_KEY is None and current_figure['layout'].get('annotations'):
        current_figure['layout']['annotations'][0]['font']['color'] = 'red' # Make it visible on light bg too
        layout['annotations'] = current_figure['layout']['annotations']

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
            "id": f"success-{pd.Timestamp.now().timestamp()}",
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
            "id": f"error-{pd.Timestamp.now().timestamp()}",
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
