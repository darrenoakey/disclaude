#!/usr/bin/env python3
"""
Console output utilities for consistent colored terminal output
Why: Centralizes all console output formatting to avoid repetition
"""

from colorama import Fore, Style


def print_success(message: str):
    """Print success message in green with checkmark"""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def print_error(message: str):
    """Print error message in red with X mark"""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")


def print_info(message: str):
    """Print info message in cyan"""
    print(f"{Fore.CYAN}{message}{Style.RESET_ALL}")


def print_warning(message: str):
    """Print warning message in yellow"""
    print(f"{Fore.YELLOW}⚠️ {message}{Style.RESET_ALL}")


def print_discord_message(author: str, content: str):
    """Print formatted Discord message"""
    print(f"{Fore.CYAN}📨 Discord: {author}: {content}{Style.RESET_ALL}")


def print_outgoing(destination: str, preview: str):
    """Print outgoing message with preview"""
    print(f"{Fore.YELLOW}📤 Sending to {destination}: {preview}...{Style.RESET_ALL}")


def print_processing(service: str):
    """Print processing indicator"""
    print(f"{Fore.CYAN}🤖 {service} processing...{Style.RESET_ALL}")


def print_output_preview(source: str, preview: str):
    """Print output preview"""
    print(f"{Fore.GREEN}🤖 {source} output: {preview}...{Style.RESET_ALL}")


def print_separator():
    """Print visual separator"""
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
