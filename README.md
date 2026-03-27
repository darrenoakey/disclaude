![DisClaude Banner](assets/banner.png)

# DisClaude

Discord integration bridge to Claude Agent SDK - forward Discord messages to Claude and send responses back with intelligent debouncing.

## Overview

DisClaude bridges Discord and Claude Agent SDK, allowing users to interact with Claude through Discord channels. The system:

- Forwards Discord messages as prompts to Claude Agent SDK
- Returns Claude's responses to Discord with 1-second debouncing to minimize message spam
- Runs fully async - accepts new messages immediately even while Claude is processing
- Filters output to show only text content in Discord, logs everything else to files
- Pre-approves tool permissions so Claude can work autonomously

## Architecture

- **discord_client.py** - Discord bot with debounced message sending
- **claude_agent.py** - Claude Agent SDK wrapper with output filtering and logging
- **main.py** - Bridge orchestrator that connects Discord and Claude
- **console_utils.py** - Centralized colored terminal output
- **text_utils.py** - Text manipulation utilities
- **file_utils.py** - File I/O operations

## Setup

### Install Dependencies

```bash
./run install
```

### Configure Discord Token

Store your Discord bot token in keyring:

```bash
keyring set discord token
```

### Install as System Daemon (macOS)

To run DisClaude automatically at login:

```bash
launchctl load ~/Library/LaunchAgents/com.disclaude.bridge.plist
```

The daemon is already configured and will:
- Start automatically when you log in
- Restart if it crashes
- Log to `~/icloud/disclaude/output/disclaude.log`

## Usage

### Manual Run

```bash
./run
```

### Run Tests

All tests are real integration tests - no mocking or simulation:

```bash
./run test
```

### Lint Code

```bash
./run lint
```

## Configuration

- **Discord Channel**: Set in `src/main.py` - currently `1422706572865310813`
- **Working Directory**: `~/icloud/disclaude`
- **Output Logs**: Saved to `output/` directory (gitignored)

## How It Works

1. Bot connects to Discord and sends startup message
2. When a user posts in the channel, message is forwarded to Claude Agent SDK
3. Claude processes the request with pre-approved tools (Read, Write, Edit, Bash, Glob, Grep, WebFetch, WebSearch)
4. Claude's text responses are extracted and queued for Discord
5. Messages are debounced (1 second) and combined before sending to Discord
6. All message metadata is logged to JSON files in `output/`

## Development

Code follows strict engineering standards:

- **DRY > KISS > YAGNI** - no duplication, small functions, minimal abstraction
- Every function has a "Why" comment explaining its purpose
- 95% generic program code, 5% business logic
- All tests are real end-to-end integration tests
- No mocking, simulation, or fake implementations
- All code must pass `dazpycheck` validation

## License

This project is licensed under [CC BY-NC 4.0](https://darren-static.waft.dev/license) - free to use and modify, but no commercial use without permission.