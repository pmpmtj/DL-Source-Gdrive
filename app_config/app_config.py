from dataclasses import dataclass


@dataclass
class AppConfig:
    """
    Application-level configuration.

    download_dir must be an absolute path. Example (Windows):
    r"C:\\Users\\me\\Downloads". Example (Linux/macOS): "/home/me/downloads".
    """

    download_dir: str = r"C:\Users\pmpmt\Scripts_Cursor\downloads"


# Global application config instance
APP_CONFIG = AppConfig()

