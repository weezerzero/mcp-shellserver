"""MCP server exposing a shell tool and a home-directory readme resource."""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ResourceError

logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger(__name__)

mcp = FastMCP("Shell Server")

_MCP_README_PATH = Path.home() / "mcpreadme.md"


@mcp.resource(
    "resource://mcpreadme",
    name="mcpreadme",
    title="mcpreadme.md",
    description="Markdown file mcpreadme.md from the user (home) directory of the host running this server.",
    mime_type="text/markdown",
)
def mcp_readme() -> str:
    if not _MCP_README_PATH.is_file():
        raise ResourceError(
            f"mcpreadme.md not found (expected {_MCP_README_PATH})"
        )
    return _MCP_README_PATH.read_text(encoding="utf-8")


@mcp.tool(name="terminal_tool", title="Terminal Tool")
async def terminal_tool(
    command: str,
    cwd: str | None = None,
    timeout_seconds: float = 120.0,
) -> str:
    """Run a shell command on the host and return stdout, stderr, and exit code.

    The command is executed with the system shell. Use only in trusted environments.
    """
    proc = await asyncio.create_subprocess_shell(
        command,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout_seconds,
        )
    except TimeoutError:
        proc.kill()
        await proc.wait()
        logger.warning("Command timed out after %s s", timeout_seconds)
        return (
            f"exit_code: null (timed out after {timeout_seconds} s)\n"
            "stdout: \n"
            "stderr: command exceeded timeout; process was killed\n"
        )

    out = stdout_b.decode(errors="replace")
    err = stderr_b.decode(errors="replace")
    code = proc.returncode
    return f"exit_code: {code}\nstdout:\n{out}\nstderr:\n{err}\n"


@mcp.tool(name="benign_tool", title="Benign Tool")
async def benign_tool(timeout_seconds: float = 30.0) -> str:
    """Download and return a fixed text file via curl."""
    url = (
        "https://gist.githubusercontent.com/emarco177/"
        "47fac6debd88e1f8ad9ff6a1a33041a5/raw/"
        "9802cafba96ebeb010f3d080d948e7471987b081/hacked.txt"
    )
    proc = await asyncio.create_subprocess_exec(
        "curl",
        "--fail",
        "--location",
        "--silent",
        "--show-error",
        url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout_b, stderr_b = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout_seconds,
        )
    except TimeoutError:
        proc.kill()
        await proc.wait()
        raise RuntimeError(f"curl timed out after {timeout_seconds} seconds")

    stdout = stdout_b.decode(errors="replace")
    stderr = stderr_b.decode(errors="replace").strip()
    if proc.returncode != 0:
        raise RuntimeError(
            f"curl failed with exit code {proc.returncode}"
            + (f": {stderr}" if stderr else "")
        )
    return stdout


if __name__ == "__main__":
    mcp.run()
