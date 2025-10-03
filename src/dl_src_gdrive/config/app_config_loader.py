"""
App Config Loader Module

This module provides dynamic loading of the application configuration from
the root-level app_config directory. It supports both regular Python execution
and PyInstaller frozen applications, ensuring consistent configuration access
across different deployment scenarios.

The loader:
- Locates app_config/app_config.py at the project root
- Dynamically imports the configuration module
- Validates configuration values
- Provides detailed logging for debugging
- Raises clear errors for missing or misconfigured files

Author: [Your Name]
Date: [Current Date]
Version: 1.0.0
"""

import importlib.util
from pathlib import Path
from typing import Any

from utils.path_utils import get_script_directory
from logging_utils.logging_config import get_logger


def load_app_config() -> Any:
    """
    Dynamically load the application configuration from the root app_config directory.
    
    This function locates and loads the app_config.py file from the project root,
    ensuring it works in both regular Python execution and PyInstaller frozen
    applications. It validates the configuration and provides detailed logging.
    
    The loading process:
    1. Determines the project root directory
    2. Locates app_config/app_config.py
    3. Dynamically imports the module
    4. Validates APP_CONFIG exists and has required attributes
    5. Validates download_dir is an absolute path
    6. Returns the APP_CONFIG instance
    
    Returns:
        Any: The APP_CONFIG instance from the loaded module
        
    Raises:
        FileNotFoundError: If app_config/app_config.py is not found
        ImportError: If the module cannot be imported
        AttributeError: If APP_CONFIG is missing from the module
        ValueError: If download_dir is not an absolute path
        
    Example:
        >>> config = load_app_config()
        >>> print(config.download_dir)
        "C:\\Users\\me\\Downloads"
    """
    logger = get_logger("app_config_loader")
    
    # Get script directory and determine project root
    script_dir = get_script_directory()
    logger.debug(f"Script directory: {script_dir}")
    
    # For frozen apps, project root is the script directory
    # For regular Python, we need to go up to the project root
    if script_dir.name == "dl_src_gdrive":
        # We're in the src/dl_src_gdrive directory, go up two levels
        project_root = script_dir.parent.parent
    else:
        # We're already at project root or in a different structure
        project_root = script_dir
    
    logger.debug(f"Project root: {project_root}")
    
    # Locate app_config/app_config.py
    app_config_path = project_root / "app_config" / "app_config.py"
    logger.debug(f"Looking for app_config at: {app_config_path}")
    
    if not app_config_path.exists():
        raise FileNotFoundError(
            f"App configuration file not found at: {app_config_path}\n"
            f"Expected location: {project_root}/app_config/app_config.py"
        )
    
    # Dynamically import the module
    try:
        spec = importlib.util.spec_from_file_location("app_config", app_config_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not create module spec for {app_config_path}")
        
        app_config_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_config_module)
        
        logger.debug("Successfully loaded app_config module")
        
    except Exception as e:
        raise ImportError(f"Failed to import app_config module from {app_config_path}: {e}")
    
    # Validate APP_CONFIG exists
    if not hasattr(app_config_module, 'APP_CONFIG'):
        raise AttributeError(
            f"APP_CONFIG not found in {app_config_path}. "
            "The module must define APP_CONFIG = AppConfig()"
        )
    
    app_config = app_config_module.APP_CONFIG
    logger.debug(f"Loaded APP_CONFIG: {app_config}")
    
    # Validate download_dir is absolute
    if not hasattr(app_config, 'download_dir'):
        raise ValueError(
            f"APP_CONFIG missing download_dir attribute. "
            "AppConfig must have download_dir field."
        )
    
    download_dir_str = app_config.download_dir
    logger.debug(f"App download_dir: '{download_dir_str}'")
    
    download_path = Path(download_dir_str)
    if not download_path.is_absolute():
        raise ValueError(
            f"APP_CONFIG.download_dir must be an absolute path (got: {download_dir_str!r})\n"
            f"Example (Windows): r'C:\\\\Users\\\\me\\\\Downloads'\n"
            f"Example (Linux/macOS): '/home/me/downloads'"
        )
    
    logger.debug(f"Configuration validation successful. Download directory: {download_path}")
    
    return app_config
