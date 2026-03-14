"""Unit tests for MCP server utility functions."""

import sys
import os
import io

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp_server.utils import log, redirect_stdout_to_stderr


def test_log_writes_to_stderr(capsys):
    log("hello from test")
    captured = capsys.readouterr()
    assert "hello from test" in captured.err
    assert captured.out == ""


def test_log_does_not_touch_stdout(capsys):
    log("only stderr please")
    captured = capsys.readouterr()
    assert captured.out == ""


def test_redirect_stdout_captures_print(capsys):
    with redirect_stdout_to_stderr():
        print("this should go to stderr")
    captured = capsys.readouterr()
    assert "this should go to stderr" in captured.err
    assert captured.out == ""


def test_redirect_stdout_restores_after_context(capsys):
    with redirect_stdout_to_stderr():
        pass
    # After context, print() should write to real stdout again
    print("back to stdout")
    captured = capsys.readouterr()
    assert "back to stdout" in captured.out


def test_redirect_stdout_restores_on_exception(capsys):
    original = sys.stdout
    try:
        with redirect_stdout_to_stderr():
            raise ValueError("intentional")
    except ValueError:
        pass
    assert sys.stdout is original


def test_redirect_nested_prints(capsys):
    with redirect_stdout_to_stderr():
        print("line one")
        print("line two")
    captured = capsys.readouterr()
    assert "line one" in captured.err
    assert "line two" in captured.err
    assert captured.out == ""
