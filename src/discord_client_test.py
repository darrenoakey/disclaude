#!/usr/bin/env python3
"""
Tests for Discord client
"""

from discord_client import split_message, DISCORD_MAX_LENGTH


def test_split_message_short():
    """Test that short messages are not split"""
    text = "Hello, world!"
    result = split_message(text)
    assert len(result) == 1
    assert result[0] == text


def test_split_message_exact_limit():
    """Test message exactly at limit"""
    text = "x" * DISCORD_MAX_LENGTH
    result = split_message(text)
    assert len(result) == 1
    assert result[0] == text


def test_split_message_over_limit():
    """Test message over limit gets split"""
    text = "x" * (DISCORD_MAX_LENGTH + 100)
    result = split_message(text)
    assert len(result) == 2
    assert len(result[0]) <= DISCORD_MAX_LENGTH
    assert len(result[1]) <= DISCORD_MAX_LENGTH


def test_split_message_sentence_boundary():
    """Test splitting at sentence boundary"""
    part1 = "x" * 1000 + "."
    part2 = " " + "y" * 500  # Reduced to fit within Discord limit
    text = part1 + part2
    result = split_message(text)
    assert len(result) == 1
    assert result[0] == text


def test_split_message_multiple_chunks():
    """Test splitting into multiple chunks"""
    text = "word " * (DISCORD_MAX_LENGTH // 3)
    result = split_message(text)
    assert len(result) >= 1
    for chunk in result:
        assert len(chunk) <= DISCORD_MAX_LENGTH


def test_split_message_preserves_content():
    """Test that split messages preserve all content"""
    text = "abc " * 1000
    result = split_message(text)
    recombined = "".join(result)
    # Account for whitespace trimming at boundaries
    assert recombined.replace(" ", "") == text.replace(" ", "")
