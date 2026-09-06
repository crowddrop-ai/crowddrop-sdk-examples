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
"""
from crowddrop_sdk.cloud_brain.drone.edge_agent import main

if __name__ == "__main__":
    main()
