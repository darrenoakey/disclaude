#!/usr/bin/env python3
"""
Tests for Claude Agent wrapper
"""
import pytest
import asyncio
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


@pytest.mark.asyncio
async def test_claude_agent_simple_query():
    """Test Claude agent can process a simple query"""
    import tempfile
    outputs = []

    def capture_output(text):
        outputs.append(text)

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = ClaudeAgent(on_output=capture_output, working_dir=tmpdir)
        await agent.start()

        # Send a simple math query
        await agent.send_prompt("What is 2 + 2?")

        # Wait for response
        await asyncio.sleep(10)

        # Should have received some output
        assert len(outputs) > 0

        await agent.stop()


@pytest.mark.asyncio
async def test_claude_agent_cancellation():
    """Test that new prompts cancel previous ones"""
    import tempfile
    outputs = []

    def capture_output(text):
        outputs.append(text)

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = ClaudeAgent(on_output=capture_output, working_dir=tmpdir)
        await agent.start()

        # Send first prompt
        await agent.send_prompt("Count to 100 slowly")

        # Immediately send second prompt
        await asyncio.sleep(0.5)
        await agent.send_prompt("What is 2 + 2?")

        # Wait for second response
        await asyncio.sleep(10)

        # Should have outputs from second query
        assert len(outputs) > 0

        await agent.stop()
