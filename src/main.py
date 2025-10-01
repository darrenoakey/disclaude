#!/usr/bin/env python3
"""
Main application: Bridge Discord to Claude Agent SDK
"""
import asyncio
import socket
from typing import Optional
from discord_client import DiscordClient
from claude_agent import ClaudeAgent
from colorama import Fore, Style, init


# Initialize colorama
init(autoreset=True)

# Your new Discord channel ID
CHANNEL_ID = 1422706572865310813


class DisClaudeBridge:
    """Bridge between Discord and Claude Agent SDK"""

    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.discord_client: Optional[DiscordClient] = None
        self.claude_agent: Optional[ClaudeAgent] = None

    async def _handle_discord_message(self, author: str, message: str):
        """Handle incoming Discord message"""
        print(f"{Fore.CYAN}📨 Message from {author}: {message}{Style.RESET_ALL}")

        # Format prompt with context
        prompt = f"User {author} says: {message}"

        # Send to Claude immediately
        await self.claude_agent.send_prompt(prompt)

    def _handle_claude_output(self, output: str):
        """Handle output from Claude"""
        print(f"{Fore.GREEN}🤖 Claude output: {output[:100]}...{Style.RESET_ALL}")

        # Queue for Discord (with debouncing)
        self.discord_client.queue_message(output)

    async def start(self):
        """Start the bridge"""
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}🚀 Starting DisClaude Bridge{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")

        # Initialize Claude agent with working directory
        import os
        working_dir = os.path.expanduser("~/icloud/disclaude")
        self.claude_agent = ClaudeAgent(on_output=self._handle_claude_output, working_dir=working_dir)
        await self.claude_agent.start()

        # Initialize Discord client
        self.discord_client = DiscordClient(
            channel_id=self.channel_id,
            on_message=self._handle_discord_message
        )

        # Start Discord (this will block)
        discord_task = asyncio.create_task(self.discord_client.start())

        # Wait for Discord to be ready
        await asyncio.sleep(2)

        # Send startup message
        machine_name = socket.gethostname()
        startup_msg = f"🤖 Claude Agent is online from {machine_name}"
        self.discord_client.queue_message(startup_msg)
        print(f"{Fore.GREEN}✅ Sent startup message{Style.RESET_ALL}")

        # Wait for Discord task
        await discord_task

    async def stop(self):
        """Stop the bridge"""
        print(f"{Fore.YELLOW}🛑 Stopping bridge...{Style.RESET_ALL}")
        if self.claude_agent:
            await self.claude_agent.stop()
        if self.discord_client:
            await self.discord_client.stop()


async def main():
    """Main entry point"""
    bridge = DisClaudeBridge(CHANNEL_ID)

    try:
        await bridge.start()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⚠️ Interrupted{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
    finally:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
