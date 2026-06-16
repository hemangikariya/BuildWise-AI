import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Any

# Ensure logs directory exists inside workspace
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)

# Standard Formatter
log_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def setup_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers if logger is reinitialized
    if logger.handlers:
        return logger

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, log_file), maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)

    return logger

# Define individual loggers
system_logger = setup_logger("system", "system.log")
api_logger = setup_logger("api", "api.log")
auth_logger = setup_logger("auth", "auth.log")
agent_logger = setup_logger("agent", "agent.log")
audit_logger = setup_logger("audit", "audit.log")

def log_system_event(level: str, module: str, message: str, exception: Any = None):
    """Utility function to log system events and handle DB logging hook if needed later."""
    lvl = getattr(logging, level.upper(), logging.INFO)
    system_logger.log(lvl, f"[{module}] {message}")
    if exception and lvl >= logging.ERROR:
        system_logger.exception(exception)
