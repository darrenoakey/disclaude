#!/usr/bin/env python3
"""
Tests for console utilities
"""


def test_print_functions_exist():
    """Test that all print functions are importable"""
    from console_utils import (
        print_success,
        print_error,
        print_info,
        print_warning,
        print_discord_message,
        print_outgoing,
        print_processing,
        print_output_preview,
        print_separator,
    )

    assert print_success is not None
    assert print_error is not None
    assert print_info is not None
    assert print_warning is not None
    assert print_discord_message is not None
    assert print_outgoing is not None
    assert print_processing is not None
    assert print_output_preview is not None
    assert print_separator is not None
