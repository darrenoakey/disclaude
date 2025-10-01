#!/usr/bin/env python3
"""
Claude Agent SDK wrapper for async message handling
Why: Manages Claude Agent SDK interactions with output filtering and logging
"""

import asyncio
from typing import Callable, Optional
from claude_agent_sdk import query, ClaudeAgentOptions
from pathlib import Path
from console_utils import print_outgoing, print_processing, print_success, print_warning, print_error
from text_utils import truncate_preview
from file_utils import ensure_directory, write_json_log, get_timestamp


class ClaudeAgent:
    """Wrapper for Claude Agent SDK with async handling - Why: Bridges Discord to Claude with filtering"""

    def __init__(self, on_output: Callable[[str], None], working_dir: str):
        self.on_output = on_output
        self.working_dir = working_dir
        self.active_query_task: Optional[asyncio.Task] = None
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.processor_task: Optional[asyncio.Task] = None
        self.output_dir = Path(working_dir) / "output"
        ensure_directory(self.output_dir)

    async def start(self):
        """Start the message processor - Why: Entry point for Claude agent"""
        self.processor_task = asyncio.create_task(self._process_messages())

    async def send_prompt(self, prompt: str):
        """Send a prompt to Claude immediately - Why: Allows immediate cancellation of previous queries"""
        print_outgoing("Claude", truncate_preview(prompt))

        if self.active_query_task and not self.active_query_task.done():
            self.active_query_task.cancel()
            try:
                await self.active_query_task
            except asyncio.CancelledError:
                pass

        await self.message_queue.put(prompt)

    async def _process_messages(self):
        """Process messages from the queue - Why: Sequential processing with cancellation support"""
        while True:
            try:
                prompt = await self.message_queue.get()
                self.active_query_task = asyncio.create_task(self._query_claude(prompt))
                await self.active_query_task
            except asyncio.CancelledError:
                break
            except Exception as e:
                print_error(f"Error processing message: {e}")
                await asyncio.sleep(1.0)

    def _extract_text_from_message(self, message) -> list[str]:
        """Extract text blocks from assistant message - Why: Separates message parsing logic"""
        texts = []
        if hasattr(message, "__class__") and message.__class__.__name__ == "AssistantMessage":
            if hasattr(message, "content"):
                for block in message.content:
                    if hasattr(block, "__class__") and block.__class__.__name__ == "TextBlock":
                        if hasattr(block, "text"):
                            texts.append(block.text)
        return texts

    async def _query_claude(self, prompt: str):
        """Query Claude and stream responses - Why: Handles Claude SDK interaction with logging"""
        accumulated_text = []
        log_entries = []

        options = ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebFetch", "WebSearch"],
            cwd=self.working_dir,
        )

        try:
            print_processing("Claude")

            async for message in query(prompt=prompt, options=options):
                log_entries.append(
                    {"timestamp": get_timestamp(), "type": type(message).__name__, "message": str(message)}
                )
                accumulated_text.extend(self._extract_text_from_message(message))

            write_json_log(self.output_dir, "session", {"messages": log_entries})

            if accumulated_text:
                self.on_output("\n".join(accumulated_text))
            else:
                self.on_output("✓ Done (no text output)")

            print_success("Claude completed response")

        except asyncio.CancelledError:
            print_warning("Claude query cancelled")
            raise
        except Exception as e:
            print_error(f"Claude error: {e}")
            self.on_output(f"Error: {e}")

    async def stop(self):
        """Stop the agent - Why: Clean shutdown of Claude processing"""
        if self.active_query_task:
            self.active_query_task.cancel()
        if self.processor_task:
            self.processor_task.cancel()
