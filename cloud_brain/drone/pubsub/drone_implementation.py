"""A closer-to-real drone implementation than hello_world.py: real
device-key -> GCP-token auth (when you have a device key), a periodic
telemetry heartbeat instead of a single reading, and the two integration
points (handle_command, read_battery_and_gps) you'd actually fill in to
drive a real flight controller and read real sensors.

This runs crowddrop-sdk's own edge_agent.py, which ships inside the
crowddrop-sdk package itself - kept here as a thin runner (not a second
implementation to maintain) so it's easy to find and run right alongside
hello_world.py. See this folder's README for what it adds over
hello_world.py and how to run it.

DRONE_DEVICE_KEY doesn't need exporting by hand - it's auto-loaded from
../.env (register_agent_persona.py's output, Step 1) if you haven't
already exported one yourself; an explicit export still wins.
"""
import os

from dotenv import load_dotenv

from crowddrop_sdk.cloud_brain.drone.edge_agent import main

if __name__ == "__main__":
    # The cloud_brain/drone/.env register_agent_persona.py (Step 1) wrote
    # DRONE_DEVICE_KEY into - load_dotenv() never overrides a variable
    # already set in the real environment, so an explicit `export`/`$env:`
    # still wins. Must run before main() reads its own env vars.
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    main()
