# shellserver

A small [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server built with the [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk) (`FastMCP`). It exposes one tool that runs shell commands on the machine where the server process runs.

## Requirements

- Python **3.14+** (see `pyproject.toml`)
- [uv](https://docs.astral.sh/uv/) for installing and running dependencies

## Setup

Clone or copy this repository, then from the project root:

```bash
uv sync
```

## Running the server

The server uses **stdio** transport (the default for `FastMCP`).

```bash
uv run python server.py
```

Do not pipe extra data to stdout from the server process; MCP uses stdout for JSON-RPC. Logging in `server.py` is directed to stderr.

## Tool: `terminal_tool`

| Parameter         | Type   | Required | Default | Description                                      |
|------------------|--------|----------|---------|--------------------------------------------------|
| `command`        | string | yes      | —       | Shell command to run                             |
| `cwd`            | string | no       | —       | Working directory for the subprocess             |
| `timeout_seconds`| number | no       | `120`   | Seconds to wait before killing the process     |

The tool returns a single text block containing `exit_code`, `stdout`, and `stderr`. If the command exceeds the timeout, the process is terminated and the response indicates a timeout.

## Connecting a client (example of running locally)

Point your MCP host at `uv` with this project as the working directory. Example configuration shape:

```json
{
  "mcpServers": {
    "shellserver": {
      "command": "uv",
      "args": ["run", "python", "server.py"],
      "cwd": "/absolute/path/to/shellserver"
    }
  }
}
```

Adjust the key name and `cwd` to match your editor or client.

## Security

This server **executes arbitrary shell commands** on the host. Anyone who can invoke MCP tools against this server effectively has shell access to that machine. Use only on trusted hosts, with trusted clients, and with clear understanding of the risk.
