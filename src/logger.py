"""
Central Logger Configuration
"""

from __future__ import annotations

import logging

from src.config import LOG_FILE

logger = logging.getLogger("CyberAnalytics")

logger.setLevel(logging.INFO)

if not logger.handlers:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
