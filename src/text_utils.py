#!/usr/bin/env python3
"""
Text manipulation utilities
Why: Reusable text operations separate from business logic
"""


def split_text_at_boundary(text: str, max_length: int, buffer: int = 100) -> list[str]:
    """
    Split text into chunks at sentence or word boundaries
    Why: Generic text splitting logic used by Discord and potentially other message systems
    """
    if len(text) <= max_length:
        return [text]

    chunks = []
    remaining = text

    while remaining:
        if len(remaining) <= max_length:
            chunks.append(remaining)
            break

        # Try sentence boundary
        split_point = remaining.rfind(".", 0, max_length - buffer)
        if split_point == -1 or split_point < max_length // 2:
            # Try word boundary
            split_point = remaining.rfind(" ", 0, max_length)

        if split_point == -1:
            split_point = max_length
        else:
            split_point += 1

        chunk = remaining[:split_point].rstrip()
        chunks.append(chunk)
        remaining = remaining[split_point:].lstrip()

    return chunks


def format_user_prompt(author: str, message: str) -> str:
    """
    Format user message as prompt
    Why: Standardizes how user messages are formatted for AI
    """
    return f"User {author} says: {message}"


def truncate_preview(text: str, length: int = 100) -> str:
    """
    Truncate text for preview display
    Why: Consistent preview formatting across all console output
    """
    if len(text) <= length:
        return text
    return text[:length]
