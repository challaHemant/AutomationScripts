from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
import io

def download_from_drive(drive_file_id, local_file_path, credentials_path):
    """
    Downloads a file from Google Drive using a service account.

    Args:
        drive_file_id (str): The ID of the file to be downloaded from Google Drive.
        local_file_path (str): The local path to save the downloaded file.
        credentials_path (str): The path to the service account credentials JSON file.
    """
    # Authenticate with Google Drive
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    service = build('drive', 'v3', credentials=credentials)

    # Request the file
    request = service.files().get_media(fileId=drive_file_id)
    with io.FileIO(local_file_path, 'wb') as file:
        downloader = MediaIoBaseDownload(file, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.")
    print(f"File downloaded to {local_file_path}")

# Replace these with appropriate values or pass as arguments during runtime
drive_file_id = "your_drive_file_id"  # Replace with the file ID
local_resume_path = "your_local_file_path"  # Replace with the local file path
credentials_path = "your_credentials_file_path"  # Replace with the path to your credentials JSON file

# Download the file
download_from_drive(drive_file_id, local_resume_path, credentials_path)
