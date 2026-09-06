"""The smallest possible working example of crowddrop-sdk's cloud-brain
scenario: publish one telemetry reading, then listen for commands and turn
each one into a (dummy, print-only) drone action. No flight controller, no
real sensors, no error handling beyond what the SDK already gives you for
free - this exists to prove the wiring works, not to be production code.

Same code either way:
- Against a local Pub/Sub emulator (zero GCP credentials) - see this
  folder's README for the one-time setup.
- Against real GCP, once you have a real DRONE_ID and (for a real device)
  the agent-device-key flow crowddrop-sdk's own edge_agent.py example
  demonstrates - not repeated here, this file stays deliberately minimal.
"""
import os

from crowddrop_sdk.cloud_brain.drone.channels import DroneCommandSubscriber, DroneTelemetryPublisher
from crowddrop_sdk.cloud_brain.events import DroneCommandEvent

DRONE_ID = os.environ.get("DRONE_ID", "hello-world-drone")


# A command like "take_off" is just a string on the wire - crowddrop-sdk has
# no idea what it means physically, and never will. Turning it into a real
# drone action is entirely your job: one function per command below, each a
# dummy stand-in (print only) for now. Replace each body with a real call
# into your flight controller.
def take_off() -> None:
    print("  -> would spin up the rotors and climb to hover altitude")


def land() -> None:
    print("  -> would descend and cut the rotors on touchdown")


def forward() -> None:
    print("  -> would pitch forward and move forward one step")


def backward() -> None:
    print("  -> would pitch backward and move backward one step")


def strafe_left() -> None:
    print("  -> would roll left and move sideways one step")


def strafe_right() -> None:
    print("  -> would roll right and move sideways one step")


def turn_left() -> None:
    print("  -> would yaw left by a fixed angle")


def turn_right() -> None:
    print("  -> would yaw right by a fixed angle")


COMMAND_HANDLERS = {
    "take_off": take_off,
    "land": land,
    "forward": forward,
    "backward": backward,
    "strafe_left": strafe_left,
    "strafe_right": strafe_right,
    "turn_left": turn_left,
    "turn_right": turn_right,
}


def on_command(event: DroneCommandEvent) -> None:
    print(f"Received command: {event.command!r} (sequence={event.sequence})")
    handler = COMMAND_HANDLERS.get(event.command)
    if handler is None:
        print(f"  -> unknown command {event.command!r}, ignoring")
        return
    handler()


def main() -> None:
    print(f"Starting hello-world drone '{DRONE_ID}'...")

    latitude, longitude, heading, battery_level = 0.0, 0.0, 0.0, 100.0
    telemetry_publisher = DroneTelemetryPublisher()
    telemetry_publisher.publish_telemetry(
        drone_id=DRONE_ID, latitude=latitude, longitude=longitude, heading=heading, battery_level=battery_level
    )
    print(
        f"Published telemetry: lat={latitude}, lon={longitude}, "
        f"heading={heading}, battery={battery_level}%"
    )

    print("Listening for commands - Ctrl-C to stop.")
    command_subscriber = DroneCommandSubscriber()
    command_subscriber.pull_forever(on_command)


if __name__ == "__main__":
    main()
