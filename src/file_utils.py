#!/usr/bin/env python3
"""
File operations utilities
Why: Centralizes file I/O operations separate from business logic
"""

import json
from pathlib import Path
from datetime import datetime


def ensure_directory(path: Path):
    """
    Ensure directory exists
    Why: Standard directory creation pattern
    """
    path.mkdir(parents=True, exist_ok=True)


def write_json_log(directory: Path, prefix: str, data: dict):
    """
    Write JSON log file with timestamp
    Why: Standard logging pattern for session data
    """
    ensure_directory(directory)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.json"
    filepath = directory / filename

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    return filepath


def get_timestamp() -> str:
    """
    Get current timestamp in standard format
    Why: Consistent timestamp formatting across application
    """
    return datetime.now().isoformat()
