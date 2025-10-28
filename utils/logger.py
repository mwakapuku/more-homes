# logger.py
import os
import logging
from datetime import datetime


class AppLogger:
    def __init__(self, name=__name__, log_dir="logs"):
        """
        Initialize the logger with a name and log directory.

        Args:
            name (str): Name of the logger (usually __name__)
            log_dir (str): Directory to store log files
        """
        self._setup_log_directory(log_dir)
        self.logger = logging.getLogger(name)
        self._configure_logger(log_dir)

    def _setup_log_directory(self, log_dir):
        """Create log directory if it doesn't exist"""
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            self._log_to_file(f"Created logs directory at {os.path.abspath(log_dir)}", "info")

    def _configure_logger(self, log_dir):
        """Configure logging settings"""
        log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
        log_filepath = os.path.join(log_dir, log_filename)

        # Set up logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Configure handlers
        file_handler = logging.FileHandler(log_filepath)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Add handlers and set level
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def info(self, message):
        """Log an info message"""
        self.logger.info(message)

    def error(self, message):
        """Log an error message"""
        self.logger.error(message)

    def warning(self, message):
        """Log a warning message"""
        self.logger.warning(message)

    def debug(self, message):
        """Log a debug message"""
        self.logger.debug(message)

    def _log_to_file(self, message, level="info"):
        """Internal method for initial logging before logger is configured"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level.upper()}: {message}\n"

        log_filename = datetime.now().strftime("%Y-%m-%d") + ".log"
        log_filepath = os.path.join("logs", log_filename)

        with open(log_filepath, "a") as log_file:
            log_file.write(log_entry)