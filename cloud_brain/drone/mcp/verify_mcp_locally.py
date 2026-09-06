"""Stands in for CrowdDrop's own cloud brain, for local testing only: starts
the exact same MCP server mcp_example.py would run (reusing
dummy_robot.py's DummyDrone via command_handlers_from_robot()), then
connects to it with a plain MCP client - the same protocol CrowdDrop's
backend speaks, just without any of CrowdDrop's own infra - lists its
tools and calls one, so you can see the whole loop work before touching a
device key, a tunnel, or a real backend.

Needs the `mcp` extra: pip install "crowddrop-sdk[mcp]" (same as
mcp_example.py - no additional dependency for this script).

Usage:
    python verify_mcp_locally.py [command] [arg=value ...]
Defaults to "take_off" with no arguments. For a tool that takes
parameters, e.g. dummy_robot.py's move_to(lat, lon):
    python verify_mcp_locally.py move_to lat=52.4 lon=13.0
"""
import asyncio
import sys

from mcp import ClientSession
from mcp.client.sse import sse_client

from crowddrop_sdk.mcp_tools import build_command_mcp_server, run_mcp_server_in_background
from crowddrop_sdk.robot_protocol import command_handlers_from_robot
from dummy_robot import DummyDrone

PORT = 8765


def _parse_args(raw_args: list) -> dict:
    """Turns ["lat=52.4", "lon=13.0"] into {"lat": 52.4, "lon": 13.0} -
    values are parsed as floats when possible, left as strings otherwise."""
    args = {}
    for raw_arg in raw_args:
        key, _, value = raw_arg.partition("=")
        try:
            args[key] = float(value)
        except ValueError:
            args[key] = value
    return args


async def _list_and_call(command: str, arguments: dict) -> None:
    async with sse_client(f"http://127.0.0.1:{PORT}/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            print(f"Tools discovered: {[t.name for t in tools]}")

            if command not in {t.name for t in tools}:
                print(f"'{command}' isn't one of the discovered tools.")
                sys.exit(1)

            print(f"Calling '{command}'({arguments})...")
            result = await session.call_tool(command, arguments)
            for content in result.content:
                if hasattr(content, "text"):
                    print(f"  -> {content.text}")
            print(f"Call completed (isError={result.isError}).")


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "take_off"
    arguments = _parse_args(sys.argv[2:])

    server = build_command_mcp_server("verify-mcp-locally", command_handlers_from_robot(DummyDrone()), port=PORT)
    run_mcp_server_in_background(server)
    print(f"MCP server listening locally on port {PORT} (no tunnel - this stays on your machine).")

    asyncio.run(_list_and_call(command, arguments))


if __name__ == "__main__":
    main()
