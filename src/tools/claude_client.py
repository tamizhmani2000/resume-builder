"""Shared Claude CLI caller for all tools."""

import subprocess


def call(system: str, user: str, timeout: int = 300) -> str:
    """Single-turn Claude call via the CLI. Returns the text response."""
    result = subprocess.run(
        ["claude", "-p", user, "--system-prompt", system, "--output-format", "text"],
        capture_output=True, text=True, timeout=timeout,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"claude CLI exited {result.returncode}")
    return result.stdout
