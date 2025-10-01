#!/usr/bin/env python3
"""
Discord client for sending/receiving messages with debouncing
"""
import asyncio
import discord
from discord.ext import commands
import keyring
import time
from typing import Optional, Callable
from collections import deque
from dataclasses import dataclass
from colorama import Fore, Style


DISCORD_MAX_LENGTH = 2000
DEBOUNCE_SECONDS = 1.0


@dataclass
class PendingMessage:
    """A message waiting to be sent after debounce period"""
    content: str
    timestamp: float


def get_discord_token() -> str:
    """Get Discord token from keyring"""
    token = keyring.get_password("discord", "token")
    if not token:
        raise RuntimeError("Discord token not found. Use: keyring set discord token YOUR_TOKEN")
    return token


def split_message(text: str) -> list[str]:
    """Split message into Discord-safe chunks"""
    if len(text) <= DISCORD_MAX_LENGTH:
        return [text]

    chunks = []
    remaining = text

    while remaining:
        if len(remaining) <= DISCORD_MAX_LENGTH:
            chunks.append(remaining)
            break

        # Try sentence split
        split_point = remaining.rfind(".", 0, DISCORD_MAX_LENGTH - 100)
        if split_point == -1 or split_point < DISCORD_MAX_LENGTH // 2:
            # Try word split
            split_point = remaining.rfind(" ", 0, DISCORD_MAX_LENGTH)

        if split_point == -1:
            split_point = DISCORD_MAX_LENGTH
        else:
            split_point += 1

        chunk = remaining[:split_point].rstrip()
        chunks.append(chunk)
        remaining = remaining[split_point:].lstrip()

    return chunks


class DiscordClient:
    """Discord client with debounced message sending"""

    def __init__(self, channel_id: int, on_message: Optional[Callable[[str, str], None]] = None):
        self.channel_id = channel_id
        self.on_message_callback = on_message
        self.channel: Optional[discord.TextChannel] = None

        # Message debouncing
        self.pending_messages: deque[PendingMessage] = deque()
        self.send_task: Optional[asyncio.Task] = None

        # Setup Discord bot
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        self.bot = commands.Bot(command_prefix="!", intents=intents)

        self._setup_events()

    def _setup_events(self):
        """Setup Discord event handlers"""

        @self.bot.event
        async def on_ready():
            print(f"{Fore.GREEN}✅ Discord connected: {self.bot.user}{Style.RESET_ALL}")
            self.channel = self.bot.get_channel(self.channel_id)
            if self.channel:
                print(f"{Fore.GREEN}✅ Found channel: #{self.channel.name}{Style.RESET_ALL}")
                # Start message sender
                if not self.send_task:
                    self.send_task = asyncio.create_task(self._process_pending_messages())
            else:
                print(f"{Fore.RED}❌ Channel {self.channel_id} not found{Style.RESET_ALL}")

        @self.bot.event
        async def on_message(message: discord.Message):
            # Ignore own messages
            if message.author.id == self.bot.user.id:
                return

            # Only process messages from target channel
            if message.channel.id == self.channel_id:
                author = str(message.author)
                content = message.content

                print(f"{Fore.CYAN}📨 Discord: {author}: {content}{Style.RESET_ALL}")

                if self.on_message_callback:
                    if asyncio.iscoroutinefunction(self.on_message_callback):
                        await self.on_message_callback(author, content)
                    else:
                        self.on_message_callback(author, content)

    def queue_message(self, text: str):
        """Queue a message for sending with debounce"""
        if not text.strip():
            return

        msg = PendingMessage(content=text, timestamp=time.time())
        self.pending_messages.append(msg)

    async def _process_pending_messages(self):
        """Process pending messages with debouncing"""
        accumulated = []
        last_message_time = 0.0

        while True:
            try:
                current_time = time.time()

                # Collect pending messages
                while self.pending_messages:
                    msg = self.pending_messages.popleft()
                    accumulated.append(msg.content)
                    last_message_time = msg.timestamp

                # If we have messages and debounce period passed, send them
                if accumulated and (current_time - last_message_time) >= DEBOUNCE_SECONDS:
                    # Combine all accumulated messages
                    combined = "\n".join(accumulated)
                    accumulated = []

                    # Split if needed and send
                    chunks = split_message(combined)
                    for chunk in chunks:
                        if self.channel:
                            await self.channel.send(chunk)
                            await asyncio.sleep(0.5)  # Brief pause between chunks

                await asyncio.sleep(0.1)  # Check frequently

            except Exception as e:
                print(f"{Fore.RED}❌ Error sending Discord message: {e}{Style.RESET_ALL}")
                await asyncio.sleep(1.0)

    async def start(self):
        """Start the Discord bot"""
        token = get_discord_token()
        await self.bot.start(token)

    async def stop(self):
        """Stop the Discord bot"""
        if self.send_task:
            self.send_task.cancel()
        await self.bot.close()
