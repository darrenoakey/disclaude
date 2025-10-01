#!/usr/bin/env python3
"""
Tests for main bridge application
"""
import pytest
import asyncio
from main import DisClaudeBridge, CHANNEL_ID


def test_channel_id_configured():
    """Test that channel ID is properly configured"""
    assert CHANNEL_ID == 1422706572865310813


@pytest.mark.asyncio
async def test_bridge_initialization():
    """Test bridge can be initialized"""
    bridge = DisClaudeBridge(CHANNEL_ID)
    assert bridge is not None
    assert bridge.channel_id == CHANNEL_ID
    assert bridge.discord_client is None
    assert bridge.claude_agent is None


@pytest.mark.asyncio
async def test_bridge_components_initialize():
    """Test bridge initializes its components"""
    bridge = DisClaudeBridge(CHANNEL_ID)

    # Start in background (don't wait for it to block)
    start_task = asyncio.create_task(bridge.start())

    # Give it time to initialize
    await asyncio.sleep(3)

    # Components should be initialized
    assert bridge.claude_agent is not None
    assert bridge.discord_client is not None

    # Stop it
    await bridge.stop()
    start_task.cancel()
    try:
        await start_task
    except asyncio.CancelledError:
        pass
