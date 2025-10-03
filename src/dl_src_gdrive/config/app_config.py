"""
App Config Stub Module

This module has been moved to the project root for better organization and
to allow external tools to share the same configuration structure.

The app configuration is now located at: ./app_config/app_config.py

To use the configuration, import the loader:
    from config.app_config_loader import load_app_config
    APP_CONFIG = load_app_config()

This stub file prevents accidental imports and provides clear guidance
on the new location and usage pattern.
"""

raise ImportError(
    "The app_config module has been moved to the project root.\n"
    "\n"
    "New location: ./app_config/app_config.py\n"
    "\n"
    "To use the configuration, import the loader instead:\n"
    "    from config.app_config_loader import load_app_config\n"
    "    APP_CONFIG = load_app_config()\n"
    "\n"
    "This allows external tools to share the same configuration structure\n"
    "by accessing ./app_config/app_config.py at the project root."
)
