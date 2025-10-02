"""
Application Configuration Module

This module provides centralized configuration management for the Google Drive
audio file downloader. It uses Python dataclasses to define configuration
structures with type hints and default values.

The configuration is organized into logical sections:
- GdriveConfig: Google Drive API settings and file processing options
- AppConfig: Main application configuration combining all sections

Configuration Features:
- Type-safe configuration with dataclasses
- Default values for all settings
- Centralized configuration management
- Easy to extend with new settings
- No external configuration files required

Usage:
    from config.dl_gdrive_config import CONFIG
    
    # Access Google Drive settings
    print(CONFIG.gdrive.allowed_extensions)
    
    # Modify settings at runtime
    CONFIG.gdrive.delete_from_src = False

Author: [Your Name]
Date: [Current Date]
Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import List, Optional



@dataclass
class GdriveConfig:
    """
    Google Drive API and file processing configuration.
    
    This dataclass contains all configuration settings related to Google Drive
    operations, including API credentials, folder search settings, file processing
    options, and supported audio formats.
    
    Attributes:
        delete_from_src (bool): Whether to delete files from Google Drive after
                               successful download. Default: True
        search_folders (List[str]): List of Google Drive folder IDs to search.
                                   Use "root" for root directory. Default: ["root"]
        client_secret_file (str): Filename of the OAuth2 client secret JSON file.
                                 Default: "client_secret_890800499519-...json"
        token_file (str): Path to store OAuth2 token file. Default: "config/token.json"
        scopes (List[str]): Google Drive API scopes. Default: ['https://www.googleapis.com/auth/drive']
        allowed_extensions (List[str]): Audio file extensions to download.
                                      Default: ['.mp3', '.m4a']
    """

    delete_from_src: bool = False

    
    # Folders to search for files (Google Drive folder IDs or "root" for root directory)
    search_folders: List[str] = field(default_factory=lambda: [
        "root"  # Search in root directory by default
    ])
    
    # Google Drive API settings
    client_secret_file: str = "client_secret_890800499519-d2bvsnp5bbfqieovpd4fnafacl0hkjaa.apps.googleusercontent.com.json"
    token_file: str = "config/token.json"
    scopes: List[str] = field(default_factory=lambda: [
        'https://www.googleapis.com/auth/drive'
    ])

    # ============================================================================
    # FILE FORMAT CONFIGURATION
    # ============================================================================
    allowed_extensions: List[str] = field(default_factory=lambda: [
        '.mp3',   # MPEG Audio Layer III
        '.m4a',   # MPEG-4 Audio
        '.wav',   # Waveform Audio
        '.ogg',   # Ogg Vorbis
        '.flac',  # Free Lossless Audio Codec
        '.aac',   # Advanced Audio Coding
        '.wma',   # Windows Media Audio
    ])
    

@dataclass
class AppConfig:
    """
    Main application configuration combining all configuration sections.
    
    This is the top-level configuration class that combines all configuration
    sections into a single, easily accessible configuration object. It provides
    a centralized way to access all application settings.
    
    Attributes:
        gdrive (GdriveConfig): Google Drive API and file processing configuration.
                              Default: GdriveConfig() with default values
    """
    # Google Drive configuration
    gdrive: GdriveConfig = field(default_factory=GdriveConfig)
    

# Global configuration instance
# Import this in your scripts: from dl_gdrive_config import CONFIG
CONFIG = AppConfig()


