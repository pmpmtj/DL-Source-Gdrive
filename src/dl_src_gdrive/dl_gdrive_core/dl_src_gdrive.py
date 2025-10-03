"""
Google Drive Downloader Core Module

This module provides the core functionality for downloading audio files from Google Drive.
It implements a comprehensive GoogleDriveDownloader class that handles OAuth2 authentication,
file discovery, filtering, and downloading with robust error handling and logging.

Key Features:
- OAuth2 authentication with automatic token refresh
- Configurable folder search (root directory or specific folder IDs)
- Audio file filtering by extension (.mp3, .m4a)
- UUID-based file organization in download directory
- Optional file deletion from Google Drive after successful download
- Comprehensive logging and error handling
- Cross-platform path handling

The GoogleDriveDownloader class provides these main methods:
- authenticate(): Handle OAuth2 authentication flow
- list_files_in_folders(): Discover files in configured folders
- filter_audio_files(): Filter files by audio extensions
- download_file(): Download individual files with progress tracking
- download_all_audio_files(): Batch download all audio files
- delete_file_from_gdrive(): Remove files from Google Drive
- cleanup_credentials(): Remove stored credentials for security

Author: [Your Name]
Date: [Current Date]
Version: 1.0.0
"""

from pathlib import Path
from typing import List, Dict, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

from config.dl_gdrive_config import CONFIG
from config.app_config_loader import load_app_config
from logging_utils.logging_config import get_logger
from utils.path_utils import resolve_path, ensure_directory, sanitize_filename, get_script_directory


class GoogleDriveDownloader:
    """
    Google Drive audio file downloader with comprehensive file management.
    
    This class provides a complete solution for downloading audio files from Google Drive
    with OAuth2 authentication, configurable folder search, and robust error handling.
    
    The downloader supports:
    - OAuth2 authentication with automatic token refresh
    - Search in root directory or specific Google Drive folders
    - Audio file filtering by extension (.mp3, .m4a)
    - UUID-based file organization to prevent conflicts
    - Optional file deletion from Google Drive after successful download
    - Comprehensive logging and progress tracking
    - Cross-platform path handling
    
    Attributes:
        logger: Configured logger instance for this downloader
        service: Google Drive API service instance (set after authentication)
        credentials: OAuth2 credentials (set after authentication)
        script_dir: Path to the script directory for relative path resolution
        client_secret_path: Path to the OAuth2 client secret file
        token_path: Path to the stored OAuth2 token file
        download_dir: Directory where files will be downloaded
        
    Example:
        >>> downloader = GoogleDriveDownloader()
        >>> if downloader.authenticate():
        ...     successful, total = downloader.download_all_audio_files()
        ...     print(f"Downloaded {successful}/{total} files")
    """
    
    def __init__(self):
        """
        Initialize the Google Drive downloader with configuration and paths.
        
        This constructor sets up the downloader by:
        - Initializing the logger
        - Resolving script directory for relative path handling
        - Setting up paths for client secret, token, and download directories
        - Configuring Google Drive API settings from app configuration
        
        The downloader will be ready for authentication after initialization.
        All paths are resolved relative to the script directory to ensure
        cross-platform compatibility.
        """
        self.logger = get_logger('gdrive_downloader')
        self.service = None
        self.credentials = None
        
        # Get script directory for path resolution
        self.script_dir = get_script_directory()
        
        # Resolve configuration paths
        self.client_secret_path = resolve_path(
            CONFIG.gdrive.client_secret_file, 
            self.script_dir / "config"
        )
        # Handle token file path - if it starts with 'config/', resolve relative to script directory
        if CONFIG.gdrive.token_file.startswith('config/'):
            self.token_path = self.script_dir / CONFIG.gdrive.token_file
        else:
            self.token_path = resolve_path(
                CONFIG.gdrive.token_file,
                self.script_dir
            )
        # Load app configuration dynamically
        APP_CONFIG = load_app_config()
        
        # Resolve absolute download directory from APP_CONFIG
        self.logger.debug(f"App download_dir: '{APP_CONFIG.download_dir}'")
        download_dir_str = APP_CONFIG.download_dir
        download_path = Path(download_dir_str)
        if not download_path.is_absolute():
            raise ValueError(f"APP_CONFIG.download_dir must be an absolute path (got: {download_dir_str!r})")
        self.download_dir = download_path
        
        self.logger.debug(f"Script directory: {self.script_dir}")
        self.logger.debug(f"Client secret path: {self.client_secret_path}")
        self.logger.debug(f"Token path: {self.token_path}")
        self.logger.debug(f"Download directory: {self.download_dir}")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive API using OAuth2 flow.
        
        This method handles the complete OAuth2 authentication process:
        1. Checks for existing valid credentials
        2. Refreshes expired credentials if refresh token is available
        3. Initiates OAuth2 flow if no valid credentials exist
        4. Saves credentials for future use
        5. Builds the Google Drive API service
        
        The authentication process supports:
        - Automatic credential refresh for expired tokens
        - Local server OAuth2 flow for user authorization
        - Persistent credential storage for subsequent runs
        
        Returns:
            bool: True if authentication successful, False otherwise
            
        Raises:
            Exception: If authentication fails due to network issues,
                     invalid credentials, or API errors
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
    
    def list_files_in_folders(self) -> List[Dict]:
        """
        List all files in the configured Google Drive folders.
        
        This method searches through all configured folders (root directory or
        specific folder IDs) and retrieves file metadata including ID, name,
        MIME type, size, and timestamps.
        
        The search process:
        1. Iterates through each configured folder ID
        2. Queries Google Drive API for files in each folder
        3. Retrieves file metadata (id, name, mimeType, size, createdTime, modifiedTime)
        4. Logs detailed information about found files
        5. Handles API errors gracefully and continues with other folders
        
        Returns:
            List[Dict]: List of file metadata dictionaries, each containing:
                - id: Google Drive file ID
                - name: File name
                - mimeType: MIME type of the file
                - size: File size in bytes (if available)
                - createdTime: File creation timestamp
                - modifiedTime: File modification timestamp
                
        Note:
            Requires authentication before calling. Returns empty list if not authenticated.
        """
        if not self.service:
            self.logger.error("Not authenticated. Call authenticate() first.")
            return []
        
        all_files = []
        
        for folder_id in CONFIG.gdrive.search_folders:
            folder_name = "root directory" if folder_id == "root" else f"folder {folder_id}"
            self.logger.info(f"Listing files in {folder_name}...")
            
            try:
                # Query for files in this folder
                if folder_id == "root":
                    query = "parents in 'root' and trashed=false"
                else:
                    query = f"parents in '{folder_id}' and trashed=false"
                
                results = self.service.files().list(
                    q=query,
                    pageSize=1000,
                    fields="nextPageToken, files(id, name, mimeType, size, createdTime, modifiedTime)"
                ).execute()
                
                files = results.get('files', [])
                self.logger.info(f"Found {len(files)} files in {folder_name}")
                
                # Log file details
                for file in files:
                    self.logger.debug(f"File: {file['name']} (ID: {file['id']}, Size: {file.get('size', 'Unknown')})")
                
                all_files.extend(files)
                
            except HttpError as e:
                self.logger.error(f"Error listing files in {folder_name}: {str(e)}")
                continue
            except Exception as e:
                self.logger.error(f"Unexpected error listing files in {folder_name}: {str(e)}")
                continue
        
        self.logger.info(f"Total files found across all folders: {len(all_files)}")
        return all_files
    
    def filter_audio_files(self, files: List[Dict]) -> List[Dict]:
        """
        Filter files to only include audio files with allowed extensions.
        
        This method processes a list of file metadata dictionaries and filters
        them to include only files with audio extensions configured in the
        application settings (.mp3, .m4a by default).
        
        The filtering process:
        1. Extracts file extension from each file name
        2. Converts extension to lowercase for case-insensitive matching
        3. Checks if extension is in the allowed extensions list
        4. Logs detailed information about each file's filtering decision
        5. Returns only files that match the audio extension criteria
        
        Args:
            files (List[Dict]): List of file metadata dictionaries from
                               list_files_in_folders() or similar source
                               
        Returns:
            List[Dict]: Filtered list containing only audio files with
                       allowed extensions. Each dictionary contains the same
                       metadata as the input files.
                       
        Note:
            The allowed extensions are configured in CONFIG.gdrive.allowed_extensions
            and default to ['.mp3', '.m4a'].
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
        Download a single file from Google Drive with progress tracking.
        
        This method downloads a file from Google Drive to the local filesystem
        with comprehensive error handling, progress tracking, and optional
        post-download cleanup. Files are organized in date-prefixed directories
        to maintain chronological order for diary entries.
        
        The download process:
        1. Retrieves file metadata to get creation date
        2. Sanitizes filename for filesystem safety
        3. Creates date-prefixed subdirectory to maintain chronological order
        4. Checks if file already exists (skips if found)
        5. Downloads file with progress tracking
        6. Verifies download integrity
        7. Optionally deletes file from Google Drive if configured
        
        Args:
            file_id (str): Google Drive file ID for the file to download
            file_name (str): Original name of the file (will be sanitized)
            
        Returns:
            bool: True if download successful, False otherwise
            
        Note:
            - Requires authentication before calling
            - Files are organized in date-prefixed subdirectories for chronological ordering
            - Filenames are sanitized to prevent filesystem issues
            - Existing files are skipped (not re-downloaded)
            - File deletion from Google Drive is optional and configurable
        """
        if not self.service:
            self.logger.error("Not authenticated. Call authenticate() first.")
            return False
        
        # Sanitize filename for filesystem safety
        safe_filename = sanitize_filename(file_name)
        
        # Get file metadata to extract creation date for chronological ordering
        try:
            file_metadata = self.service.files().get(fileId=file_id).execute()
            created_time = file_metadata.get('createdTime', '')
            
            if created_time:
                # Parse ISO 8601 timestamp and format as YYYY-MM-DD_HHMMSS
                from datetime import datetime
                dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                formatted_date = dt.strftime('%Y-%m-%d_%H%M%S')
                self.logger.debug(f"File creation date: {created_time} -> {formatted_date}")
            else:
                # Fallback to current time if creation date not available
                from datetime import datetime
                formatted_date = datetime.now().strftime('%Y-%m-%d_%H%M%S')
                self.logger.warning(f"No creation date found for {file_name}, using current time: {formatted_date}")
            
        except Exception as e:
            # Fallback to current time if metadata retrieval fails
            from datetime import datetime
            formatted_date = datetime.now().strftime('%Y-%m-%d_%H%M%S')
            self.logger.warning(f"Failed to get creation date for {file_name}: {e}, using current time: {formatted_date}")
        
        # Create date-prefixed subdirectory for chronological ordering
        date_prefixed_dir = self.download_dir / f"{formatted_date}_{file_id}"
        file_path = date_prefixed_dir / safe_filename
        
        # Check if file already exists
        if file_path.exists():
            self.logger.warning(f"File already exists, skipping: {formatted_date}_{file_id}/{safe_filename}")
            return True
        
        self.logger.info(f"Downloading: {file_name} -> {formatted_date}_{file_id}/{safe_filename}")
        
        try:
            # Ensure date-prefixed directory exists
            ensure_directory(date_prefixed_dir)
            
            # Get file size from metadata (already retrieved above)
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
                self.logger.info(f"Successfully downloaded: {formatted_date}_{file_id}/{safe_filename}")
                
                # Delete from Google Drive if configured to do so
                if CONFIG.gdrive.delete_from_src:
                    self.logger.debug("delete_from_src is enabled, deleting from Google Drive...")
                    if self.delete_file_from_gdrive(file_id, file_name):
                        self.logger.info(f"File deleted from Google Drive after successful download: {file_name}")
                    else:
                        self.logger.warning(f"Failed to delete file from Google Drive: {file_name}")
                        # Note: We don't fail the download if deletion fails
                
                return True
            else:
                self.logger.error(f"Download failed or file is empty: {formatted_date}_{file_id}/{safe_filename}")
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
        Download all audio files from configured Google Drive folders.
        
        This is the main method for batch downloading audio files. It orchestrates
        the complete process of discovering, filtering, and downloading audio files
        from all configured Google Drive folders.
        
        The process follows these steps:
        1. Lists all files in configured folders
        2. Filters files to include only audio files (.mp3, .m4a)
        3. Downloads each audio file individually
        4. Tracks successful and failed downloads
        5. Reports comprehensive results
        
        Returns:
            Tuple[int, int]: A tuple containing:
                - successful_downloads: Number of files successfully downloaded
                - total_files: Total number of audio files found
                
        Note:
            - Returns (0, 0) if no files are found in any configured folders
            - Returns (0, 0) if no audio files are found among the files
            - Requires authentication before calling
            - Each file is downloaded to its own UUID-based subdirectory
        """
        self.logger.info("Starting download of all audio files from configured Google Drive folders...")
        
        # List all files from configured folders
        all_files = self.list_files_in_folders()
        if not all_files:
            self.logger.warning("No files found in configured Google Drive folders")
            return 0, 0
        
        # Filter for audio files
        audio_files = self.filter_audio_files(all_files)
        if not audio_files:
            self.logger.warning("No audio files found in configured Google Drive folders")
            return 0, 0
        
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
    
    def delete_file_from_gdrive(self, file_id: str, file_name: str) -> bool:
        """
        Delete a file from Google Drive after successful download.
        
        This method removes a file from Google Drive using the Google Drive API.
        It's typically called after a successful download when the application
        is configured to delete source files.
        
        Args:
            file_id (str): Google Drive file ID of the file to delete
            file_name (str): Name of the file (used for logging purposes only)
            
        Returns:
            bool: True if deletion successful, False otherwise
            
        Note:
            - Requires authentication before calling
            - This is a permanent operation - deleted files cannot be recovered
            - Used in conjunction with CONFIG.gdrive.delete_from_src setting
            - File deletion failures do not affect download success status
        """
        if not self.service:
            self.logger.error("Not authenticated. Call authenticate() first.")
            return False
        
        self.logger.info(f"Deleting from Google Drive: {file_name} (ID: {file_id})")
        
        try:
            # Delete the file
            self.service.files().delete(fileId=file_id).execute()
            self.logger.info(f"Successfully deleted from Google Drive: {file_name}")
            return True
            
        except HttpError as e:
            self.logger.error(f"HTTP error deleting {file_name}: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"Error deleting {file_name}: {str(e)}")
            return False
    
    def cleanup_credentials(self) -> None:
        """
        Remove stored credentials file for security purposes.
        
        This method permanently deletes the stored OAuth2 token file from the
        local filesystem. This is useful for security-conscious environments
        where credentials should not persist after the application completes.
        
        The cleanup process:
        1. Checks if the token file exists
        2. Logs the cleanup operation
        3. Permanently removes the token file
        4. Confirms successful cleanup
        
        Note:
            - This is a permanent operation - credentials cannot be recovered
            - User will need to re-authenticate on next run
            - Typically called with --cleanup command-line flag
            - Safe to call multiple times (no error if file doesn't exist)
        """
        if self.token_path.exists():
            self.logger.debug("Cleaning up credentials file...")
            self.token_path.unlink()
            self.logger.info("Credentials file removed")
