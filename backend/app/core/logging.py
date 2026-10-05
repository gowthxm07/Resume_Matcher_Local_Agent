"""
Structured logging module for CareerCrew.
Enforces privacy guards to prevent logging full resume contents,
sensitive applicant details, or complete job description dumps.
"""

import logging
import sys
from typing import Any, Dict


class PrivacyFilter(logging.Filter):
    """
    Log filter that redacts or suppresses accidental inclusion of lengthy PII
    or raw document texts in log messages.
    """

    MAX_MESSAGE_LENGTH = 1000

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str) and len(record.msg) > self.MAX_MESSAGE_LENGTH:
            record.msg = (
                record.msg[: self.MAX_MESSAGE_LENGTH]
                + f"... [REDACTED {len(record.msg) - self.MAX_MESSAGE_LENGTH} chars for privacy/safety]"
            )
        return True


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configure structured console logging with privacy guards."""
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Avoid duplicate handlers during reload/tests
    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(numeric_level)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(PrivacyFilter())
        root_logger.addHandler(handler)

    # Set external noisemakers to WARNING
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)

    logger = logging.getLogger("careercrew")
    logger.setLevel(numeric_level)
    return logger


def sanitize_for_log(data: Any, max_len: int = 120) -> str:
    """Helper to safely represent potentially sensitive data in log strings."""
    if data is None:
        return "None"
    s = str(data).strip().replace("\n", " ").replace("\r", " ")
    if len(s) > max_len:
        return f"{s[:max_len]}... ({len(s)} chars total)"
    return s


logger = setup_logging()
