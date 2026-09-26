"""Logging Configuration for SOC-Style Event Tracing

Provides structured, timestamped logging for the defensive analysis pipeline.
"""

import logging
import sys
from app.core.config import settings


def configure_logging() -> logging.Logger:
    """Configures structured console logging for the application."""
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Root logger configuration
    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logger = logging.getLogger("phishing_analyzer")
    logger.setLevel(level)
    return logger


logger = configure_logging()
