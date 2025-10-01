#!/usr/bin/env python3
"""
Main application: Bridge Discord to Claude Agent SDK
Why: Coordinates Discord and Claude integration
"""

import asyncio
import socket
import os
from typing import Optional
from discord_client import DiscordClient
from claude_agent import ClaudeAgent
from console_utils import print_info, print_success, print_separator, print_output_preview, print_error, print_warning
from text_utils import format_user_prompt, truncate_preview
from colorama import init


init(autoreset=True)

CHANNEL_ID = 1422706572865310813
WORKING_DIR = os.path.expanduser("~/icloud/disclaude")


class DisClaudeBridge:
    """Bridge between Discord and Claude Agent SDK - Why: Main orchestrator of the system"""

    def __init__(self, channel_id: int, working_dir: str):
        self.channel_id = channel_id
        self.working_dir = working_dir
        self.discord_client: Optional[DiscordClient] = None
        self.claude_agent: Optional[ClaudeAgent] = None

    async def _handle_discord_message(self, author: str, message: str):
        """Handle incoming Discord message - Why: Entry point for user requests"""
        prompt = format_user_prompt(author, message)
        await self.claude_agent.send_prompt(prompt)

    def _handle_claude_output(self, output: str):
        """Handle output from Claude - Why: Routes Claude responses back to Discord"""
        print_output_preview("Claude", truncate_preview(output))
        self.discord_client.queue_message(output)

    async def start(self):
        """Start the bridge - Why: Initializes and connects all components"""
        print_separator()
        print_info("🚀 Starting DisClaude Bridge")
        print_separator()

        self.claude_agent = ClaudeAgent(on_output=self._handle_claude_output, working_dir=self.working_dir)
        await self.claude_agent.start()

        self.discord_client = DiscordClient(channel_id=self.channel_id, on_message=self._handle_discord_message)

        discord_task = asyncio.create_task(self.discord_client.start())
        await asyncio.sleep(2)

        startup_msg = f"🤖 Claude Agent is online from {socket.gethostname()}"
        self.discord_client.queue_message(startup_msg)
        print_success("Sent startup message")

        await discord_task

    async def stop(self):
        """Stop the bridge - Why: Clean shutdown of all components"""
        print_warning("Stopping bridge...")
        if self.claude_agent:
            await self.claude_agent.stop()
        if self.discord_client:
            await self.discord_client.stop()


async def main():
    """Main entry point - Why: Application startup"""
    bridge = DisClaudeBridge(CHANNEL_ID, WORKING_DIR)

    try:
        await bridge.start()
    except KeyboardInterrupt:
        print_warning("\nInterrupted")
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
