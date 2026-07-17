import logging
import os
import time
from logging.handlers import RotatingFileHandler
from app.core.config import settings

# ANSI color codes for elegant console formatting
COLOR_CODES = {
    "DEBUG": "\033[36m",  # Cyan
    "INFO": "\033[32m",  # Green
    "WARNING": "\033[33m",  # Yellow
    "ERROR": "\033[31m",  # Red
    "CRITICAL": "\033[41m\033[37m",  # Red background, white text
}
RESET_CODE = "\033[0m"


class UTCFormatter(logging.Formatter):
    """Formatter to force UTC timezone for timestamps."""

    converter = time.gmtime


class ColoredFormatter(UTCFormatter):
    """Console formatter that dynamically injects ANSI colors to the log level name."""

    def format(self, record):
        # Cache original level name to restore it for other non-colored handlers
        orig_levelname = record.levelname
        color = COLOR_CODES.get(orig_levelname, RESET_CODE)
        record.levelname = f"{color}{orig_levelname:<5}{RESET_CODE}"
        result = super().format(record)
        record.levelname = orig_levelname
        return result


def get_logger(name: str) -> logging.Logger:
    """Helper to retrieve a logger by namespace."""
    return logging.getLogger(name)


def setup_logging() -> None:
    """Centralized function to initialize and configure application-wide logging handlers."""
    # 1. Parse configuration parameters
    log_level_name = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_name, logging.INFO)
    log_dir = settings.LOG_DIRECTORY
    to_file = settings.LOG_TO_FILE

    # Custom log format string
    log_format = "%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | line %(lineno)d | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Define base formatters
    file_formatter = UTCFormatter(fmt=log_format, datefmt=date_format)
    console_formatter = ColoredFormatter(fmt=log_format, datefmt=date_format)

    # 2. Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates on reload
    for handler in list(root_logger.handlers):
        root_logger.removeHandler(handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    # 3. Setup file loggers if enabled
    if to_file and log_dir:
        os.makedirs(log_dir, exist_ok=True)

        # Main app.log file handler
        app_file = os.path.join(log_dir, "app.log")
        app_handler = RotatingFileHandler(
            app_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        app_handler.setFormatter(file_formatter)
        app_handler.setLevel(log_level)
        root_logger.addHandler(app_handler)

        # Global error.log file handler (receives ERROR and CRITICAL levels from all loggers)
        error_file = os.path.join(log_dir, "error.log")
        error_handler = RotatingFileHandler(
            error_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        error_handler.setFormatter(file_formatter)
        error_handler.setLevel(logging.ERROR)
        root_logger.addHandler(error_handler)

        # 4. Route specific handlers for domain logs

        # GitHub Integration Logs (github.log)
        github_logger = logging.getLogger("app.services.github_service")
        github_logger.setLevel(log_level)
        github_logger.propagate = True  # Ensure it also outputs to console and app.log

        github_file = os.path.join(log_dir, "github.log")
        github_handler = RotatingFileHandler(
            github_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        github_handler.setFormatter(file_formatter)
        github_handler.setLevel(log_level)
        github_logger.addHandler(github_handler)

        # Sync service logs (sync.log)
        sync_logger = logging.getLogger("app.services.sync_service")
        sync_logger.setLevel(log_level)
        sync_logger.propagate = True

        # GitRepository db logs are also sync-related, so they go to sync.log
        repo_logger = logging.getLogger("app.repositories.github_repository")
        repo_logger.setLevel(log_level)
        repo_logger.propagate = True

        sync_file = os.path.join(log_dir, "sync.log")
        sync_handler = RotatingFileHandler(
            sync_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        sync_handler.setFormatter(file_formatter)
        sync_handler.setLevel(log_level)

        sync_logger.addHandler(sync_handler)
        repo_logger.addHandler(sync_handler)
