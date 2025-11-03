"""
Google Drive Module

This module handles downloading images from Google Drive.
It can:
- Connect to your Google Drive account
- List files in a folder
- Download image files
- Sort images by when they were created (newest first)
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import googleapiclient.http
except ImportError:
    print("Error: Google API libraries not installed.")
    print("Run: pip3 install -r requirements.txt")
    sys.exit(1)

from . import config


class GoogleDriveDownloader:
    """
    Handles downloading images from Google Drive.
    
    This class connects to Google Drive, finds images in a folder,
    and downloads them to your computer.
    """
    
    def __init__(self, credentials_path: str = 'credentials.json', 
                 token_path: str = 'token.json'):
        """
        Set up the Google Drive downloader.
        
        Args:
            credentials_path: Path to Google API credentials file
            token_path: Where to save the authentication token
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._authenticate()
    
    def _authenticate(self):
        """
        Log in to Google Drive.
        
        This opens a browser window where you sign in with your Google account.
        You only need to do this once - it saves your login for next time.
        """
        creds = None
        
        # Check if we already logged in before
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(
                self.token_path, config.DRIVE_SCOPES
            )
        
        # If we need to log in (or login expired)
        if not creds or not creds.valid:
            # Try to refresh the login token
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # Need to log in for the first time
                if not os.path.exists(self.credentials_path):
                    print(f"\nError: {self.credentials_path} not found!")
                    print("Please download your Google API credentials:")
                    print("1. Go to https://console.cloud.google.com/apis/credentials")
                    print("2. Create OAuth 2.0 Client ID credentials")
                    print("3. Download as JSON and save as 'credentials.json'")
                    sys.exit(1)
                
                print(f"\nLogging in to Google Drive...")
                print(f"Using: {self.credentials_path}")
                
                # Open browser for login
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, config.DRIVE_SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the login token for next time
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        # Connect to Google Drive service
        self.service = build('drive', 'v3', credentials=creds)
        print("✓ Connected to Google Drive")
    
    def list_files_in_folder(self, folder_id: str) -> List[Dict]:
        """
        Get a list of all files in a Google Drive folder.
        
        Args:
            folder_id: The ID of the folder to look in
            
        Returns:
            List of file information (name, ID, date, etc.)
        """
        try:
            # Ask Google Drive for files in this folder
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and trashed=false",
                pageSize=100,
                fields="files(id, name, createdTime, modifiedTime, mimeType, size)",
                orderBy="modifiedTime desc,createdTime desc"
            ).execute()
            
            files = results.get('files', [])
            print(f"✓ Found {len(files)} files in folder")
            return files
            
        except HttpError as error:
            print(f"Error listing files: {error}")
            return []
    
    def download_file(self, file_id: str, file_name: str, output_dir: str) -> Optional[str]:
        """
        Download a single file from Google Drive.
        
        Args:
            file_id: The ID of the file to download
            file_name: What to name the downloaded file
            output_dir: Where to save the file
            
        Returns:
            Path to the downloaded file, or None if it failed
        """
        try:
            # Get the file from Google Drive
            request = self.service.files().get_media(fileId=file_id)
            file_path = os.path.join(output_dir, file_name)
            
            # Save it to disk
            with open(file_path, 'wb') as f:
                downloader = googleapiclient.http.MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            
            print(f"✓ Downloaded: {file_name}")
            return file_path
            
        except HttpError as error:
            print(f"Error downloading {file_name}: {error}")
            return None
    
    def download_recent_images(self, folder_id: str, num_images: int, 
                               output_dir: str) -> List[str]:
        """
        Download the newest images from a folder.
        
        This function:
        1. Gets all files from the folder
        2. Filters to only images
        3. Sorts by date (newest first)
        4. Downloads the most recent ones
        
        Args:
            folder_id: Google Drive folder ID
            num_images: How many images to download
            output_dir: Where to save the images
            
        Returns:
            List of paths to downloaded image files
        """
        # Get all files
        files = self.list_files_in_folder(folder_id)
        
        # Find only image files
        image_files = []
        for file in files:
            file_name = file.get('name', '')
            mime_type = file.get('mimeType', '')
            
            # Check if it's an image file
            is_image = (
                any(file_name.lower().endswith(ext.lower()) 
                    for ext in config.IMAGE_EXTENSIONS) or
                mime_type.startswith('image/')
            )
            
            if is_image:
                image_files.append(file)
        
        # Sort by when the file was created or modified (newest first)
        def get_timestamp(file):
            """Get the latest timestamp for a file."""
            return file.get('modifiedTime') or file.get('createdTime', '')
        
        image_files.sort(key=get_timestamp, reverse=True)
        
        # Show which images we're selecting
        if image_files:
            print(f"  Selected {min(len(image_files), num_images)} most recent image(s) by timestamp:")
            for i, img in enumerate(image_files[:num_images], 1):
                timestamp = get_timestamp(img)
                print(f"    {i}. {img.get('name', 'Unknown')} - {timestamp[:19] if timestamp else 'No timestamp'}")
        
        # Download the most recent images
        downloaded_paths = []
        for file in image_files[:num_images]:
            file_id = file['id']
            file_name = file['name']
            path = self.download_file(file_id, file_name, output_dir)
            if path:
                downloaded_paths.append(path)
        
        return downloaded_paths

