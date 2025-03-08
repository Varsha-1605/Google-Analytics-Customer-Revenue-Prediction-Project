"""Logging configuration for the Revenue Analytics Dashboard."""
import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging
def setup_logger(name):
    """Set up logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create handlers
    current_date = datetime.now().strftime('%Y-%m-%d')
    file_handler = logging.FileHandler(
        os.path.join(LOG_DIR, f'{current_date}.log')
    )
    console_handler = logging.StreamHandler()

    # Create formatters and add it to handlers
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(log_format)
    console_handler.setFormatter(log_format)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger