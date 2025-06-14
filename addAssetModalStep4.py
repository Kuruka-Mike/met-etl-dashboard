"""
Step 4: Ingest Configuration (Modular)
- Defines inputs for tbl_ingest_config
"""

import dash_mantine_components as dmc
from dash import html, callback, Output, Input, State
# from DBcontroller import DBcontoller # Uncomment when DB interaction is needed
import pandas as pd

# dbc_instance = DBcontoller() # Uncomment when DB interaction is needed

def create_step4_layout():
    """Create the layout for Step 4: Ingest Configuration"""
    return dmc.Stack(
        spacing="md",
        children=[
            dmc.Alert(
                "Location details saved! Now configure ingest settings.",
                title="Step 3 Complete",
                color="green",
                id="step4-success-alert",
                style={"display": "none"} # Initially hidden
            ),
            dmc.Text(
                "Configure the data ingest parameters for this asset:",
                size="sm",
                color="dimmed",
                mb="lg"
            ),
            dmc.SimpleGrid(
                cols=2,
                spacing="lg",
                breakpoints=[{"maxWidth": "sm", "cols": 1}],
                children=[
                    dmc.TextInput(
                        label="Sender",
                        id="step4-sender-input",
                        placeholder="e.g., sender@example.com or specific identifier",
                        required=True,
                        style={"width": "100%"}
                    ),
                    dmc.TextInput(
                        label="Logger Site Number",
                        id="step4-logger-site-number-input",
                        placeholder="e.g., 12345",
                        style={"width": "100%"}
                    ),
                    dmc.TextInput(
                        label="Dropbox Path",
                        id="step4-dropbox-input",
                        placeholder="e.g., /Apps/METData/Site123/",
                        style={"width": "100%"}
                    ),
                    dmc.TextInput(
                        label="Altosphere Path",
                        id="step4-altosphere-input",
                        placeholder="e.g., /data/projects/ProjectX/Site123/",
                        style={"width": "100%"}
                    ),
                    dmc.TextInput(
                        label="Gmail Folder ID",
                        id="step4-gmail-folder-input",
                        placeholder="Gmail Label ID for email processing",
                        style={"width": "100%"}
                    ),
                    dmc.TextInput(
                        label="Email Text (for filtering)",
                        id="step4-email-text-input",
                        placeholder="Specific text in email subject or body",
                        style={"width": "100%"}
                    ),
                ]
            ),
            dmc.Space(h="md"),
            dmc.Checkbox(
                label="Show in Logger Viewer",
                id="step4-logger-viewer-checkbox",
                checked=True,
                mb="sm"
            ),
            dmc.Checkbox(
                label="Show in Email Reports",
                id="step4-email-checkbox",
                checked=True
            ),
            # Hidden input to store project_asset_id from previous steps
            html.Div(id="step4-project-asset-id-store", style={"display": "none"})
        ]
    )

def validate_step4_data(sender, dropbox_path, gmail_folder_id, email_text, logger_site_number, show_logger, show_email, altosphere_path):
    """Validate data for Step 4"""
    if not sender:
        return False, "Sender information is required."
    # Add more specific validation rules as needed
    return True, "Valid"

def process_step4_completion(sender, dropbox_path, gmail_folder_id, email_text, logger_site_number, show_logger, show_email, altosphere_path, project_asset_id):
    """Process the completion of Step 4, inserting data into tbl_ingest_config"""
    try:
        if project_asset_id is None:
            return {
                "title": "Error",
                "message": "Project Asset ID is missing. Cannot save ingest configuration.",
                "color": "red", "icon": "❌"
            }, None, "Project Asset ID missing"

        # Convert checkbox boolean to int (1 for True, 0 for False)
        show_logger_int = 1 if show_logger else 0
        show_email_int = 1 if show_email else 0
        
        # Placeholder for actual database insertion logic
        print(f"DEBUG: Attempting to save ingest config for ProjectAssetID: {project_asset_id}")
        print(f"DEBUG: Params: Sender='{sender}', Dropbox='{dropbox_path}', GmailID='{gmail_folder_id}', EmailText='{email_text}', LoggerSite='{logger_site_number}', ShowLogger={show_logger_int}, ShowEmail={show_email_int}, Altosphere='{altosphere_path}'")
        
        # --- Uncomment and implement when DBcontroller method is ready ---
        # success = dbc_instance.add_ingest_config(
        #     sender=sender,
        #     dropbox_path=dropbox_path,
        #     gmail_folder_id=gmail_folder_id,
        #     email_text=email_text,
        #     logger_site_number=logger_site_number,
        #     project_asset_id=project_asset_id,
        #     show_in_logger_viewer=show_logger_int,
        #     show_in_email=show_email_int,
        #     altosphere_path=altosphere_path
        # )
        # if not success:
        #     raise Exception("Failed to save ingest configuration to database.")
        # --- End of placeholder ---

        notification = {
            "title": "Ingest Configuration Saved!",
            "message": "Data ingest settings have been configured.",
            "color": "green",
            "icon": "✅"
        }
        log_entry = {
            "type": "success",
            "message": f"Saved ingest configuration for ProjectAssetID: {project_asset_id}",
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return notification, log_entry, None
    except Exception as e:
        error_msg = f"Failed to save ingest configuration: {str(e)}"
        notification = {
            "title": "Ingest Config Error",
            "message": error_msg,
            "color": "red",
            "icon": "❌"
        }
        log_entry = {
            "type": "error",
            "message": error_msg,
            "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return notification, log_entry, error_msg
