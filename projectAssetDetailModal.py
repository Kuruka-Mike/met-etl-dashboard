"""
Project Asset Detail Modal for Dash Mantine Dashboard

- Mantine-based modal UI for adding asset coordinates (Latitude, Longitude, Elevation)
- All callback logic for open/close, submit, notification, and reset
- Designed for clean integration into the assets dashboard
"""

import dash
import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State, no_update
import pandas as pd
from DBcontroller import DBcontoller

dbc_instance = DBcontoller()

def create_project_asset_detail_modal():
    """Mantine-styled modal for adding asset coordinates"""
    return dmc.Modal(
        title="Asset Coordinates",
        id="project-asset-detail-modal",
        size="md",
        centered=True,
        overlayProps={"background_color": "rgba(0, 0, 0, 0.55)", "blur": 3},
        children=[
            dmc.Stack(
                gap="md",
                children=[
                    # Step indicator
                    dmc.Group(
                        justify="center",
                        mb="md",
                        children=[
                            dmc.Badge("Step 3 of 4", color="blue", size="lg")
                        ]
                    ),
                    
                    # Asset name display
                    dmc.Text(
                        "Enter coordinates for your asset:",
                        id="asset-detail-message",
                        size="md",
                        mb="md"
                    ),
                    
                    # Latitude input
                    dmc.NumberInput(
                        label="Latitude",
                        description="Enter the latitude in decimal degrees (e.g., 47.7593)",
                        placeholder="Enter latitude",
                        id="latitude-input",
                        decimalScale=8,
                        step=0.00001,
                        style={"width": "100%"}
                    ),
                    
                    # Longitude input
                    dmc.NumberInput(
                        label="Longitude",
                        description="Enter the longitude in decimal degrees (e.g., -99.1992)",
                        placeholder="Enter longitude",
                        id="longitude-input",
                        decimalScale=8,
                        step=0.00001,
                        style={"width": "100%"}
                    ),
                    
                    # Elevation input
                    dmc.NumberInput(
                        label="Elevation",
                        description="Enter the elevation in meters",
                        placeholder="Enter elevation",
                        id="elevation-input",
                        decimalScale=2,
                        step=0.1,
                        style={"width": "100%"}
                    ),
                    
                    # Hidden input to store ProjectAssetID
                    html.Div(
                        style={"display": "none"},
                        children=[
                            dmc.TextInput(id="detail-project-asset-id-input"),
                        ]
                    ),
                    
                    # Action buttons
                    dmc.Group(
                        justify="flex-end",
                        mt="md",
                        children=[
                            dmc.Button(
                                "Back",
                                id="back-to-pairing-btn",
                                variant="outline",
                                color="gray"
                            ),
                            dmc.Button(
                                "Save",
                                id="save-coordinates-btn",
                                color="blue"
                            ),
                            dmc.Button(
                                "Next",
                                id="next-to-ingest-btn",
                                color="green",
                                disabled=True
                            )
                        ]
                    )
                ]
            ),
            dcc.Store(id="coordinates-notification-store"),
        ]
    )

# Callback to handle modal open/close
@callback(
    Output("project-asset-detail-modal", "opened"),
    [Input("next-to-coordinates-btn", "n_clicks"),
     Input("back-to-pairing-btn", "n_clicks"),
     Input("next-to-ingest-btn", "n_clicks")],
    [State("project-asset-detail-modal", "opened")],
    prevent_initial_call=True
)
def toggle_coordinates_modal(next_clicks, back_clicks, next_to_ingest_clicks, is_open):
    from dash import ctx
    if ctx.triggered_id == "next-to-coordinates-btn":
        return True
    elif ctx.triggered_id in ["back-to-pairing-btn", "next-to-ingest-btn"]:
        return False
    return is_open

# Callback to handle back button - go back to appropriate modal based on asset type
@callback(
    [Output("project-asset-modal", "opened", allow_duplicate=True),
     Output("add-asset-modal", "opened", allow_duplicate=True)],
    [Input("back-to-pairing-btn", "n_clicks")],
    [State("asset-type-id-input", "value")],
    prevent_initial_call=True
)
def handle_back_button(n_clicks, asset_type_id):
    if not n_clicks:
        return no_update, no_update
    
    # For Met Towers (type 1), go back to Step 1
    if asset_type_id == "1":
        return False, True
    
    # For Lidar/Sodar (type 2/3), go back to Step 2
    return True, False

# Callback to reset button states in the pairing modal when it's opened
@callback(
    [Output("save-project-asset-btn", "disabled", allow_duplicate=True),
     Output("next-to-coordinates-btn", "disabled", allow_duplicate=True)],
    [Input("project-asset-modal", "opened")],
    prevent_initial_call=True
)
def reset_pairing_button_states(is_open):
    if is_open:
        # Enable Save button, disable Next button
        return False, True
    return no_update, no_update

# Callback to load asset name when the modal is opened
@callback(
    [Output("detail-project-asset-id-input", "value"),
     Output("asset-detail-message", "children")],
    [Input("project-asset-detail-modal", "opened")],
    [State("current-project-asset-id-store", "data")],
    prevent_initial_call=True
)
def load_asset_details(is_open, project_asset_id):
    if not is_open or project_asset_id is None:
        return no_update, no_update
    
    try:
        # Fetch the project asset data from the database
        project_asset_data = get_project_asset_data(project_asset_id)
        
        if project_asset_data:
            asset_name = project_asset_data.get("AssetName", "")
            message = f"Enter coordinates for {asset_name}:"
            return str(project_asset_id), message
        
        return no_update, no_update
    
    except Exception as e:
        print(f"Error loading asset details: {e}")
        return no_update, no_update

def get_project_asset_data(project_asset_id):
    """
    Fetch project asset data from the database using the ProjectAssetID.
    """
    if project_asset_id is None:
        return None
    
    try:
        # Query to get the project asset record
        query = f"""
            SELECT 
                pa.ProjectAssetID, 
                pa.Name as AssetName
            FROM tbl_project_asset pa
            WHERE pa.ProjectAssetID = {project_asset_id}
        """
        
        # Execute the query
        result = dbc_instance.dal.cnn.execute(query).fetchone()
        
        if result:
            # Convert the result to a dictionary
            project_asset_data = {
                "ProjectAssetID": result.ProjectAssetID,
                "AssetName": result.AssetName
            }
            return project_asset_data
        return None
    except Exception as e:
        print(f"Error fetching project asset data: {e}")
        return None

# Callback to handle saving coordinates
@callback(
    [Output("latitude-input", "value"),
     Output("longitude-input", "value"),
     Output("elevation-input", "value"),
     Output("coordinates-notification-store", "data"),
     Output("assets-dashboard-refresh-trigger-new", "data", allow_duplicate=True),
     Output("save-coordinates-btn", "disabled", allow_duplicate=True),
     Output("next-to-ingest-btn", "disabled", allow_duplicate=True)],
    [Input("save-coordinates-btn", "n_clicks")],
    [State("detail-project-asset-id-input", "value"),
     State("latitude-input", "value"),
     State("longitude-input", "value"),
     State("elevation-input", "value"),
     State("assets-dashboard-refresh-trigger-new", "data")],
    prevent_initial_call=True
)
def save_coordinates(n_clicks, project_asset_id, latitude, longitude, elevation, refresh_trigger):
    if not n_clicks or not project_asset_id:
        return no_update, no_update, no_update, no_update, refresh_trigger
    
    if latitude is None or longitude is None or elevation is None:
        notification = {
            "id": f"warning-{pd.Timestamp.now().timestamp()}",
            "title": "Warning",
            "message": "Please enter values for all coordinates.",
            "color": "yellow",
            "icon": "⚠️"
        }
        return latitude, longitude, elevation, notification, refresh_trigger
    
    try:
        # Convert project_asset_id to integer
        project_asset_id = int(project_asset_id)
        
        # Insert Latitude
        insert_latitude = f"""
            INSERT INTO tbl_project_asset_detail (ProjectAssetID, property, value)
            VALUES ({project_asset_id}, 'Latitude', '{latitude:.8f}')
        """
        
        # Insert Longitude
        insert_longitude = f"""
            INSERT INTO tbl_project_asset_detail (ProjectAssetID, property, value)
            VALUES ({project_asset_id}, 'Longitude', '{longitude:.8f}')
        """
        
        # Insert Elevation
        insert_elevation = f"""
            INSERT INTO tbl_project_asset_detail (ProjectAssetID, property, value)
            VALUES ({project_asset_id}, 'Elevation', '{elevation:.2f}')
        """
        
        print(f"DEBUG: Inserting coordinates for asset {project_asset_id}")
        
        # Execute the queries using transaction context managers
        with dbc_instance.dal.cnn.begin() as transaction:
            dbc_instance.dal.cnn.execute(insert_latitude)
            dbc_instance.dal.cnn.execute(insert_longitude)
            dbc_instance.dal.cnn.execute(insert_elevation)
            print(f"DEBUG: Coordinates inserted successfully")
        
        notification = {
            "id": f"success-{pd.Timestamp.now().timestamp()}",
            "title": "Success!",
            "message": "Asset coordinates saved successfully.",
            "color": "green",
            "icon": "✅"
        }
        
        # Clear all fields and update button states
        return None, None, None, notification, (refresh_trigger or 0) + 1, True, False
    
    except Exception as e:
        print(f"Error saving coordinates: {e}")
        notification = {
            "id": f"error-{pd.Timestamp.now().timestamp()}",
            "title": "Error",
            "message": f"Failed to save coordinates: {str(e)}",
            "color": "red",
            "icon": "❌"
        }
        
        # Keep the entered values and button states
        return latitude, longitude, elevation, notification, refresh_trigger, False, True

# Callback to show notifications
@callback(
    Output("coordinates-notification-store", "data", allow_duplicate=True),
    Input("coordinates-notification-store", "data"),
    prevent_initial_call=True
)
def clientside_show_coordinates_notification(notification):
    if notification:
        return notification
    return no_update
