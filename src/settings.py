"""Application settings and configuration for the Markdown MCP server.

This module centralizes logging configuration and can be extended
for other application-wide functionality.
"""

import logging
import logging.config
import os
from pathlib import Path
from typing import Optional

import yaml


def setup_logging(config_path: Optional[str] = None) -> None:
    """Configure logging for the entire application using YAML configuration.

    Args:
        config_path: Path to the logging configuration YAML file.
                    Defaults to configs/logging.yaml in the same directory.
    """
    if config_path is None:
        config_path = Path(__file__).parent / "configs" / "logging.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        # Fallback to basic configuration if YAML file doesn't exist
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logging.getLogger(__name__).warning(
            f"Logging config file not found at {config_path}. Using basic configuration."
        )
        return

    # Ensure logs directory exists for file handler
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Allow environment variable override for log levels
        log_level = os.getenv("LOG_LEVEL", "").upper()
        if log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            # Override all logger levels with environment variable
            for logger_name in config.get("loggers", {}):
                config["loggers"][logger_name]["level"] = log_level
            if "root" in config:
                config["root"]["level"] = log_level

        logging.config.dictConfig(config)
        logging.getLogger(__name__).info("Logging configuration loaded successfully.")

    except Exception as e:
        # Fallback to basic configuration if YAML loading fails
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        logging.getLogger(__name__).error(
            f"Failed to load logging configuration from {config_path}: {e}. Using basic configuration."
        )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name.

    Args:
        name: Logger name (typically __name__ from calling module)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Automatically setup logging when module is imported
setup_logging()
