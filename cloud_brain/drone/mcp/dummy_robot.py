"""DummyDrone - a dummy (print-only) RobotProtocol implementation, so you
can see the whole MCP wiring work before any real hardware is involved.
This is the recommended starting point for your own device: subclass
crowddrop_sdk.robot_protocol.RobotProtocol, implement
identify_device_type()/get_device_status() (required - see this folder's
README's "Identity and status tools" section for why), and add whatever
action methods your own device actually supports. Replace each method's
body with a real call into your device's own SDK - see this folder's
README's "Writing a real tool function" section.

Also includes one parameterized action, move_to(lat, lon) - MCP tools
aren't limited to the zero-argument shape the eight movement methods below
use; build_command_mcp_server() (via command_handlers_from_robot()) builds
each tool's input schema straight from its method's type hints, so an
action that takes real arguments works with no extra wiring.
"""
from crowddrop_sdk.robot_protocol import RobotProtocol


class DummyDrone(RobotProtocol):
    def identify_device_type(self) -> str:
        return "A crowddrop-sdk example drone (dummy hardware, no real flight controller)."

    def get_device_status(self) -> str:
        return "battery: 100%, location: (52.4219, 13.0483), heading: 0"

    def take_off(self) -> str:
        print("  -> would spin up the rotors and climb to hover altitude")
        return "spun up the rotors and climbed to hover altitude"

    def land(self) -> str:
        print("  -> would descend and cut the rotors on touchdown")
        return "descended and cut the rotors on touchdown"

    def forward(self) -> str:
        print("  -> would pitch forward and move forward one step")
        return "pitched forward and moved forward one step"

    def backward(self) -> str:
        print("  -> would pitch backward and move backward one step")
        return "pitched backward and moved backward one step"

    def strafe_left(self) -> str:
        print("  -> would roll left and move sideways one step")
        return "rolled left and moved sideways one step"

    def strafe_right(self) -> str:
        print("  -> would roll right and move sideways one step")
        return "rolled right and moved sideways one step"

    def turn_left(self) -> str:
        print("  -> would yaw left by a fixed angle")
        return "yawed left by a fixed angle"

    def turn_right(self) -> str:
        print("  -> would yaw right by a fixed angle")
        return "yawed right by a fixed angle"

    def move_to(self, lat: float, lon: float) -> str:
        """Parameterized example: called with {"lat": ..., "lon": ...}, not
        with no arguments like the movement methods above."""
        print(f"  -> would fly to ({lat}, {lon})")
        return f"now heading to ({lat}, {lon})"
