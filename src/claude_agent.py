#!/usr/bin/env python3
"""
Claude Agent SDK wrapper for async message handling
"""
import asyncio
from typing import Callable, Optional
from claude_agent_sdk import query, ClaudeAgentOptions
from colorama import Fore, Style
import json
from datetime import datetime
from pathlib import Path


class ClaudeAgent:
    """Wrapper for Claude Agent SDK with async handling"""

    def __init__(self, on_output: Callable[[str], None], working_dir: str):
        self.on_output = on_output
        self.working_dir = working_dir
        self.active_query_task: Optional[asyncio.Task] = None
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.processor_task: Optional[asyncio.Task] = None
        self.output_dir = Path(working_dir) / "output"
        self.output_dir.mkdir(exist_ok=True)

    async def start(self):
        """Start the message processor"""
        self.processor_task = asyncio.create_task(self._process_messages())

    async def send_prompt(self, prompt: str):
        """Send a prompt to Claude immediately"""
        print(f"{Fore.YELLOW}📤 Sending to Claude: {prompt[:100]}...{Style.RESET_ALL}")

        # Cancel any active query
        if self.active_query_task and not self.active_query_task.done():
            self.active_query_task.cancel()
            try:
                await self.active_query_task
            except asyncio.CancelledError:
                pass

        # Queue the new prompt
        await self.message_queue.put(prompt)

    async def _process_messages(self):
        """Process messages from the queue"""
        while True:
            try:
                # Get next prompt
                prompt = await self.message_queue.get()

                # Process it
                self.active_query_task = asyncio.create_task(self._query_claude(prompt))
                await self.active_query_task

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"{Fore.RED}❌ Error processing message: {e}{Style.RESET_ALL}")
                await asyncio.sleep(1.0)

    async def _query_claude(self, prompt: str):
        """Query Claude and stream responses"""
        accumulated_text = []
        log_entries = []
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Configure Claude with full permissions
        options = ClaudeAgentOptions(
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep", "WebFetch", "WebSearch"],
            working_directory=self.working_dir
        )

        try:
            print(f"{Fore.CYAN}🤖 Claude processing...{Style.RESET_ALL}")

            async for message in query(prompt=prompt, options=options):
                # Log everything to output directory
                log_entries.append({
                    "timestamp": datetime.now().isoformat(),
                    "type": type(message).__name__,
                    "message": str(message)
                })

                # Extract only assistant text content for Discord
                if hasattr(message, '__class__') and message.__class__.__name__ == 'AssistantMessage':
                    if hasattr(message, 'content'):
                        for block in message.content:
                            if hasattr(block, '__class__') and block.__class__.__name__ == 'TextBlock':
                                if hasattr(block, 'text'):
                                    accumulated_text.append(block.text)

            # Write full log to file
            log_file = self.output_dir / f"session_{session_id}.json"
            with open(log_file, 'w') as f:
                json.dump(log_entries, f, indent=2)

            # Send only text content to Discord
            if accumulated_text:
                combined = "\n".join(accumulated_text)
                self.on_output(combined)
            else:
                self.on_output("✓ Done (no text output)")

            print(f"{Fore.GREEN}✅ Claude completed response{Style.RESET_ALL}")

        except asyncio.CancelledError:
            print(f"{Fore.YELLOW}⚠️ Claude query cancelled{Style.RESET_ALL}")
            raise
        except Exception as e:
            print(f"{Fore.RED}❌ Claude error: {e}{Style.RESET_ALL}")
            self.on_output(f"Error: {e}")

    async def stop(self):
        """Stop the agent"""
        if self.active_query_task:
            self.active_query_task.cancel()
        if self.processor_task:
            self.processor_task.cancel()
