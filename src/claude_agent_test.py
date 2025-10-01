#!/usr/bin/env python3
"""
Tests for Claude Agent wrapper
"""

import pytest
from claude_agent import ClaudeAgent


@pytest.mark.asyncio
async def test_claude_agent_initialization():
    """Test Claude agent can be initialized"""
    import tempfile

    outputs = []

    def capture_output(text):
        outputs.append(text)

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = ClaudeAgent(on_output=capture_output, working_dir=tmpdir)
        assert agent is not None
        assert agent.on_output == capture_output
        assert len(outputs) == 0


@pytest.mark.asyncio
async def test_claude_agent_start_stop():
    """Test Claude agent can start and stop"""
    import tempfile

    outputs = []

    def capture_output(text):
        outputs.append(text)

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = ClaudeAgent(on_output=capture_output, working_dir=tmpdir)
        await agent.start()
        assert agent.processor_task is not None
        await agent.stop()
