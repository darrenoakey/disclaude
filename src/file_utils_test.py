#!/usr/bin/env python3
"""
Tests for file utilities
"""

import tempfile
from pathlib import Path
from file_utils import ensure_directory, write_json_log, get_timestamp


def test_ensure_directory():
    """Test directory creation"""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "subdir" / "nested"
        ensure_directory(test_dir)
        assert test_dir.exists()
        assert test_dir.is_dir()


def test_write_json_log():
    """Test JSON log writing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        log_dir = Path(tmpdir)
        data = {"test": "data", "number": 42}
        filepath = write_json_log(log_dir, "test", data)

        assert filepath.exists()
        assert filepath.suffix == ".json"
        assert "test" in filepath.name

        import json

        with open(filepath) as f:
            loaded = json.load(f)
        assert loaded == data


def test_get_timestamp():
    """Test timestamp generation"""
    ts = get_timestamp()
    assert isinstance(ts, str)
    assert len(ts) > 0
    # Should be ISO format
    assert "T" in ts or "-" in ts
