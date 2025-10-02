"""
Google Drive Downloader Core Module

This module provides the core functionality for downloading files from Google Drive.
It handles authentication, file listing, and downloading with proper error handling
and logging.

Author: [Your Name]
Date: [Current Date]
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from ..config.app_config import CONFIG
from ..logging_utils.logging_config import get_logger
from ..utils.path_utils import resolve_path, ensure_directory, sanitize_filename, get_script_directory


class GoogleDriveDownloader:
    """
    Google Drive file downloader with authentication and file management.
    
    This class handles OAuth2 authentication with Google Drive API and provides
    methods to list and download files from the root directory of Google Drive.
    """
    
    def __init__(self):
        """Initialize the Google Drive downloader."""
        self.logger = get_logger('gdrive_downloader')
        self.service = None
        self.credentials = None
        
        # Get script directory for path resolution
        self.script_dir = get_script_directory()
        
        # Resolve configuration paths
        self.client_secret_path = resolve_path(
            CONFIG.gdrive.client_secret_file, 
            self.script_dir
        )
        self.token_path = resolve_path(
            CONFIG.gdrive.token_file,
            self.script_dir
        )
        self.download_dir = resolve_path(
            CONFIG.gdrive.download_dir,
            self.script_dir
        )
        
        self.logger.debug(f"Script directory: {self.script_dir}")
        self.logger.debug(f"Client secret path: {self.client_secret_path}")
        self.logger.debug(f"Token path: {self.token_path}")
        self.logger.debug(f"Download directory: {self.download_dir}")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive API using OAuth2.
        
        Returns:
            True if authentication successful, False otherwise
        """
        self.logger.info("Starting Google Drive authentication...")
        
        try:
            # Check if client secret file exists
            if not self.client_secret_path.exists():
                self.logger.error(f"Client secret file not found: {self.client_secret_path}")
                return False
            
            # Load existing credentials if available
            if self.token_path.exists():
                self.logger.debug("Loading existing credentials...")
                self.credentials = Credentials.from_authorized_user_file(
                    str(self.token_path), 
                    CONFIG.gdrive.scopes
                )
            
            # If there are no (valid) credentials available, let the user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.logger.debug("Refreshing expired credentials...")
                    self.credentials.refresh(Request())
                else:
                    self.logger.info("Starting OAuth2 flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.client_secret_path), 
                        CONFIG.gdrive.scopes
                    )
                    self.credentials = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                self.logger.debug(f"Saving credentials to: {self.token_path}")
                with open(self.token_path, 'w') as token_file:
                    token_file.write(self.credentials.to_json())
            
            # Build the service
            self.service = build('drive', 'v3', credentials=self.credentials)
            self.logger.info("Google Drive authentication successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            return False
    
    def list_root_files(self) -> List[Dict]:
        """
        List all files in the root directory of Google Drive.
        
        Returns:
            List of file metadata dictionaries
        """
        if not self.service:
            self.logger.error("Not authenticated. Call authenticate() first.")
            return []
        
        self.logger.info("Listing files in Google Drive root directory...")
        
        try:
            # Query for files in root directory (not in any folder)
            query = "parents in 'root' and trashed=false"
            
            results = self.service.files().list(
                q=query,
                pageSize=1000,
                fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime)"
            ).execute()
            
            files = results.get('files', [])
            self.logger.info(f"Found {len(files)} files in root directory")
            
            # Log file details
            for file in files:
                self.logger.debug(f"File: {file['name']} (ID: {file['id']}, Size: {file.get('size', 'Unknown')})")
            
            return files
            
        except HttpError as e:
            self.logger.error(f"Error listing files: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error listing files: {str(e)}")
            return []
    
    def filter_audio_files(self, files: List[Dict]) -> List[Dict]:
        """
        Filter files to only include audio files with allowed extensions.
        
        Args:
            files: List of file metadata dictionaries
            
        Returns:
            Filtered list of audio files
        """
        self.logger.info(f"Filtering files for audio extensions: {CONFIG.gdrive.allowed_extensions}")
        
        audio_files = []
        for file in files:
            file_name = file.get('name', '')
            file_ext = Path(file_name).suffix.lower()
            
            if file_ext in CONFIG.gdrive.allowed_extensions:
                audio_files.append(file)
                self.logger.debug(f"Audio file found: {file_name}")
            else:
                self.logger.debug(f"Skipping non-audio file: {file_name} (extension: {file_ext})")
        
        self.logger.info(f"Found {len(audio_files)} audio files to download")
        return audio_files
    
    def download_file(self, file_id: str, file_name: str) -> bool:
        """
        Download a single file from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            file_name: Name of the file to save
            
        Returns:
            True if download successful, False otherwise
        """
        if not self.service:
            self.logger.error("Not authenticated. Call authenticate() first.")
            return False
        
        # Sanitize filename for filesystem safety
        safe_filename = sanitize_filename(file_name)
        file_path = self.download_dir / safe_filename
        
        # Check if file already exists
        if file_path.exists():
            self.logger.warning(f"File already exists, skipping: {safe_filename}")
            return True
        
        self.logger.info(f"Downloading: {file_name} -> {safe_filename}")
        
        try:
            # Ensure download directory exists
            ensure_directory(self.download_dir)
            
            # Request file metadata to get size
            file_metadata = self.service.files().get(fileId=file_id).execute()
            file_size = int(file_metadata.get('size', 0))
            
            if file_size > 0:
                self.logger.debug(f"File size: {file_size} bytes")
            
            # Download the file
            request = self.service.files().get_media(fileId=file_id)
            
            with open(file_path, 'wb') as file_handle:
                downloader = MediaIoBaseDownload(file_handle, request)
                done = False
                
                while done is False:
                    status, done = downloader.next_chunk()
                    if status:
                        progress = int(status.progress() * 100)
                        self.logger.debug(f"Download progress: {progress}%")
            
            # Verify download
            if file_path.exists() and file_path.stat().st_size > 0:
                self.logger.info(f"Successfully downloaded: {safe_filename}")
                return True
            else:
                self.logger.error(f"Download failed or file is empty: {safe_filename}")
                if file_path.exists():
                    file_path.unlink()  # Remove empty file
                return False
                
        except HttpError as e:
            self.logger.error(f"HTTP error downloading {file_name}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error downloading {file_name}: {str(e)}")
            return False
    
    def download_all_audio_files(self) -> Tuple[int, int]:
        """
        Download all audio files from Google Drive root directory.
        
        Returns:
            Tuple of (successful_downloads, total_files)
        """
        self.logger.info("Starting download of all audio files from Google Drive root...")
        
        # List all files
        all_files = self.list_root_files()
        if not all_files:
            self.logger.warning("No files found in Google Drive root directory")
            return 0, 0
        
        # Filter for audio files
        audio_files = self.filter_audio_files(all_files)
        if not audio_files:
            self.logger.warning("No audio files found in Google Drive root directory")
            return 0, len(all_files)
        
        # Download each file
        successful_downloads = 0
        total_files = len(audio_files)
        
        for i, file in enumerate(audio_files, 1):
            file_id = file['id']
            file_name = file['name']
            
            self.logger.info(f"Downloading file {i}/{total_files}: {file_name}")
            
            if self.download_file(file_id, file_name):
                successful_downloads += 1
            else:
                self.logger.error(f"Failed to download: {file_name}")
        
        self.logger.info(f"Download complete: {successful_downloads}/{total_files} files downloaded successfully")
        return successful_downloads, total_files
    
    def cleanup_credentials(self) -> None:
        """Remove stored credentials file for security."""
        if self.token_path.exists():
            self.logger.debug("Cleaning up credentials file...")
            self.token_path.unlink()
            self.logger.info("Credentials file removed")
