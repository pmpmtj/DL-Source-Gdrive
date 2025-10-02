#!/usr/bin/env python3
"""
Google Drive Audio File Downloader

Main CLI script for downloading MP3 and M4A files from Google Drive root directory.
This script authenticates with Google Drive API and downloads all audio files
matching the configured extensions.

Usage:
    python -m dl_src_gdrive.main [--cleanup] [--debug]

Author: [Your Name]
Date: [Current Date]
"""

import argparse
import sys
from pathlib import Path

# Get script directory for proper imports
SCRIPT_DIR = Path(__file__).resolve().parent

from dl_gdrive_core.dl_src_gdrive import GoogleDriveDownloader
from logging_utils.logging_config import get_logger, set_console_level
from config.app_config import CONFIG


def main():
    """Main entry point for the Google Drive downloader."""
    parser = argparse.ArgumentParser(
        description="Download MP3 and M4A files from Google Drive root directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m dl_src_gdrive.main              # Download all audio files
    python -m dl_src_gdrive.main --debug      # Enable debug logging
    python -m dl_src_gdrive.main --cleanup    # Remove credentials after download
        """
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Remove stored credentials after download (for security)'
    )
    
    parser.add_argument(
        '--delete-from-gdrive',
        action='store_true',
        help='Delete files from Google Drive after successful download'
    )
    
    args = parser.parse_args()
    
    # Initialize logger
    logger = get_logger('gdrive_downloader')
    
    # Set debug level if requested
    if args.debug:
        set_console_level(logger, 'DEBUG')
        logger.debug("Debug logging enabled")
    
    # Override delete_from_src config if command-line argument is provided
    if args.delete_from_gdrive:
        CONFIG.gdrive.delete_from_src = True
        logger.info("Delete from Google Drive enabled via command-line argument")
    
    logger.info("=" * 60)
    logger.info("Google Drive Audio File Downloader")
    logger.info("=" * 60)
    logger.info(f"Search folders: {CONFIG.gdrive.search_folders}")
    logger.info(f"Delete from source: {CONFIG.gdrive.delete_from_src}")
    logger.info("=" * 60)
    
    try:
        # Initialize downloader
        downloader = GoogleDriveDownloader()
        
        # Authenticate with Google Drive
        logger.info("Step 1: Authenticating with Google Drive...")
        if not downloader.authenticate():
            logger.error("Authentication failed. Please check your client secret file.")
            return 1
        
        # Download all audio files
        logger.info("Step 2: Downloading audio files...")
        successful, total = downloader.download_all_audio_files()
        
        # Report results
        if total == 0:
            logger.warning("No audio files found in Google Drive root directory")
        elif successful == total:
            logger.info(f"Successfully downloaded all {total} audio files")
        else:
            logger.warning(f"Downloaded {successful} out of {total} audio files")
        
        # Cleanup credentials if requested
        if args.cleanup:
            logger.info("Step 3: Cleaning up credentials...")
            downloader.cleanup_credentials()
            logger.info("Credentials cleaned up for security")
        
        logger.info("=" * 60)
        logger.info("Download process completed")
        logger.info("=" * 60)
        
        return 0 if successful == total else 1
        
    except KeyboardInterrupt:
        logger.info("\nDownload interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
