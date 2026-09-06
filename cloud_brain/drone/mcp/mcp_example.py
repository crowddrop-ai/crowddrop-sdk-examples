"""Runs your own MCP server locally and lets CrowdDrop's cloud brain call
your tools directly, over a Cloudflare quick tunnel. See this folder's
README for the concept and how the pieces fit together, and
crowddrop_sdk.mcp_tools/crowddrop_sdk's own README for what
serve_and_register() actually does under the hood.

Uses dummy_robot.py's DummyDrone - a RobotProtocol subclass with dummy
stand-ins (eight zero-argument movement methods, a parameterized
move_to(lat, lon) example, and identify_device_type()/get_device_status()
- see this folder's README's "Identity and status tools" section for why
those two names matter) so you can see the whole thing work before any
real hardware is involved - replace them with real calls into your
device's own SDK when you're ready.

Needs the `mcp` extra: pip install "crowddrop-sdk[mcp]". Also needs
the `cloudflared` binary on PATH - see
https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/.

Before running this against the real backend, try verify_mcp_locally.py -
it exercises the exact same MCP server with no tunnel, device key, or
backend needed at all.
"""
import os

from crowddrop_sdk.mcp_tools import serve_and_register
from crowddrop_sdk.robot_protocol import command_handlers_from_robot
from dummy_robot import DummyDrone

DRONE_ID = os.environ.get("DRONE_ID", "hello-world-drone")
DEVICE_KEY = os.environ["DRONE_DEVICE_KEY"]
BACKEND_URL = os.environ["BACKEND_URL"]


def main() -> None:
    serve_and_register(
        name=DRONE_ID,
        command_handlers=command_handlers_from_robot(DummyDrone()),
        model_id=DRONE_ID,
        device_key=DEVICE_KEY,
        backend_url=BACKEND_URL,
    )


if __name__ == "__main__":
    main()
