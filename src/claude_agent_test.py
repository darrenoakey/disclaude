#!/usr/bin/env python3
"""
Tests for Claude Agent wrapper - real integration tests
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from claude_agent import ClaudeAgent


@pytest.mark.asyncio
async def test_claude_agent_initialization():
    """Test Claude agent can be initialized"""
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
    """Test Claude agent can process a simple math query"""
    outputs = []

    def capture_output(text):
        outputs.append(text)

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = ClaudeAgent(on_output=capture_output, working_dir=tmpdir)
        await agent.start()

        await agent.send_prompt("What is 7 + 5? Reply with just the number.")

        # Wait for response
        await asyncio.sleep(15)

        # Should have received output
        assert len(outputs) > 0
        # Should contain the answer
        combined = "".join(outputs)
        assert "12" in combined

        await agent.stop()


@pytest.mark.asyncio
async def test_claude_agent_creates_log_files():
    """Test that Claude agent creates log files in output directory"""
    outputs = []

    def capture_output(text):
        outputs.append(text)

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = ClaudeAgent(on_output=capture_output, working_dir=tmpdir)
        await agent.start()

        await agent.send_prompt("Say hello")
        await asyncio.sleep(10)

        # Check output directory was created
        output_dir = Path(tmpdir) / "output"
        assert output_dir.exists()

        # Check log file was created
        log_files = list(output_dir.glob("session_*.json"))
        assert len(log_files) > 0

        await agent.stop()


@pytest.mark.asyncio
async def test_claude_agent_filters_output():
    """Test that Claude agent filters to only text output"""
    outputs = []

    def capture_output(text):
        outputs.append(text)

    with tempfile.TemporaryDirectory() as tmpdir:
        agent = ClaudeAgent(on_output=capture_output, working_dir=tmpdir)
        await agent.start()

        await agent.send_prompt("Reply with: Hello test")
        await asyncio.sleep(10)

        # Should have output
        assert len(outputs) > 0

        # Output should not contain system messages or metadata
        combined = "".join(outputs)
        assert "AssistantMessage" not in combined
        assert "ResultMessage" not in combined
        assert "SystemMessage" not in combined

        await agent.stop()
