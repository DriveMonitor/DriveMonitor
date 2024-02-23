Google Drive File Permission Monitor
Overview

This Python script monitors a Google Drive for new files in publicly accessible folders and updates their permissions to private. It is designed to enhance privacy and security by automatically adjusting the permissions of files that may have been inadvertently set to public.
Features

    Credential Management: Handles Google OAuth2 credentials for accessing the Google Drive API&Saving to token.
    File Permission Monitoring: Continuously monitors for new files and updates permissions for files in public folders to private.
    Utility Functions: Includes functions to list files, check if a folder is public, get the full path of a file, update file permissions, and more.

Prerequisites

    Python 3.x
    Google Cloud Project with the Drive API enabled
    OAuth 2.0 Client IDs configured in your Google Cloud Project

Installation

    git clone https://github.com/DriveMonitor/DriveMonitor.git
    
    pip3 install -r requirements.txt

Usage

To use the script, you need to provide the path to your app.json file and the interval for monitoring file permissions in seconds.

    python main.py -a <path_to_credentials.json> -i <monitor_interval_in_seconds>

Example

    python main.py -a credentials.json -i 60

This will start the script, discover default permissions for a test file, and then continuously monitor your Google Drive for new files in publicly accessible folders, updating their permissions to private as needed.
Sample Output

Discovering the default permissions...

ID: abc123, Type: user, Role: owner, Email: user@example.com

Starting to monitor Google Drive for new files in publicly accessible folders...

File: My Drive/path/to/file (fileId) in a public folder, Status: Was public, changed to private

File: My Drive/another/path/file (fileId) in a private folder, Status: Already private

Permissions & Scopes

The script requires the following scope to function correctly: https://www.googleapis.com/auth/drive. This scope allows the script to view and manage the files in Google Drive.
