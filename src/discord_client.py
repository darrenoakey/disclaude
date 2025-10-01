#!/usr/bin/env python3
"""
Discord client for sending/receiving messages with debouncing
Why: Manages Discord bot connection and message handling
"""

import asyncio
import discord
from discord.ext import commands
import keyring
import time
from typing import Optional, Callable
from collections import deque
from dataclasses import dataclass
from console_utils import print_success, print_error, print_discord_message
from text_utils import split_text_at_boundary


DISCORD_MAX_LENGTH = 2000
DEBOUNCE_SECONDS = 1.0


@dataclass
class PendingMessage:
    """A message waiting to be sent after debounce period"""

    content: str
    timestamp: float


def get_discord_token() -> str:
    """Get Discord token from keyring - Why: Centralizes credential access"""
    token = keyring.get_password("discord", "token")
    if not token:
        raise RuntimeError("Discord token not found. Use: keyring set discord token YOUR_TOKEN")
    return token


def split_message(text: str) -> list[str]:
    """Split message into Discord-safe chunks - Why: Discord-specific wrapper for generic text splitting"""
    return split_text_at_boundary(text, DISCORD_MAX_LENGTH)


class DiscordClient:
    """Discord client with debounced message sending - Why: Handles all Discord communication"""

    def __init__(self, channel_id: int, on_message: Optional[Callable[[str, str], None]] = None):
        self.channel_id = channel_id
        self.on_message_callback = on_message
        self.channel: Optional[discord.TextChannel] = None
        self.pending_messages: deque[PendingMessage] = deque()
        self.send_task: Optional[asyncio.Task] = None
        self.bot = self._create_bot()
        self._setup_events()

    def _create_bot(self) -> commands.Bot:
        """Create Discord bot with required intents - Why: Separates bot configuration"""
        intents = discord.Intents.default()
        intents.message_content = True
        intents.messages = True
        return commands.Bot(command_prefix="!", intents=intents)

    def _setup_events(self):
        """Setup Discord event handlers - Why: Configures bot event callbacks"""

        @self.bot.event
        async def on_ready():
            print_success(f"Discord connected: {self.bot.user}")
            self.channel = self.bot.get_channel(self.channel_id)
            if self.channel:
                print_success(f"Found channel: #{self.channel.name}")
                if not self.send_task:
                    self.send_task = asyncio.create_task(self._process_pending_messages())
            else:
                print_error(f"Channel {self.channel_id} not found")

        @self.bot.event
        async def on_message(message: discord.Message):
            if message.author.id == self.bot.user.id:
                return

            if message.channel.id == self.channel_id:
                author = str(message.author)
                content = message.content
                print_discord_message(author, content)

                if self.on_message_callback:
                    if asyncio.iscoroutinefunction(self.on_message_callback):
                        await self.on_message_callback(author, content)
                    else:
                        self.on_message_callback(author, content)

    def queue_message(self, text: str):
        """Queue a message for sending with debounce - Why: Enables debounced message aggregation"""
        if not text.strip():
            return
        msg = PendingMessage(content=text, timestamp=time.time())
        self.pending_messages.append(msg)

    async def _process_pending_messages(self):
        """Process pending messages with debouncing - Why: Aggregates messages to reduce Discord API calls"""
        accumulated = []
        last_message_time = 0.0

        while True:
            try:
                current_time = time.time()

                while self.pending_messages:
                    msg = self.pending_messages.popleft()
                    accumulated.append(msg.content)
                    last_message_time = msg.timestamp

                if accumulated and (current_time - last_message_time) >= DEBOUNCE_SECONDS:
                    combined = "\n".join(accumulated)
                    accumulated = []

                    chunks = split_message(combined)
                    for chunk in chunks:
                        if self.channel:
                            await self.channel.send(chunk)
                            await asyncio.sleep(0.5)

                await asyncio.sleep(0.1)

            except Exception as e:
                print_error(f"Error sending Discord message: {e}")
                await asyncio.sleep(1.0)

    async def start(self):
        """Start the Discord bot - Why: Entry point for Discord connection"""
        token = get_discord_token()
        await self.bot.start(token)

    async def stop(self):
        """Stop the Discord bot - Why: Clean shutdown of Discord connection"""
        if self.send_task:
            self.send_task.cancel()
        await self.bot.close()
