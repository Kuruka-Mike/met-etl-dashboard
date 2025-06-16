"""
Modern Add Asset Modal - Modular 3-step wizard orchestrator
Integrates the modular step files for a complete asset creation workflow
"""

import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State, ctx
import pandas as pd
from DBcontroller import DBcontoller

# Import modular step components
from addAssetModalStep1 import create_step1_layout, validate_step1_data
from addAssetModalStep2 import create_step2_layout, validate_step2_data, process_step2_to_step3
from addAssetModalStep3 import create_step3_layout, validate_step3_data, process_step3_completion
from addAssetModalStep4 import create_step4_layout, validate_step4_data, process_step4_completion # Added Step 4

dbc_instance = DBcontoller()

def create_add_asset_modal():
    """Multi-step asset configuration wizard using modular components"""
    return dmc.Modal(
        title="Asset Configuration Wizard",
        id="modern-add-asset-modal",
        size="50vw",
        centered=True,
        overlayProps={"background_color": "rgba(0, 0, 0, 0.55)", "blur": 3},
        opened=False,
        children=[
            html.Div(
                style={"position": "relative"},
                children=[
                    # Main wizard content (no global loading overlay)
                    dmc.Stack(
                        gap="md",
                        children=[
                            dmc.Stepper(
                                id="asset-wizard-stepper",
                                active=0,
                                children=[
                                    dmc.StepperStep(
                                        label="Basic Information",
                                        description="Create the asset record",
                                        children=[create_step1_layout()]
                                    ),
                                    dmc.StepperStep(
                                        label="Project Configuration",
                                        description="Configure project asset details",
                                        children=[create_step2_layout()]
                                    ),
                                    dmc.StepperStep(
                                        label="Location Details",
                                        description="Add geographic coordinates",
                                        children=[create_step3_layout()]
                                    ),
                                    dmc.StepperStep( # New Step 4
                                        label="Ingest Configuration",
                                        description="Setup data ingest parameters",
                                        children=[create_step4_layout()]
                                    )
                                ]
                            ),
                                dmc.Group(
                                    justify="space-between",
                                    mt="xl",
                                    children=[
                                    dmc.Button(
                                        "Cancel",
                                        id="modern-cancel-asset-btn",
                                        variant="outline",
                                        color="gray"
                                    ),
                                    dmc.Group(
                                        gap="sm",
                                        children=[
                                            dmc.Button(
                                                "Previous",
                                                id="wizard-prev-btn",
                                                variant="outline",
                                                style={"display": "none"}
                                            ),
                                            dmc.Button(
                                                "Next",
                                                id="wizard-next-btn",
                                                color="blue",
                                                loading=False # This loading is for the button itself, not the overlay
                                            ),
                                            dmc.Button(
                                                "Complete",
                                                id="wizard-complete-btn",
                                                color="green",
                                                style={"display": "none"},
                                                loading=False # This loading is for the button itself
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    ) # End of main wizard Stack
                ] # End of html.Div children
            ), # End of html.Div
            # Stores are outside the LoadingOverlay
            dcc.Store(id="add-asset-notification-store"),
            dcc.Store(id="wizard-step-data", data={}),
            dcc.Store(id="created-asset-info", data={}),
        ] # End of Modal children
    ) # End of Modal

# Temporarily disabled lazy load client data callback
# @callback(
#     Output("modern-asset-client-dropdown", "data"),
#     Input("modern-add-asset-modal", "opened"),
#     prevent_initial_call=True
# )
# def load_client_data_on_modal_open(is_opened):
#     if is_opened:
#         try:
#             print("DEBUG: Loading client data for modal")
#             clients = dbc_instance.getAllClients()
#             return [{"label": c, "value": c} for c in clients]
#         except Exception as e:
#             print(f"Error loading client data: {e}")
#             return []
#     return []

# Temporarily disabled main modal control callback
# @callback(
#     [
#         Output("modern-add-asset-modal", "opened"),
#         Output("asset-wizard-stepper", "active", allow_duplicate=True),
#         Output("wizard-step-data", "data", allow_duplicate=True),
#         Output("created-asset-info", "data", allow_duplicate=True),
#         Output("add-asset-notification-store", "data", allow_duplicate=True),
#         Output("notification-log-store", "data", allow_duplicate=True),
#         Output("assets-dashboard-refresh-trigger-new", "data", allow_duplicate=True),
#     ],
#     [
#         Input("quick-add-asset-btn-new", "n_clicks"),
#         Input("modern-cancel-asset-btn", "n_clicks"),
#         Input("wizard-complete-btn", "n_clicks")
#     ],
#     [
#         State("modern-add-asset-modal", "opened"),
#         # Step 3 inputs (used if completing from Step 3, though now Step 4 is final)
#         # State("step3-latitude-input", "value"),
#         # State("step3-longitude-input", "value"),
#         # State("step3-elevation-input", "value"),
#         # Step 4 inputs
#         State("step4-sender-input", "value"),
#         State("step4-dropbox-input", "value"),
#         State("step4-gmail-folder-input", "value"),
#         State("step4-email-text-input", "value"),
#         State("step4-logger-site-number-input", "value"),
#         State("step4-logger-viewer-checkbox", "checked"),
#         State("step4-email-checkbox", "checked"),
#         State("step4-altosphere-input", "value"),
#         State("wizard-step-data", "data"),
#         State("created-asset-info", "data"),
#         State("notification-log-store", "data"),
#         State("assets-dashboard-refresh-trigger-new", "data"),
#         State("asset-wizard-stepper", "active") # To know which step we are completing from
#     ],
#     prevent_initial_call=True
# )
# def toggle_add_asset_modal(
#     open_btn, cancel_btn, complete_btn, is_open, 
#     # latitude, longitude, elevation, # Step 3 states, moved to handle_wizard_navigation
#     sender, dropbox_path, gmail_folder_id, email_text, logger_site_number, 
#     show_logger, show_email, altosphere_path, # Step 4 states
#     step_data, asset_info, log_data, refresh_trigger, current_step_on_complete):
#
#     if ctx.triggered_id == "quick-add-asset-btn-new" and open_btn and open_btn > 0:
#         print("DEBUG: Opening modal, resetting to Step 1")
#         return True, 0, {}, {}, {}, log_data or [], refresh_trigger
#
#     elif ctx.triggered_id == "wizard-complete-btn" and complete_btn:
#         print(f"DEBUG: Processing wizard completion from Step {current_step_on_complete + 1}")
#         project_asset_id = step_data.get("project_asset_id")
#         if not project_asset_id: 
#             notification = {"id": f"error-{pd.Timestamp.now().timestamp()}", "title": "Error", "message": "Project Asset ID missing. Cannot complete.", "color": "red", "icon": "❌"}
#             return is_open, current_step_on_complete, step_data, asset_info, notification, log_data or [], refresh_trigger
#
#         is_valid, error_msg = validate_step4_data(sender, dropbox_path, gmail_folder_id, email_text, logger_site_number, show_logger, show_email, altosphere_path)
#         if not is_valid:
#             notification = {"id": f"validation-error-{pd.Timestamp.now().timestamp()}", "title": "Validation Error (Step 4)", "message": error_msg, "color": "yellow", "icon": "⚠️"}
#             return is_open, 3, step_data, asset_info, notification, log_data or [], refresh_trigger
#
#         notification_out, log_entry, error = process_step4_completion(
#             sender, dropbox_path, gmail_folder_id, email_text, logger_site_number, 
#             show_logger, show_email, altosphere_path, project_asset_id
#         )
#         updated_log = (log_data or []) + [log_entry]
#
#         if error:
#             return is_open, 3, step_data, asset_info, notification_out, updated_log, refresh_trigger
#         else:
#             return False, 0, {}, {}, notification_out, updated_log, (refresh_trigger or 0) + 1
#
#     elif ctx.triggered_id == "modern-cancel-asset-btn":
#         print("DEBUG: Closing modal, resetting wizard")
#         return False, 0, {}, {}, {}, log_data or [], refresh_trigger
#
#     # Default return for other cases (e.g., modal just being present without action)
#     return is_open, current_step_on_complete if current_step_on_complete is not None else 0, step_data, asset_info, {}, log_data or [], refresh_trigger

# Temporarily disabled wizard navigation callback
# @callback(
#     [
#         Output("asset-wizard-stepper", "active"),
#         Output("wizard-prev-btn", "style"),
#         Output("wizard-next-btn", "style"),
#         Output("wizard-complete-btn", "style"),
#         Output("wizard-step-data", "data"),
#         Output("created-asset-info", "data"),
#         Output("add-asset-notification-store", "data"),
#         Output("step2-project-dropdown", "data"),
#         Output("step2-project-dropdown", "value"),
#         Output("step2-asset-name-display", "value"),
#         Output("step2-asset-type-display", "value"),
#         Output("step2-asset-id-display", "value"),
#         Output("met-tower-pairing-section", "style")
#     ],
#     [
#         Input("wizard-next-btn", "n_clicks"),
#         Input("wizard-prev-btn", "n_clicks")
#     ],
#     [
#         State("asset-wizard-stepper", "active"),
#         State("modern-asset-client-dropdown", "value"),
#         State("modern-asset-project-dropdown", "value"),
#         State("modern-asset-type-dropdown", "value"),
#         State("modern-asset-name-input", "value"),
#         State("wizard-step-data", "data"),
#         State("created-asset-info", "data"),
#         State("step2-met-tower-dropdown", "value"),
#         State("step2-project-dropdown", "value"),
#         # Add Step 3 inputs for processing when moving from Step 3 to 4
#         State("step3-latitude-input", "value"),
#         State("step3-longitude-input", "value"),
#         State("step3-elevation-input", "value")
#     ],
#     prevent_initial_call=True
# )
# def handle_wizard_navigation(
#     next_clicks, prev_clicks, current_step, 
#     client_name, project_name, asset_type_id, asset_name, 
#     step_data, asset_info, 
#     met_tower_pair_id, step2_project_name,
#     s3_latitude, s3_longitude, s3_elevation # Step 3 values
#     ):
#     print(f"DEBUG: Wizard navigation triggered. Current step: {current_step}, Triggered by: {ctx.triggered_id}")
#
#     # Show loading overlay if loading_state is True
#     loading_style_output = {"display": "none"}
#
#     if not ctx.triggered:
#         return current_step, {"display": "none"}, {}, {"display": "none"}, step_data, asset_info, {}, [], "", "", "", "", {"display": "none"}
#     
#     notification = {}
#     
#     if ctx.triggered_id == "wizard-next-btn":
#         if current_step == 0:  # Moving from Step 1 to Step 2
#             is_valid, error_msg = validate_step1_data(client_name, project_name, asset_type_id, asset_name)
#             if not is_valid:
#                 notification = {
#                     "id": f"validation-error-{pd.Timestamp.now().timestamp()}",
#                     "title": "Validation Error",
#                     "message": error_msg,
#                     "color": "yellow",
#                     "icon": "⚠️"
#                 }
#                 return current_step, {"display": "none"}, {}, {"display": "none"}, step_data, asset_info, notification, [], "", "", "", "", {"display": "none"}
#             
#             try:
#                 print(f"DEBUG: Creating asset from wizard: {asset_name}, type: {asset_type_id}")
#                 new_asset_id = dbc_instance.addSimpleAsset(asset_name, int(asset_type_id))
#                 print(f"DEBUG: Asset created with ID: {new_asset_id}")
#                 
#                 asset_info = {
#                     "asset_id": new_asset_id,
#                     "asset_name": asset_name,
#                     "asset_type_id": asset_type_id,
#                     "client_name": client_name,
#                     "project_name": project_name
#                 }
#                 
#                 client_id = dbc_instance.getClientID(client_name)
#                 projects = dbc_instance.getProjects(client_id)
#                 project_options = [{"label": str(p), "value": str(p)} for p in projects] if isinstance(projects, list) else []
#                 pairing_style = {} if int(asset_type_id) in [2, 3] else {"display": "none"}
#                 next_style_conditional = {"display": "none"} if int(asset_type_id) in [2, 3] else {}
#                 
#                 new_step = 1
#                 return (
#                     new_step, {}, next_style_conditional, {"display": "none"}, step_data, asset_info, notification,
#                     project_options, project_name, asset_name, f"Asset Type {asset_type_id}", str(new_asset_id),
#                     pairing_style
#                 )
#             except Exception as e:
#                 print(f"DEBUG: Error creating asset: {e}")
#                 notification = {
#                     "id": f"error-{pd.Timestamp.now().timestamp()}",
#                     "title": "Error",
#                     "message": f"Failed to create asset: {str(e)}",
#                     "color": "red",
#                     "icon": "❌"
#                 }
#                 return current_step, {"display": "none"}, {}, {"display": "none"}, step_data, asset_info, notification, [], "", "", "", "", {"display": "none"}
#         
#         elif current_step == 1:  # Moving from Step 2 to Step 3
#             is_valid, error_msg = validate_step2_data(step2_project_name, asset_info)
#             if not is_valid:
#                 notification = {
#                     "id": f"validation-error-{pd.Timestamp.now().timestamp()}",
#                     "title": "Validation Error",
#                     "message": error_msg,
#                     "color": "yellow",
#                     "icon": "⚠️"
#                 }
#                 return current_step, {}, {}, {"display": "none"}, step_data, asset_info, notification, [], "", "", "", "", {"display": "none"}, {"display": "none"}
#             
#             project_asset_id, error = process_step2_to_step3(step2_project_name, met_tower_pair_id, asset_info)
#             if error:
#                 notification = {
#                     "id": f"error-{pd.Timestamp.now().timestamp()}",
#                     "title": "Error",
#                     "message": error,
#                     "color": "red",
#                     "icon": "❌"
#                 }
#                 return current_step, {}, {}, {"display": "none"}, step_data, asset_info, notification, [], "", "", "", "", {"display": "none"}, {"display": "none"}
#             
#             step_data["project_asset_id"] = project_asset_id
#             new_step = 2
#             return (
#                 new_step, {}, {"display": "none"}, {}, step_data, asset_info, {},
#                 [], "", "", "", "", {"display": "none"}
#             )
#         elif current_step == 2: # Moving from Step 3 to Step 4
#             print("DEBUG: Validating and processing Step 3 data before moving to Step 4.")
#             is_valid_s3, error_msg_s3 = validate_step3_data(s3_latitude, s3_longitude, s3_elevation)
#             if not is_valid_s3:
#                 notification = {"id": f"validation-error-{pd.Timestamp.now().timestamp()}", "title": "Validation Error (Step 3)", "message": error_msg_s3, "color": "yellow", "icon": "⚠️"}
#                 return current_step, {}, {}, {"display": "none"}, step_data, asset_info, notification, [], "", "", "", "", {"display": "none"}
#
#             s3_notification, _log_entry, s3_error = process_step3_completion(s3_latitude, s3_longitude, s3_elevation, step_data, asset_info)
#             
#             if s3_error:
#                 return current_step, {}, {}, {"display": "none"}, step_data, asset_info, s3_notification, [], "", "", "", "", {"display": "none"}, {"display": "none"}
#
#             notification = s3_notification 
#             new_step = 3 
#             return (
#                 new_step, {}, {"display": "none"}, {}, step_data, asset_info, notification,
#                 [], "", "", "", "", {"display": "none"}
#             )
#         else: 
#             new_step = min(current_step + 1, 3) 
#     elif ctx.triggered_id == "wizard-prev-btn":
#         new_step = max(current_step - 1, 0)
#         # loading_style_output remains {"display": "none"} for prev button
#     else: 
#         new_step = current_step
#         # loading_style_output remains {"display": "none"}
#
#     prev_style = {} if new_step > 0 else {"display": "none"}
#     if new_step == 0:
#         next_style = {}
#         complete_style = {"display": "none"}
#     elif new_step == 1:
#         asset_type_id_for_style = asset_info.get("asset_type_id") if asset_info else None
#         if asset_type_id_for_style and int(asset_type_id_for_style) in [2, 3] and not met_tower_pair_id:
#              next_style = {"display": "none"}
#         else:
#             next_style = {}
#         complete_style = {"display": "none"}
#     elif new_step == 2:
#         next_style = {}
#         complete_style = {"display": "none"} # Was {}, changed to hide on step 3 next
#     elif new_step == 3:
#         next_style = {"display": "none"}
#         complete_style = {}
#     else:
#         next_style = {}
#         complete_style = {"display": "none"}
#
#     # The variable `loading_visible` from the original code is effectively always False in this path
#     # So, loading_style_output will be {"display": "none"}
#     return new_step, prev_style, next_style, complete_style, step_data, asset_info, notification, [], "", "", "", "", {"display": "none"}

# Temporarily disabled Met Tower dropdown callback
# @callback(
#     [
#         Output("step2-met-tower-dropdown", "data"),
#         Output("wizard-next-btn", "style", allow_duplicate=True)
#     ],
#     [
#         Input("step2-project-dropdown", "value"),
#         Input("step2-met-tower-dropdown", "value")
#     ],
#     [
#         State("created-asset-info", "data"),
#         State("asset-wizard-stepper", "active")
#     ],
#     prevent_initial_call=True
# )
# def update_met_tower_dropdown_and_next_button(selected_project, met_tower_selection, asset_info, current_step):
#     if current_step != 1:  # Only active on Step 2
#         return [], {}
#     
#     met_tower_options = [{"label": "Standalone", "value": "standalone"}]
#     
#     if selected_project and asset_info:
#         try:
#             client_name = asset_info.get("client_name")
#             project_id = dbc_instance.getProjectIdByName(selected_project, client_name)
#             if project_id:
#                 met_towers = dbc_instance.getMetTowersByProjectName(selected_project, client_name)
#                 met_tower_options.extend(met_towers)
#         except Exception as e:
#             print(f"Error loading Met Towers: {e}")
#     
#     asset_type_id = asset_info.get("asset_type_id") if asset_info else None
#     if asset_type_id and int(asset_type_id) in [2, 3]:
#         next_style = {} if met_tower_selection else {"display": "none"}
#     else:
#         next_style = {}
#     
#     return met_tower_options, next_style
