#!/usr/bin/env python3
"""
Tests for Discord client - real integration tests
"""

import pytest
import asyncio
from discord_client import split_message, DISCORD_MAX_LENGTH, DiscordClient, get_discord_token


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
    part2 = " " + "y" * 500
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
    assert recombined.replace(" ", "") == text.replace(" ", "")


def test_get_discord_token():
    """Test Discord token can be retrieved from keyring"""
    token = get_discord_token()
    assert token is not None
    assert len(token) > 0


TEST_CHANNEL_ID = 1422875238794006651


@pytest.mark.asyncio
async def test_discord_client_connection():
    """Test Discord client can connect to Discord"""
    received_messages = []

    def handle_message(author: str, content: str):
        received_messages.append((author, content))

    client = DiscordClient(channel_id=TEST_CHANNEL_ID, on_message=handle_message)

    client_task = asyncio.create_task(client.start())
    await asyncio.sleep(5)

    # Should be connected
    assert client.bot.user is not None
    assert client.channel is not None

    await client.stop()
    client_task.cancel()
    try:
        await client_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_discord_client_send_message():
    """Test Discord client can send messages"""
    client = DiscordClient(channel_id=TEST_CHANNEL_ID)

    client_task = asyncio.create_task(client.start())
    await asyncio.sleep(3)

    # Queue a test message
    test_msg = "🧪 Test message from discord_client_test.py"
    client.queue_message(test_msg)

    # Wait for message to be sent
    await asyncio.sleep(2)

    # Message should have been sent (queue empty)
    assert len(client.pending_messages) == 0

    await client.stop()
    client_task.cancel()
    try:
        await client_task
    except asyncio.CancelledError:
        pass


@pytest.mark.asyncio
async def test_discord_client_message_debouncing():
    """Test that multiple messages are debounced correctly"""
    client = DiscordClient(channel_id=TEST_CHANNEL_ID)

    client_task = asyncio.create_task(client.start())
    await asyncio.sleep(3)

    # Queue multiple messages quickly
    client.queue_message("Message 1")
    client.queue_message("Message 2")
    client.queue_message("Message 3")

    # Should be queued
    assert len(client.pending_messages) == 3

    # Wait for debounce and send
    await asyncio.sleep(3)

    # Should be sent
    assert len(client.pending_messages) == 0

    await client.stop()
    client_task.cancel()
    try:
        await client_task
    except asyncio.CancelledError:
        pass
