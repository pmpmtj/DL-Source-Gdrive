"""
Google Drive Audio File Downloader Package

A comprehensive Python package for downloading audio files (MP3, M4A) from Google Drive
with OAuth2 authentication, configurable folder search, and robust error handling.

Key Features:
- OAuth2 authentication with automatic token refresh
- Configurable folder search (root directory or specific folder IDs)
- Audio file filtering by extension (.mp3, .m4a)
- UUID-based file organization to prevent conflicts
- Optional file deletion from Google Drive after successful download
- Comprehensive logging and progress tracking
- Cross-platform path handling
- PyInstaller frozen application support

Package Structure:
- dl_gdrive_core: Core Google Drive API functionality
- config: Application configuration management
- utils: Cross-platform path utilities
- logging_utils: Centralized logging configuration
- main: Command-line interface

Usage:
    from dl_src_gdrive import GoogleDriveDownloader
    from dl_src_gdrive.config import CONFIG
    
    downloader = GoogleDriveDownloader()
    if downloader.authenticate():
        successful, total = downloader.download_all_audio_files()
        print(f"Downloaded {successful}/{total} files")

Author: [Your Name]
Date: [Current Date]
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "[Your Name]"
__description__ = "Google Drive Audio File Downloader"
