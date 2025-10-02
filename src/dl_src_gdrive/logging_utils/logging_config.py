"""
Logging Configuration Module

This module provides centralized logging configuration for the Google Drive
audio file downloader. It supports configurable log levels, file outputs,
and console outputs with comprehensive logging management.

Key Features:
- Centralized logging configuration management
- Per-module logger configuration
- Configurable log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Separate console and file output control
- Automatic log directory creation
- Consistent log formatting across all modules
- Dynamic log level adjustment

Configuration Structure:
- LOGGING_CONFIG: Dictionary defining logger configurations
- DEFAULT_LOG_DIR: Default directory for log files
- DEFAULT_LOG_FORMAT: Standard log message format
- DEFAULT_DATE_FORMAT: Standard timestamp format

The module provides these main functions:
- get_logger(): Create or retrieve configured logger instances
- set_console_level(): Dynamically adjust console log levels
- Centralized configuration for consistent logging across the application

Author: [Your Name]
Date: [Current Date]
Version: 1.0.0
"""

import logging
import sys
from pathlib import Path
from typing import Optional


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOGGING_CONFIG = {
    # Google Drive downloader logger
    "gdrive_downloader": {
        "level": "DEBUG",
        "log_filename": "gdrive_downloader.log",
        "console_output": True,
        "file_output": True,
    },
}

# ============================================================================
# DEFAULT SETTINGS
# ============================================================================
DEFAULT_LOG_DIR = "logs"  # Default log directory (relative to CWD or configurable)
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(
    logger_name: str,
    log_dir: Optional[Path] = None,
    console_level: Optional[str] = None,
    file_level: Optional[str] = None,
) -> logging.Logger:
    """
    Get or create a configured logger instance with console and file handlers.
    
    This function creates a logger with both console and file handlers based on
    the configuration defined in LOGGING_CONFIG. If the logger already exists,
    it returns the existing instance to prevent duplicate handlers.
    
    The logger configuration process:
    1. Retrieves configuration for the specified logger name
    2. Sets up console handler with configurable log level
    3. Sets up file handler with configurable log level and directory
    4. Applies consistent formatting to all handlers
    5. Prevents duplicate handler creation
    
    Args:
        logger_name (str): Name of the logger (must match a key in LOGGING_CONFIG)
        log_dir (Optional[Path]): Directory for log files. Defaults to DEFAULT_LOG_DIR
                                 in current working directory if None
        console_level (Optional[str]): Override for console log level.
                                     Valid values: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        file_level (Optional[str]): Override for file log level.
                                  Valid values: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        
    Returns:
        logging.Logger: Configured logger instance with console and file handlers
        
    Example:
        >>> logger = get_logger('gdrive_downloader', console_level='DEBUG')
        >>> logger.info('Starting download...')
        >>> logger.debug('Detailed debug information')
        
    Note:
        - Logger names should match keys in LOGGING_CONFIG dictionary
        - Existing loggers are returned without modification
        - Log directory is created automatically if it doesn't exist
        - Console and file levels can be set independently
    """
    # Get configuration for this logger
    config = LOGGING_CONFIG.get(logger_name, {})
    
    # Use provided levels or fall back to config
    default_level = config.get("level", "INFO")
    console_level = console_level or default_level
    file_level = file_level or default_level
    
    # Create logger
    logger = logging.getLogger(logger_name)
    
    # Only configure if not already configured (avoid duplicate handlers)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)  # Set to DEBUG to allow handlers to filter
        logger.propagate = False  # Don't propagate to root logger
        
        # Create formatters
        formatter = logging.Formatter(
            fmt=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT
        )
        
        # Console handler (if enabled in config)
        if config.get("console_output", True):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, console_level.upper()))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # File handler (if enabled in config)
        if config.get("file_output", False):
            # Determine log directory
            if log_dir is None:
                log_dir = Path.cwd() / DEFAULT_LOG_DIR
            else:
                log_dir = Path(log_dir)
            
            # Create log directory if it doesn't exist
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Get log filename from config
            log_filename = config.get("log_filename", f"{logger_name}.log")
            log_file = log_dir / log_filename
            
            # Create file handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(getattr(logging, file_level.upper()))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    
    return logger


def set_console_level(logger: logging.Logger, level: str) -> None:
    """
    Update the console handler's log level for an existing logger.
    
    This function dynamically changes the console log level for an existing
    logger instance. It's particularly useful for implementing CLI flags
    like --debug that need to adjust logging verbosity at runtime.
    
    The update process:
    1. Converts the level string to a logging level constant
    2. Searches through all handlers for console handlers
    3. Updates the level of the first console handler found
    4. Leaves file handlers unchanged
    
    Args:
        logger (logging.Logger): Logger instance to update
        level (str): New log level for console output.
                    Valid values: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
        
    Example:
        >>> logger = get_logger('gdrive_downloader')
        >>> set_console_level(logger, 'DEBUG')  # Enable debug output
        >>> logger.debug('This will now appear in console')
        
    Note:
        - Only affects console handlers, file handlers remain unchanged
        - Level names are case-insensitive
        - If no console handler is found, no error is raised
        - This is typically used with command-line --debug flags
    """
    log_level = getattr(logging, level.upper())
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            handler.setLevel(log_level)
            break



