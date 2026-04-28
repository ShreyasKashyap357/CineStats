"""Timestamped logging utility for CineStats backend with file rotation."""

import datetime
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Log file paths
BACKEND_LOG = LOGS_DIR / "backend.log"
ERROR_LOG = LOGS_DIR / "errors.log"

# Configure logging
def setup_logging():
    """Setup logging with file rotation and console output."""
    # Create formatters
    timestamp_format = "%d%m%Y %H%M%S.%f"
    timestamp_format_short = timestamp_format[:-3]  # Remove last 3 digits for milliseconds
    
    file_formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
        datefmt=timestamp_format_short
    )
    
    console_formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt=timestamp_format_short
    )
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # File handler with rotation (10MB max, keep 5 backups)
    file_handler = RotatingFileHandler(
        BACKEND_LOG,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = RotatingFileHandler(
        ERROR_LOG,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    return root_logger

# Initialize logging
_logger = setup_logging()

def get_logger(name: str = "cinestats"):
    """Get a logger instance with the given name."""
    return logging.getLogger(name)

def get_timestamp():
    """Get timestamp in ddmmYYYY hhmmss.milliseconds format (legacy)."""
    now = datetime.datetime.now()
    return now.strftime("%d%m%Y %H%M%S.%f")[:-3]

def log_info(message):
    """Log info message with timestamp."""
    _logger.info(message)

def log_error(message):
    """Log error message with timestamp."""
    _logger.error(message)

def log_warning(message):
    """Log warning message with timestamp."""
    _logger.warning(message)

def log_debug(message):
    """Log debug message with timestamp."""
    _logger.debug(message)
