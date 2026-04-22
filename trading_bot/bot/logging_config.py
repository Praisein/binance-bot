import logging
import os
from logging.handlers import RotatingFileHandler


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "trading_bot.log")


def setup_logging() -> logging.Logger:
    """
    Configure application logging.

    Logs are written to:
        logs/trading_bot.log

    The logger records API requests, API responses, successful orders,
    and errors.
    """

    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.INFO)

    # Prevent duplicate logs if setup_logging() is called more than once
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger