"""Tests for cli.py."""
import sys
from unittest.mock import MagicMock, patch

import pytest
import typer

from a2abase_cli.cli import app, err_console, main, main_callback


def test_main_callback_no_subcommand():
    """Test main_callback when no subcommand is invoked."""
    ctx = MagicMock()
    ctx.invoked_subcommand = None
    
    with patch("a2abase_cli.cli.console") as mock_console:
        main_callback(ctx)
        assert mock_console.print.called


def test_main_callback_with_subcommand():
    """Test main_callback when subcommand is invoked."""
    ctx = MagicMock()
    ctx.invoked_subcommand = "init"
    
    with patch("a2abase_cli.cli.console") as mock_console:
        main_callback(ctx)
        # Should not print help when subcommand exists
        assert not mock_console.print.called or mock_console.print.call_count == 0


def test_main_success():
    """Test main function with successful execution."""
    with patch("a2abase_cli.cli.app") as mock_app:
        main()
        mock_app.assert_called_once()


def test_main_keyboard_interrupt():
    """Test main function with KeyboardInterrupt."""
    with patch("a2abase_cli.cli.app", side_effect=KeyboardInterrupt()):
        with patch("a2abase_cli.cli.console") as mock_console:
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 130
            mock_console.print.assert_called_once()


def test_main_exception():
    """Test main function with exception."""
    test_error = Exception("Test error")
    with patch("a2abase_cli.cli.app", side_effect=test_error):
        with patch("a2abase_cli.cli.err_console") as mock_err_console:
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
            mock_err_console.print.assert_called_once()


def test_app_registration():
    """Test that app is properly configured."""
    assert app.info.name == "a2abase"
    assert app.info.help is not None


def test_err_console():
    """Test that err_console is configured for stderr."""
    assert err_console.file == sys.stderr

