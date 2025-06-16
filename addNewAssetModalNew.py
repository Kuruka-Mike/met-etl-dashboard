"""
Modern Add Asset Modal (New Version) - 4-step wizard for asset creation
Using Dash Mantine Components 2.0
"""

import dash
import dash_mantine_components as dmc
from dash import html, dcc, callback, Output, Input, State, ctx
import pandas as pd
from DBcontroller import DBcontoller
# Import Step UI and validation logic
from addAssetModalStep1 import create_step1_layout as create_asset_step1_ui
from addAssetModalStep1 import validate_step1_data as validate_asset_step1_data
from addAssetModalStep2 import create_step2_layout as create_asset_step2_ui
# from addAssetModalStep2 import validate_step2_data as validate_asset_step2_data # Import when ready for step 2 logic
from addAssetModalStep3 import create_step3_layout as create_asset_step3_ui
# from addAssetModalStep3 import validate_step3_data as validate_asset_step3_data # Import when ready for step 3 logic
from addAssetModalStep4 import create_step4_layout as create_asset_step4_ui
# from addAssetModalStep4 import validate_step4_data as validate_asset_step4_data # Import when ready for step 4 logic


dbc_instance = DBcontoller()

# create_stepX_layout() functions are now imported. Removing placeholders.

def create_add_asset_modal():
    """Multi-step asset configuration wizard using DMC 2.0 components"""
    return dmc.Modal(
        title="Asset Configuration Wizard",
        id="modern-add-asset-modal-new",
        size="50vw",
        centered=True,
        withCloseButton=True,
        # bg="#23262f",      # Removed
        # c="white",         # Removed
        overlayProps={"background_color": "rgba(0, 0, 0, 0.55)", "blur": 3},
        opened=False,
        # styles removed
        children=[
            html.Div(
                style={"position": "relative"}, 
                children=[
                    # Main wizard content
                    dmc.Stack(
                        gap="md",
                        children=[
                            dmc.Stepper(
                                id="asset-wizard-stepper-new",
                                active=0,
                                color="blue",
                                size="sm",
                                mt="md", # Added top margin
                                children=[
                                    dmc.StepperStep(
                                        label="Basic Information",
                                        description="Create the asset record",
                                        children=create_asset_step1_ui() # Use imported UI
                                    ),
                                    dmc.StepperStep(
                                        label="Project Configuration",
                                        description="Configure project asset details",
                                        children=create_asset_step2_ui() # Use imported UI
                                    ),
                                    dmc.StepperStep(
                                        label="Location Details",
                                        description="Add geographic coordinates",
                                        children=create_asset_step3_ui() # Use imported UI
                                    ),
                                    dmc.StepperStep(
                                        label="Ingest Configuration",
                                        description="Setup data ingest parameters",
                                        children=create_asset_step4_ui() # Use imported UI
                                    ),
                                    dmc.StepperCompleted(
                                        children=dmc.Text(
                                            "Asset configuration completed successfully!",
                                            ta="center",
                                            size="lg",
                                            c="green"
                                        )
                                    )
                                ]
                            ),
                            dmc.Group(
                                justify="space-between",
                                mt="xl",
                                children=[
                                    dmc.Button(
                                        "Cancel",
                                        id="modern-cancel-asset-btn-new",
                                        variant="outline",
                                        color="gray"
                                    ),
                                    dmc.Group(
                                        gap="sm",
                                        children=[
                                            dmc.Button(
                                                "Back",
                                                id="wizard-prev-btn-new",
                                                variant="default"
                                            ),
                                            dmc.Button(
                                                "Next step",
                                                id="wizard-next-btn-new",
                                                color="blue"
                                            ),
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            ),
            # Stores for state management
            dcc.Store(id="wizard-step-data-new", data={}),
            dcc.Store(id="created-asset-info-new", data={}),
        ]
    )

# Callback to load client data when modal opens
@callback(
    Output("modern-asset-client-dropdown-new", "data"),
    Input("modern-add-asset-modal-new", "opened"),
    prevent_initial_call=True
)
def load_client_data_on_modal_open(is_opened):
    if is_opened:
        try:
            print("DEBUG: Loading client data for new modal")
            clients = dbc_instance.getAllClients()
            return [{"label": c, "value": c} for c in clients]
        except Exception as e:
            print(f"Error loading client data: {e}")
            return []
    return []

# Import validation and processing functions for other steps when ready
from addAssetModalStep2 import validate_step2_data as validate_asset_step2_data
# from addAssetModalStep2 import process_step2_to_step3 # Placeholder for actual processing
from addAssetModalStep3 import validate_step3_data as validate_asset_step3_data
# from addAssetModalStep3 import process_step3_completion
from addAssetModalStep4 import validate_step4_data as validate_asset_step4_data
# from addAssetModalStep4 import process_step4_completion

# Callback to handle stepper navigation, data population, and validation
@callback(
    [   # Stepper and general outputs
        Output("asset-wizard-stepper-new", "active"),
        Output(dcc.Store(id="wizard-step-data-new"), "data", allow_duplicate=True),
        Output("notification-container", "sendNotifications", allow_duplicate=True), # For global notifications

        # Step 1 outputs
        Output("step1-alert-message-new", "children", allow_duplicate=True),
        Output("step1-alert-message-new", "hide", allow_duplicate=True),
        
        # Step 2 outputs (display fields, alerts, dropdown data)
        Output("step2-client-name-display-new", "value", allow_duplicate=True),
        Output("step2-project-dropdown-new", "data", allow_duplicate=True),
        Output("step2-project-dropdown-new", "value", allow_duplicate=True),
        Output("step2-asset-name-display-new", "value", allow_duplicate=True),
        Output("step2-asset-type-display-new", "value", allow_duplicate=True),
        Output("step2-asset-id-display-new", "value", allow_duplicate=True),
        Output("met-tower-pairing-section-new", "style", allow_duplicate=True),
        Output("step2-met-tower-dropdown-new", "data", allow_duplicate=True),
        Output("step2-success-alert-new", "hide", allow_duplicate=True),
        Output("step2-alert-message-new", "children", allow_duplicate=True),
        Output("step2-alert-message-new", "hide", allow_duplicate=True),

        # Step 3 outputs
        Output("step3-asset-name-display-new", "value", allow_duplicate=True),
        Output("step3-project-name-display-new", "value", allow_duplicate=True),
        Output("step3-success-alert-new", "hide", allow_duplicate=True),
        Output("step3-alert-message-new", "children", allow_duplicate=True),
        Output("step3-alert-message-new", "hide", allow_duplicate=True),

        # Step 4 outputs
        Output("step4-asset-name-display-new", "value", allow_duplicate=True),
        Output("step4-project-name-display-new", "value", allow_duplicate=True),
        Output("step4-success-alert-new", "hide", allow_duplicate=True),
        Output("step4-alert-message-new", "children", allow_duplicate=True),
        Output("step4-alert-message-new", "hide", allow_duplicate=True),
    ],
    [Input("wizard-next-btn-new", "n_clicks"),
     Input("wizard-prev-btn-new", "n_clicks")],
    [State("asset-wizard-stepper-new", "active"),
     State(dcc.Store(id="wizard-step-data-new"), "data"),
     # Step 1 inputs
     State("modern-asset-client-dropdown-new", "value"),
     State("modern-asset-project-dropdown-new", "value"),
     State("modern-asset-type-dropdown-new", "value"),
     State("modern-asset-name-input-new", "value"),
     # Step 2 inputs
     State("step2-project-dropdown-new", "value"), # Project selected/confirmed in step 2
     State("step2-met-tower-dropdown-new", "value"),
     # Step 3 inputs
     State("step3-latitude-input-new", "value"),
     State("step3-longitude-input-new", "value"),
     State("step3-elevation-input-new", "value"),
     # Step 4 inputs
     State("step4-sender-input-new", "value"),
     State("step4-logger-site-number-input-new", "value"),
     State("step4-dropbox-input-new", "value"),
     State("step4-altosphere-input-new", "value"),
     State("step4-gmail-folder-input-new", "value"),
     State("step4-email-text-input-new", "value"),
     State("step4-logger-viewer-checkbox-new", "checked"),
     State("step4-email-checkbox-new", "checked"),
    ],
    prevent_initial_call=True,
)
def update_stepper(
    next_clicks, prev_clicks, current_step, wizard_data,
    s1_client, s1_project, s1_asset_type, s1_asset_name,
    s2_project, s2_met_tower_pair_id,
    s3_lat, s3_lon, s3_elev,
    s4_sender, s4_logger_site, s4_dropbox, s4_altosphere, s4_gmail, s4_email_text, s4_show_logger, s4_show_email
):
    button_id = ctx.triggered_id
    wizard_data = wizard_data or {}
    
    # Initialize all outputs to no_update to avoid errors for unset outputs
    num_outputs = 26 # Count of all outputs defined
    outputs = [dash.no_update] * num_outputs
    
    # Helper to update specific output indices
    def set_output(index, value):
        outputs[index] = value

    # Default values for alerts
    set_output(3, "")    # Step 1 alert children (index 3)
    set_output(4, True)  # Step 1 alert hide (index 4)
    
    set_output(13, True) # Step 2 success alert hide (index 13)
    set_output(14, "")   # Step 2 alert children (index 14)
    set_output(15, True) # Step 2 alert hide (index 15)
    
    set_output(18, True) # Step 3 success alert hide (index 18)
    set_output(19, "")   # Step 3 alert children (index 19)
    set_output(20, True) # Step 3 alert hide (index 20)
    
    set_output(23, True) # Step 4 success alert hide (index 23)
    set_output(24, "")   # Step 4 alert children (index 24)
    set_output(25, True) # Step 4 alert hide (index 25)

    new_step = current_step

    if button_id == "wizard-next-btn-new":
        if current_step == 0: # Validate & Process Step 1
            is_valid, result_or_msg = validate_asset_step1_data(s1_client, s1_project, s1_asset_type, s1_asset_name)
            if is_valid:
                try:
                    # result_or_msg is data_dict from validation
                    asset_name = result_or_msg["asset_name"]
                    asset_type_id = int(result_or_msg["asset_type_id"])
                    
                    new_asset_id = dbc_instance.addSimpleAsset(asset_name, asset_type_id) # DB Call
                    
                    project_id = dbc_instance.getProjectIdByName(result_or_msg["project_name"], result_or_msg["client_name"])
                    if project_id is None:
                        raise ValueError(f"Project '{result_or_msg['project_name']}' not found for client '{result_or_msg['client_name']}'.")

                    wizard_data["step1_completed_data"] = {
                        "asset_id": new_asset_id,
                        "asset_name": asset_name,
                        "asset_type_id": asset_type_id,
                        "client_name": result_or_msg["client_name"],
                        "project_name": result_or_msg["project_name"],
                        "project_id": project_id
                    }
                    set_output(1, wizard_data) # Update wizard_step_data_new
                    new_step = 1
                    set_output(14, False) # Show Step 2 success alert
                    set_output(2, [{"action": "show", "id": "asset-created", "title": "Asset Record Created", "message": f"Base record for '{asset_name}' created (ID: {new_asset_id}).", "color": "green", "autoClose": 4000}])
                except Exception as e:
                    set_output(3, f"Error creating asset: {str(e)}") # step1_alert_children
                    set_output(4, False) # step1_alert_hide
                    new_step = current_step # Stay on current step
            else: # Validation failed
                set_output(3, result_or_msg) # step1_alert_children (error message)
                set_output(4, False) # step1_alert_hide
                new_step = current_step # Stay on current step
        
        elif current_step == 1: # Validate & Process Step 2
            # Placeholder for Step 2 logic (validation, DB call for tbl_project_asset, update wizard_data)
            # For now, just proceed and show success alert for next step
            # is_valid_s2, result_or_msg_s2 = validate_asset_step2_data(s2_project, wizard_data.get("step1_completed_data"))
            # if is_valid_s2:
            #    wizard_data["step2_completed_data"] = ...
            #    new_step = 2
            #    set_output(19, False) # Show Step 3 success alert
            # else:
            #    set_output(15, result_or_msg_s2) # step2_alert_children
            #    set_output(16, False) # step2_alert_hide
            new_step = 2 # TEMPORARY: auto-advance
            set_output(19, False) # Show Step 3 success alert
            
        elif current_step == 2: # Validate & Process Step 3
            # Placeholder for Step 3 logic
            new_step = 3 # TEMPORARY: auto-advance
            set_output(24, False) # Show Step 4 success alert

        elif current_step == 3: # Validate & Process Step 4 (Final data step)
            # Placeholder for Step 4 logic
            new_step = 4 # Go to "Completed" view
            # Potentially show a final success notification here
            set_output(2, [{"action": "show", "id": "wizard-complete", "title": "Wizard Complete!", "message": "Asset configuration finished.", "color": "blue", "autoClose": 4000}])
        
        set_output(0, new_step) # Update stepper active index

    elif button_id == "wizard-prev-btn-new":
        new_step = max(current_step - 1, 0)
        set_output(0, new_step)
        # Clear any error messages from the step we are moving back to, or from current step
        if new_step == 0: # Moving back to step 1
            set_output(3, ""); set_output(4, True) # Clear step 1 alert
        if current_step == 1: # Was on step 2, moving back
             set_output(15, ""); set_output(16, True) # Clear step 2 alert
        # Add similar for other steps if needed

    # Populate display fields for the new_step (or current_step if not changed)
    # This part runs regardless of whether next/prev was clicked, to update displays if step changed
    active_display_step = new_step if outputs[0] != dash.no_update else current_step

    if active_display_step == 1 and wizard_data.get("step1_completed_data"): # Populate Step 2 displays
        s1_data = wizard_data["step1_completed_data"]
        set_output(5, s1_data.get("client_name", "")) # step2_client_name_display
        # TODO: Populate step2_project_dropdown_new data and value
        # For now, just set the value from step1. Data population needs another callback or more complex logic here.
        set_output(7, s1_data.get("project_name", "")) # step2_project_dropdown_value
        set_output(8, s1_data.get("asset_name", ""))   # step2_asset_name_display
        asset_type_map = {"1": "Development Met Tower", "2": "Lidar", "3": "Sodar"} # Assuming this mapping
        set_output(9, asset_type_map.get(str(s1_data.get("asset_type_id","")),"")) # step2_asset_type_display
        set_output(10, str(s1_data.get("asset_id", ""))) # step2_asset_id_display
        
        # Conditional visibility for met tower pairing
        if str(s1_data.get("asset_type_id","")) in ["2", "3"]: # Lidar or Sodar
            set_output(11, {}) # met_tower_pairing_section style (visible)
            # TODO: Populate step2_met_tower_dropdown_new data
        else:
            set_output(11, {"display": "none"})

    elif active_display_step == 2 and wizard_data.get("step2_completed_data"): # Populate Step 3 displays
        s1_data = wizard_data.get("step1_completed_data", {})
        # s2_data = wizard_data.get("step2_completed_data", {}) # When step 2 logic is added
        set_output(17, s1_data.get("asset_name", "")) # step3_asset_name_display
        set_output(18, s1_data.get("project_name", "")) # step3_project_name_display

    elif active_display_step == 3 and wizard_data.get("step3_completed_data"): # Populate Step 4 displays
        s1_data = wizard_data.get("step1_completed_data", {})
        # s3_data = wizard_data.get("step3_completed_data", {}) # When step 3 logic is added
        set_output(22, s1_data.get("asset_name", "")) # step4_asset_name_display
        set_output(23, s1_data.get("project_name", "")) # step4_project_name_display
        
    return outputs


# Callback to handle modal open
@callback(
    Output("modern-add-asset-modal-new", "opened"),
    Input("quick-add-asset-btn-new", "n_clicks"),
    State("modern-add-asset-modal-new", "opened"),
    prevent_initial_call=True
)
def open_asset_modal(add_clicks, is_open):
    if add_clicks:
        return True
    return is_open

# Callback to handle modal close
@callback(
    Output("modern-add-asset-modal-new", "opened", allow_duplicate=True),
    Input("modern-cancel-asset-btn-new", "n_clicks"),
    Input("wizard-next-btn-new", "n_clicks"),
    State("asset-wizard-stepper-new", "active"),
    prevent_initial_call=True
)
def close_asset_modal(cancel_clicks, next_clicks, active_step):
    from dash import ctx
    
    if ctx.triggered_id == "modern-cancel-asset-btn-new" and cancel_clicks:
        return False
    # Close modal when completing the wizard (reaching the final step)
    elif ctx.triggered_id == "wizard-next-btn-new" and next_clicks and active_step == 3:
        return False
    
    return dash.no_update
