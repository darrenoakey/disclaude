#!/usr/bin/env python3
"""
Tests for text utilities
"""

from text_utils import split_text_at_boundary, format_user_prompt, truncate_preview


def test_split_text_short():
    """Test that short text is not split"""
    text = "Hello, world!"
    result = split_text_at_boundary(text, 100)
    assert len(result) == 1
    assert result[0] == text


def test_split_text_at_limit():
    """Test text exactly at limit"""
    text = "x" * 100
    result = split_text_at_boundary(text, 100)
    assert len(result) == 1


def test_split_text_over_limit():
    """Test text over limit gets split"""
    text = "x" * 250
    result = split_text_at_boundary(text, 100)
    assert len(result) >= 2


def test_format_user_prompt():
    """Test user prompt formatting"""
    result = format_user_prompt("alice", "hello")
    assert "alice" in result
    assert "hello" in result
    assert result == "User alice says: hello"


def test_truncate_preview_short():
    """Test truncate doesn't change short text"""
    text = "short"
    result = truncate_preview(text, 100)
    assert result == text


def test_truncate_preview_long():
    """Test truncate shortens long text"""
    text = "x" * 200
    result = truncate_preview(text, 100)
    assert len(result) == 100
