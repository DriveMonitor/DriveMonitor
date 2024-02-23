import argparse
import time
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from ExceptionHandler import AuthenticationError, DriveAPIError


class Drive:
    def __init__(self, credentials_file, interval, token_file="token.json", scope=None):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.scope = scope if scope is not None else ['https://www.googleapis.com/auth/drive']
        self.creds = self.get_credentials()
        self.service = self.build_service()
        self.interval = interval

    def get_credentials(self): #Fetches or refreshes Google Drive API credentials
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, self.scope)
        else:
            creds = None

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    raise AuthenticationError(f"Error refreshing credentials: {e}")
            else:
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.scope)
                    creds = flow.run_local_server(port=0)
                    with open(self.token_file, "w") as token:
                        token.write(creds.to_json())
                except Exception as e:
                    raise AuthenticationError(f"Error obtaining credentials: {e}")
        return creds

    def build_service(self):
        try:
            return build("drive", "v3", credentials=self.creds)
        except Exception as e:
            raise DriveAPIError(f"Failed to build Drive service: {e}")

    def list_files(self, page_size=10): #Lists files stored in Google Drive
        results = self.service.files().list(
            pageSize=page_size, fields="nextPageToken, files(id, parents, mimeType, trashed)",
            q="'me' in owners").execute()
        return results.get('files', [])

    def get_parent_folder_id(self, file_id): #Retrieves the immediate parent folder ID of a given file
        file = self.service.files().get(fileId=file_id, fields='parents').execute()
        if 'parents' in file:
            return file['parents'][0]
        return

    def is_folder_public(self, folder_id): #Checks if a specified folder is public
        permissions = self.service.permissions().list(fileId=folder_id, fields="permissions(id, type)").execute()
        for permission in permissions.get('permissions', []):
            if permission['type'] == 'anyone':
                return True
        return False

    def get_full_path(self, file_id): #Determines the full path of a file from its ID
        path_components = []
        current_id = file_id
        while True:
            file = self.service.files().get(fileId=current_id, fields='name, parents').execute()
            path_components.append(file['name'])
            if 'parents' in file:
                current_id = file['parents'][0]  # Assuming single parent
            else:
                break
        return '/'.join(reversed(path_components))

    def update_file_permission_to_private(self, file_id): #Updates a file's permission to private if it is public
        permissions = self.service.permissions().list(fileId=file_id, fields="permissions(id, type)").execute()
        for permission in permissions.get('permissions', []):
            if permission['type'] == 'anyone':
                self.service.permissions().delete(fileId=file_id, permissionId=permission['id']).execute()
                return "Was public, changed to private"
        return "Already private"

    def monitor_and_update_permissions(self): #Monitors and updates permissions of files in public folders to private
        while True:
            try:
                items = self.list_files(page_size=100)
                for item in items:
                    if item['mimeType'] == 'application/vnd.google-apps.folder' or item['trashed']:
                        continue
                    if 'parents' in item:
                        parent_folder_id = self.get_parent_folder_id(item['id'])
                        if parent_folder_id and self.is_folder_public(parent_folder_id):
                            status_changed = self.update_file_permission_to_private(item['id'])
                            print(f"File: {self.get_full_path(item['id'])} ({item['id']}) in a public folder, Status: {status_changed}")
                        else:
                            print(f"File: {self.get_full_path(item['id'])} ({item['id']}) in a private folder, Status: Already private")
                time.sleep(self.interval)
            except Exception as e:
                print(f"Error monitoring files: {e}")

    def create_test_file(self):
        file_metadata = {'name': 'testFile', 'mimeType': 'text/plain'}
        file = self.service.files().create(body=file_metadata, fields='id').execute()
        return file['id']

    def get_file_permissions(self, file_id):
        permissions = self.service.permissions().list(fileId=file_id, fields='permissions(id, type, role, emailAddress)').execute()
        return permissions.get('permissions', [])

    def delete_file(self, file_id):
        self.service.files().delete(fileId=file_id).execute()


def discover_default_permissions(drive): #Discovers and prints the default permissions of a test file in Google Drive.
    test_file_id = drive.create_test_file()
    try:
        permissions = drive.get_file_permissions(test_file_id)
        for permission in permissions:
            print(f"ID: {permission['id']}, Type: {permission['type']}, Role: {permission['role']}, Email: {permission.get('emailAddress', 'N/A')}")
    finally:
        drive.delete_file(test_file_id)


def main():
    parser = argparse.ArgumentParser(description='Google Drive file permission monitor.')
    parser.add_argument('-a', '--app', type=str, required=True, help='App Json Token')
    parser.add_argument('-i', '--interval', type=int, required=True, help='Monitor Interval in seconds')
    args = parser.parse_args()

    drive = Drive(args.app, args.interval)
    print("Discovering the default permissions...")
    discover_default_permissions(drive)
    print("Starting to monitor Google Drive for new files in publicly accessible folders...")
    drive.monitor_and_update_permissions()

if __name__ == '__main__':
    main()