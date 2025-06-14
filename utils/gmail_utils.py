import os
import httplib2
from googleapiclient.discovery import build
from oauth2client import client
import pandas as pd

# Load environment variables if a .env file is present
# This assumes you have a .env file in the root of your project
# and that python-dotenv is installed.
# If app.py or another entry point loads .env, this might be redundant here,
# but it's good practice for a utility module that might be run independently.
from dotenv import load_dotenv
load_dotenv() # Loads variables from .env into os.environ

def get_credentials():
    client_id = os.environ.get('GMAIL_CLIENT_ID')
    client_secret = os.environ.get('GMAIL_CLIENT_SECRET')
    refresh_token = os.environ.get('GMAIL_REFRESH_TOKEN')

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("Missing one or more Gmail API credentials in environment variables (GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN)")

    credentials = client.GoogleCredentials(None,
                                           client_id,
                                           client_secret,
                                           refresh_token,
                                           None,
                                           "https://accounts.google.com/o/oauth2/token",
                                           'my-user-agent')
    return credentials

def create_gmail_service():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = build('gmail', 'v1', http=http, cache_discovery=False)
    return service

def get_gmail_label_ids_df():
    """
    Fetches all Gmail labels and returns them as a Pandas DataFrame
    sorted by a numeric key if present in the label ID.
    """
    service = create_gmail_service()
    all_labels_raw = service.users().labels().list(userId="me").execute()

    ids = []
    names = []

    if 'labels' in all_labels_raw:
        for label_dict in all_labels_raw['labels']:
            ids.append(label_dict.get('id'))
            names.append(label_dict.get('name'))
    
    if not names: # Handle case with no labels
        return pd.DataFrame(columns=['ids', 'Sort_Key'])

    label_frame = pd.DataFrame(index=names)
    label_frame['ids'] = ids
    
    # Extract numbers from each string and convert them to integers
    # Safely handle cases where 'ids' might be None or not split as expected
    sort_keys = []
    for x_id in label_frame['ids']:
        if x_id and isinstance(x_id, str):
            parts = x_id.split("_")
            if len(parts) > 1 and parts[-1].isdigit():
                sort_keys.append(float(parts[-1]))
            else:
                sort_keys.append(float('nan'))
        else:
            sort_keys.append(float('nan'))
            
    label_frame['Sort_Key'] = sort_keys
    df_sorted = label_frame.sort_values(by='Sort_Key', ascending=False)
    return df_sorted.drop(columns='Sort_Key') # Drop the helper sort key

def check_or_create_gmail_label(service, target_label_name, client_name_for_parent_check):
    """
    Checks if a Gmail label exists. If not, attempts to create it.
    Also checks if the parent label (client_name) exists.

    Args:
        service: Authorized Gmail API service instance.
        target_label_name (str): The full name of the label to check/create (e.g., "Client/TowerID").
        client_name_for_parent_check (str): The name of the parent label (client name).

    Returns:
        dict: {'status': 'found'/'created'/'parent_not_found'/'error', 
               'label_id': 'Label_XYZ' (if found/created), 
               'label_name': 'target_label_name',
               'message': 'error message if any'}
    """
    try:
        labels_df = get_gmail_label_ids_df() # Re-fetch current labels

        # Check if parent label exists
        if client_name_for_parent_check not in labels_df.index:
            return {
                'status': 'parent_not_found',
                'label_name': target_label_name,
                'parent_label_name': client_name_for_parent_check,
                'message': f"Parent label '{client_name_for_parent_check}' does not exist."
            }
        
        parent_label_id = labels_df.loc[client_name_for_parent_check, 'ids']

        # Check if the target label exists
        if target_label_name in labels_df.index:
            label_id = labels_df.loc[target_label_name, 'ids']
            return {
                'status': 'found',
                'label_id': label_id,
                'label_name': target_label_name
            }
        else:
            # Label does not exist, create it
            # For nested labels, Gmail API usually handles creation if the parent exists.
            # The 'name' field for label creation is the full path.
            label_body = {
                'name': target_label_name,
                'labelListVisibility': 'labelShow',
                'messageListVisibility': 'show',
                # If creating nested labels under a specific parent ID is required by API version/behavior:
                # 'parentLabelId': parent_label_id # This might not be standard for 'name' based creation
            }
            created_label = service.users().labels().create(userId='me', body=label_body).execute()
            return {
                'status': 'created',
                'label_id': created_label['id'],
                'label_name': created_label['name']
            }
    except Exception as e:
        return {
            'status': 'error',
            'label_name': target_label_name,
            'message': str(e)
        }

if __name__ == '__main__':
    # Example Usage (requires .env file with credentials)
    try:
        # print("Fetching all labels...")
        # all_labels = get_gmail_label_ids_df()
        # print(all_labels)

        # print("\nChecking/Creating a test label...")
        # service = create_gmail_service()
        
        # Ensure parent 'TestClient Cline' exists first if you run this directly
        # result_parent = check_or_create_gmail_label(service, "TestClient Cline", "TestClient Cline") # Creates if not exists
        # print(f"Parent check/create result: {result_parent}")

        # if result_parent['status'] in ['found', 'created']:
        #     target_label = "TestClient Cline/TestTower001"
        #     client_name = "TestClient Cline"
        #     result_child = check_or_create_gmail_label(service, target_label, client_name)
        #     print(f"Child label '{target_label}' check/create result: {result_child}")

        pass # Comment out example usage for production
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An error occurred: {e}")
