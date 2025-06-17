"""
Ingest Configuration Modal for Dash Mantine Dashboard

- Mantine-based modal UI for configuring data ingestion settings
- Two-column layout for better organization of form fields
- Auto-population of fields based on asset information
- All callback logic for open/close, submit, notification, and reset
"""

import re
import dash
import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State, no_update
import pandas as pd
from DBcontroller import DBcontoller

dbc_instance = DBcontoller()

def create_ingest_config_modal():
    """Mantine-styled modal for configuring data ingestion settings"""
    return dmc.Modal(
        title="Ingest Configuration",
        id="ingest-config-modal",
        size="90%",  # Much wider modal to show full paths
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
                            dmc.Badge("Step 4 of 4", color="blue", size="lg")
                        ]
                    ),
                    
                    # Description text
                    dmc.Text(
                        "Configure data ingestion settings for this asset. These settings control how data is collected and processed.",
                        size="sm",
                        c="dimmed",
                        mb="md"
                    ),
                    
                    # Two-column grid layout for form fields
                    dmc.Grid(
                        gutter="xl",
                        children=[
                            # Left column
                            dmc.GridCol(
                                span=6,
                                children=[
                                    # Sender field
                                    dmc.TextInput(
                                        label="Sender Email",
                                        description="Email address that sends data for this asset",
                                        placeholder="Enter sender email address",
                                        id="sender-input",
                                        required=True,
                                        mb="md"
                                    ),
                                    
                                    # Dropbox path field
                                    dmc.TextInput(
                                        label="Dropbox Path",
                                        description="Path where data will be stored",
                                        placeholder="/TrendLine Team Folder/Clients/...",
                                        id="dropbox-path-input",
                                        required=True,
                                        mb="md"
                                    ),
                                    
                                    # Gmail folder ID field with Generate Label button
                                    dmc.Group(
                                        gap="xs",
                                        align="flex-end",
                                        children=[
                                            dmc.TextInput(
                                                label="Gmail Folder ID",
                                                description="Label ID for Gmail organization",
                                                placeholder="Enter Gmail folder/label ID",
                                                id="gmail-folder-id-input",
                                                required=True,
                                                style={"width": "70%"},
                                            ),
                                            dmc.Button(
                                                "Generate Label",
                                                id="generate-gmail-label-btn",
                                                color="blue",
                                                variant="outline",
                                                size="xs",
                                                style={"marginBottom": "8px"}
                                            )
                                        ]
                                    ),
                                    
                                    # Email text field
                                    dmc.TextInput(
                                        label="Email Text",
                                        description="Text displayed in email notifications & logger viewer",
                                        placeholder="Enter display text for notifications",
                                        id="email-text-input",
                                        required=True,
                                        mb="md"
                                    ),
                                ]
                            ),
                            
                            # Right column
                            dmc.GridCol(
                                span=6,
                                children=[
                                    # Logger site number field
                                    dmc.TextInput(
                                        label="Logger Site Number",
                                        description="Unique identifier for the logger site",
                                        placeholder="e.g., 000686",
                                        id="logger-site-number-input",
                                        required=True,
                                        mb="md"
                                    ),
                                    
                                    # Project asset ID (read-only)
                                    dmc.TextInput(
                                        label="Project Asset ID",
                                        description="System-assigned ID (read-only)",
                                        id="ingest-project-asset-id-input",
                                        readOnly=True,
                                        mb="md"
                                    ),
                                    
                                    # Toggle switches using Mantine Switch component
                                    dmc.Switch(
                                        id="show-in-logger-switch",
                                        label="Show in Logger Viewer",
                                        description="Enable to display in logger viewer",
                                        checked=True,
                                        size="md",
                                        onLabel="ON",
                                        offLabel="OFF",
                                        mb="md"
                                    ),
                                    
                                    dmc.Switch(
                                        id="show-in-email-switch",
                                        label="Show in Email",
                                        description="Enable to include in email notifications",
                                        checked=True,
                                        size="md",
                                        onLabel="ON",
                                        offLabel="OFF",
                                        mb="md"
                                    ),
                                    
                                    # Altosphere path field
                                    dmc.TextInput(
                                        label="Altosphere Path",
                                        description="Optional path for Altosphere integration",
                                        id="altosphere-path-input",
                                        mb="md"
                                    ),
                                ]
                            )
                        ]
                    ),
                    
                    # Action buttons
                    dmc.Group(
                        justify="flex-end",
                        mt="md",
                        children=[
                            dmc.Button(
                                "Back",
                                id="back-to-coordinates-btn-from-ingest",
                                variant="outline",
                                color="gray"
                            ),
                            dmc.Button(
                                "Complete",
                                id="complete-asset-config-btn",
                                color="green"
                            )
                        ]
                    )
                ]
            ),
            dcc.Store(id="ingest-config-notification-store"),
        ]
    )

# Helper functions for auto-population
def extract_logger_number(asset_name):
    """Extract logger site number from asset name"""
    if not asset_name:
        return ""
        
    if "MET" in asset_name.upper():
        # For MET towers: Extract digits after "MET" and pad with leading zeros
        match = re.search(r'MET\s*(\d+)', asset_name, re.IGNORECASE)
        if match:
            # Extract digits and ensure it's 6 digits with leading zeros
            digits = match.group(1)
            return f"00{digits}"[-6:]  # Pad with zeros and take last 6 digits
    elif "ZX" in asset_name.upper():
        # For Lidar: Extract digits after hyphen (e.g., ZX333-9876 → 009876)
        match = re.search(r'ZX\d+-(\d+)', asset_name, re.IGNORECASE)
        if match:
            # Extract digits after hyphen and pad with leading zeros
            digits = match.group(1)
            return f"00{digits}"[-6:]  # Pad with zeros and take last 6 digits
        
        # Fallback for ZX without hyphen
        match = re.search(r'ZX(\d+)', asset_name, re.IGNORECASE)
        if match:
            digits = match.group(1)
            return f"00{digits}"[-6:]
    
    # Default fallback: try to extract any digits
    match = re.search(r'(\d+)', asset_name)
    if match:
        digits = match.group(1)
        return f"00{digits}"[-6:]
    
    return ""

def format_dropbox_path(client_name, project_name, asset_name):
    """Format dropbox path based on client, project and asset"""
    base_path = "/TrendLine Team Folder/Clients/"
    
    # Extract asset number for folder name
    asset_number = ""
    match = re.search(r'(\d+)', asset_name)
    if match:
        asset_number = match.group(1)
    
    if client_name and project_name and asset_number:
        return f"{base_path}{client_name}/{project_name}/{asset_number}/Raw Data/"
    
    return base_path

def format_email_text(client_name, asset_name):
    """Format email text based on client and asset name"""
    if not client_name or not asset_name:
        return ""
    
    # MET: ClientName + extracted number
    if "MET" in asset_name.upper():
        match = re.search(r'MET\s*(\d+)', asset_name, re.IGNORECASE)
        if match:
            return f"{client_name} {match.group(1)}"
    # Lidar: ClientName + full asset name
    elif "ZX" in asset_name.upper():
        return f"{client_name} {asset_name.strip()}"
    # Default: ClientName + asset name
    return f"{client_name} {asset_name.strip()}"

def get_default_sender(asset_name):
    """Get default sender email based on asset type"""
    # Return empty string to prompt user to enter the actual sender
    return ""

# Callback to handle modal open/close
@callback(
    Output("ingest-config-modal", "opened"),
    [Input("next-to-ingest-btn", "n_clicks"),
     Input("back-to-coordinates-btn-from-ingest", "n_clicks"),
     Input("complete-asset-config-btn", "n_clicks")],
    [State("ingest-config-modal", "opened")],
    prevent_initial_call=True
)
def toggle_ingest_config_modal(next_clicks, back_clicks, complete_clicks, is_open):
    from dash import ctx
    if ctx.triggered_id == "next-to-ingest-btn":
        return True
    elif ctx.triggered_id in ["back-to-coordinates-btn-from-ingest", "complete-asset-config-btn"]:
        return False
    return is_open

# Callback to handle back button - go back to coordinates modal
@callback(
    Output("project-asset-detail-modal", "opened", allow_duplicate=True),
    Input("back-to-coordinates-btn-from-ingest", "n_clicks"),
    prevent_initial_call=True
)
def handle_back_button(n_clicks):
    if n_clicks:
        return True
    return no_update

# Callback to load asset data when the modal is opened
@callback(
    [Output("ingest-project-asset-id-input", "value"),
     Output("sender-input", "value"),
     Output("dropbox-path-input", "value"),
     Output("gmail-folder-id-input", "value"),
     Output("email-text-input", "value"),
     Output("logger-site-number-input", "value"),
     Output("altosphere-path-input", "value")],
    [Input("ingest-config-modal", "opened")],
    [State("current-project-asset-id-store", "data")],
    prevent_initial_call=True
)
def load_ingest_config_data(is_open, project_asset_id):
    if not is_open or project_asset_id is None:
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    try:
        # Fetch the project asset data from the database
        project_asset_data = get_project_asset_data(project_asset_id)
        
        if project_asset_data:
            asset_name = project_asset_data.get("AssetName", "")
            client_name = project_asset_data.get("ClientName", "")
            project_name = project_asset_data.get("ProjectName", "")
            
            # Check if there's already an ingest config for this asset
            existing_config = get_ingest_config(project_asset_id)
            
            if existing_config:
                # Use existing config data
                return (
                    str(project_asset_id),
                    existing_config.get("sender", ""),
                    existing_config.get("dropbox_path", ""),
                    existing_config.get("gmail_folder_id", ""),
                    existing_config.get("email_text", ""),
                    existing_config.get("logger_site_number", ""),
                    existing_config.get("altosphere_path", "")
                )
            else:
                # Generate default values
                return (
                    str(project_asset_id),
                    get_default_sender(asset_name),
                    format_dropbox_path(client_name, project_name, asset_name),
                    "",  # Leave Gmail folder ID blank for user to enter
                    format_email_text(client_name, asset_name),
                    extract_logger_number(asset_name),
                    ""  # Empty altosphere path
                )
        
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update
    
    except Exception as e:
        print(f"Error loading ingest config data: {e}")
        return no_update, no_update, no_update, no_update, no_update, no_update, no_update

def get_project_asset_data(project_asset_id):
    """
    Fetch project asset data from the database using the ProjectAssetID.
    """
    if project_asset_id is None:
        return None
    
    try:
        # Query to get the project asset record with client and project info
        query = f"""
            SELECT 
                pa.ProjectAssetID, 
                pa.Name as AssetName, 
                pa.AssetTypeID,
                p.Name as ProjectName,
                c.Name as ClientName
            FROM tbl_project_asset pa
            JOIN tbl_project p ON pa.ProjectID = p.ProjectID
            JOIN tbl_client c ON p.ClientID = c.ClientID
            WHERE pa.ProjectAssetID = {project_asset_id}
        """
        
        # Execute the query
        result = dbc_instance.dal.cnn.execute(query).fetchone()
        
        if result:
            # Convert the result to a dictionary
            project_asset_data = {
                "ProjectAssetID": result.ProjectAssetID,
                "AssetName": result.AssetName,
                "AssetTypeID": result.AssetTypeID,
                "ProjectName": result.ProjectName,
                "ClientName": result.ClientName
            }
            return project_asset_data
        return None
    except Exception as e:
        print(f"Error fetching project asset data: {e}")
        return None

def get_ingest_config(project_asset_id):
    """
    Check if there's an existing ingest config for this project asset.
    """
    if project_asset_id is None:
        return None
    
    try:
        # Query to get the ingest config record
        query = f"""
            SELECT 
                config_id,
                sender,
                dropbox_path,
                gmail_folder_id,
                email_text,
                logger_site_number,
                altosphere_path,
                show_in_logger_viewer,
                show_in_email
            FROM tbl_ingest_config
            WHERE project_asset_id = {project_asset_id}
        """
        
        # Execute the query
        result = dbc_instance.dal.cnn.execute(query).fetchone()
        
        if result:
            # Convert the result to a dictionary
            config_data = {
                "config_id": result.config_id,
                "sender": result.sender,
                "dropbox_path": result.dropbox_path,
                "gmail_folder_id": result.gmail_folder_id,
                "email_text": result.email_text,
                "logger_site_number": result.logger_site_number,
                "altosphere_path": result.altosphere_path,
                "show_in_logger_viewer": result.show_in_logger_viewer,
                "show_in_email": result.show_in_email
            }
            return config_data
        return None
    except Exception as e:
        print(f"Error fetching ingest config: {e}")
        return None

# Callback to handle saving ingest config
@callback(
    [Output("ingest-config-notification-store", "data"),
     Output("assets-dashboard-refresh-trigger-new", "data", allow_duplicate=True)],
    [Input("complete-asset-config-btn", "n_clicks")],
    [State("ingest-project-asset-id-input", "value"),
     State("sender-input", "value"),
     State("dropbox-path-input", "value"),
     State("gmail-folder-id-input", "value"),
     State("email-text-input", "value"),
     State("logger-site-number-input", "value"),
     State("show-in-logger-switch", "checked"),
     State("show-in-email-switch", "checked"),
     State("altosphere-path-input", "value"),
     State("assets-dashboard-refresh-trigger-new", "data")],
    prevent_initial_call=True
)
def save_ingest_config(
    n_clicks, 
    project_asset_id, 
    sender, 
    dropbox_path, 
    gmail_folder_id, 
    email_text, 
    logger_site_number, 
    show_in_logger, 
    show_in_email, 
    altosphere_path,
    refresh_trigger
):
    if not n_clicks or not project_asset_id or not sender:
        return no_update, refresh_trigger
    
    try:
        # Convert project_asset_id to integer
        project_asset_id = int(project_asset_id)
        
        # Convert boolean values to bit (0/1)
        show_in_logger_bit = 1 if show_in_logger else 0
        show_in_email_bit = 1 if show_in_email else 0
        
        # Check if there's an existing config to update
        existing_config = get_ingest_config(project_asset_id)
        
        if existing_config:
            # Handle NULL value for altosphere_path
            altosphere_value = "NULL" if not altosphere_path else f"'{altosphere_path}'"
            
            # Update existing record
            update_query = f"""
                UPDATE tbl_ingest_config
                SET 
                    sender = '{sender}',
                    dropbox_path = '{dropbox_path or ""}',
                    gmail_folder_id = '{gmail_folder_id or ""}',
                    email_text = '{email_text or ""}',
                    logger_site_number = '{logger_site_number or ""}',
                    show_in_logger_viewer = {show_in_logger_bit},
                    show_in_email = {show_in_email_bit},
                    altosphere_path = {altosphere_value}
                WHERE config_id = {existing_config['config_id']}
            """
            
            # Execute the query
            with dbc_instance.dal.cnn.begin() as transaction:
                dbc_instance.dal.cnn.execute(update_query)
            
            message = "Ingest configuration updated successfully."
        else:
            # Handle NULL value for altosphere_path
            altosphere_value = "NULL" if not altosphere_path else f"'{altosphere_path}'"
            
            # Insert new record
            insert_query = f"""
                INSERT INTO tbl_ingest_config (
                    sender,
                    dropbox_path,
                    gmail_folder_id,
                    email_text,
                    logger_site_number,
                    project_asset_id,
                    show_in_logger_viewer,
                    show_in_email,
                    altosphere_path
                ) VALUES (
                    '{sender}',
                    '{dropbox_path or ""}',
                    '{gmail_folder_id or ""}',
                    '{email_text or ""}',
                    '{logger_site_number or ""}',
                    {project_asset_id},
                    {show_in_logger_bit},
                    {show_in_email_bit},
                    {altosphere_value}
                )
            """
            
            # Execute the query
            with dbc_instance.dal.cnn.begin() as transaction:
                dbc_instance.dal.cnn.execute(insert_query)
            
            message = "Ingest configuration saved successfully."
        
        notification = {
            "id": f"success-{pd.Timestamp.now().timestamp()}",
            "title": "Success!",
            "message": message,
            "color": "green",
            "icon": "✅"
        }
        
        return notification, (refresh_trigger or 0) + 1
    
    except Exception as e:
        print(f"Error saving ingest config: {e}")
        notification = {
            "id": f"error-{pd.Timestamp.now().timestamp()}",
            "title": "Error",
            "message": f"Failed to save ingest configuration: {str(e)}",
            "color": "red",
            "icon": "❌"
        }
        
        return notification, refresh_trigger

# Callback to show notifications
@callback(
    Output("ingest-config-notification-store", "data", allow_duplicate=True),
    Input("ingest-config-notification-store", "data"),
    prevent_initial_call=True
)
def clientside_show_ingest_config_notification(notification):
    if notification:
        return notification
    return no_update

# --- Gmail Label Generation Callback ---
from utils.gmail_utils import get_gmail_label_ids_df

@callback(
    [Output("gmail-folder-id-input", "value", allow_duplicate=True),
     Output("ingest-config-notification-store", "data", allow_duplicate=True)],
    [Input("generate-gmail-label-btn", "n_clicks")],
    [State("email-text-input", "value"),
     State("ingest-project-asset-id-input", "value")],
    prevent_initial_call=True
)
def generate_gmail_label(n_clicks, email_text, project_asset_id):
    if not n_clicks:
        return no_update, no_update

    if not email_text:
        notification = {
            "id": f"error-gmail-label-missing-{project_asset_id}",
            "title": "Missing Information",
            "message": "Email text is required to generate a Gmail label.",
            "color": "yellow",
            "icon": "⚠️"
        }
        return no_update, notification

    # Extract client name from email text (first part before the asset name/number)
    parts = email_text.split()
    if len(parts) < 2:
        notification = {
            "id": f"error-gmail-label-format-{project_asset_id}",
            "title": "Invalid Format",
            "message": "Email text should contain client name and asset identifier.",
            "color": "yellow",
            "icon": "⚠️"
        }
        return no_update, notification

    # Extract client name (everything before the last word, which is the asset identifier)
    client_name = " ".join(parts[:-1])
    asset_identifier = parts[-1]

    # Generate label candidates
    label_candidates = [
        f"{client_name}/{asset_identifier}",  # Client Test 7000/7777
        client_name,                          # Client Test 7000
    ]

    print(f"[DEBUG] Generate Label button clicked")
    print(f"[DEBUG] Email text: {email_text}")
    print(f"[DEBUG] Extracted client name: {client_name}")
    print(f"[DEBUG] Extracted asset identifier: {asset_identifier}")
    print(f"[DEBUG] Label candidates: {label_candidates}")

    # Call the Gmail label utility
    try:
        # Get all Gmail labels
        label_df = get_gmail_label_ids_df()
        
        # Set display options to show all rows
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(f"[DEBUG] All Gmail labels:\n{label_df}")
        
        # Check for exact matches first
        found_label = None
        matched_label_name = None
        
        for candidate in label_candidates:
            print(f"[DEBUG] Checking exact match for: {candidate}")
            matches = label_df[label_df.index == candidate]
            if not matches.empty:
                found_label = matches.iloc[0]['ids']
                matched_label_name = candidate
                print(f"[DEBUG] Found exact match: {found_label} for {matched_label_name}")
                break
        
        # If no exact match, try case-insensitive matching
        if not found_label:
            for candidate in label_candidates:
                print(f"[DEBUG] Checking case-insensitive match for: {candidate}")
                matches = label_df[label_df.index.str.lower() == candidate.lower()]
                if not matches.empty:
                    found_label = matches.iloc[0]['ids']
                    matched_label_name = matches.index[0]  # Use actual case from index
                    print(f"[DEBUG] Found case-insensitive match: {found_label} for {matched_label_name}")
                    break
        
        # If still no match, try partial matching (starts with client name)
        if not found_label:
            print(f"[DEBUG] Checking partial matches for client: {client_name}")
            client_matches = label_df[label_df.index.str.startswith(client_name)]
            
            if not client_matches.empty:
                print(f"[DEBUG] Found {len(client_matches)} partial matches:")
                for idx, row in client_matches.iterrows():
                    print(f"[DEBUG]   {idx}: {row['ids']}")
                
                # Use the first match
                found_label = client_matches.iloc[0]['ids']
                matched_label_name = client_matches.index[0]
                print(f"[DEBUG] Using first partial match: {found_label} for {matched_label_name}")

        if found_label:
            notification = {
                "id": f"success-gmail-label-{project_asset_id}",
                "title": "Gmail Label Found",
                "message": f"Label found: {matched_label_name}",
                "color": "green",
                "icon": "✅"
            }
            print(f"[DEBUG] Returning label: {found_label}")
            return found_label, notification
        else:
            notification = {
                "id": f"error-gmail-label-{project_asset_id}",
                "title": "Label Not Found",
                "message": f"No matching Gmail label found for '{client_name}'. Please create the folder/label in Gmail and try again.",
                "color": "yellow",
                "icon": "⚠️"
            }
            print(f"[DEBUG] No label found for client: {client_name}")
            return no_update, notification
    except Exception as e:
        notification = {
            "id": f"error-gmail-label-exception-{project_asset_id}",
            "title": "Gmail API Error",
            "message": f"Failed to fetch Gmail labels: {str(e)}",
            "color": "red",
            "icon": "❌"
        }
        print(f"[DEBUG] Exception in generate_gmail_label: {e}")
        import traceback
        traceback.print_exc()
        return no_update, notification
