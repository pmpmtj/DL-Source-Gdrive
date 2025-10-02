"""

"""

from dataclasses import dataclass, field
from typing import List, Optional



@dataclass
class GdriveConfig:
    """Google Drive API and file processing configuration."""

    delete_from_src: bool = True
    file_type: str = "audio"
    
    # Download directory (relative to script directory)
    download_dir: str = "downloads"
    
    # Google Drive API settings
    client_secret_file: str = "client_secret_890800499519-d2bvsnp5bbfqieovpd4fnafacl0hkjaa.apps.googleusercontent.com.json"
    token_file: str = "token.json"
    scopes: List[str] = field(default_factory=lambda: [
        'https://www.googleapis.com/auth/drive.readonly'
    ])

    # ============================================================================
    # FILE FORMAT CONFIGURATION
    # ============================================================================
    allowed_extensions: List[str] = [
        '.mp3',   # MPEG Audio Layer III
        '.m4a',   # MPEG-4 Audio
    ]
    

@dataclass
class AppConfig:
    """Main application configuration combining all sections."""

    # Google Drive configuration
    gdrive: GdriveConfig = field(default_factory=GdriveConfig)
    

# Global configuration instance
# Import this in your scripts: from app_config import CONFIG
CONFIG = AppConfig()


