"""Stands in for CrowdDrop's own backend, for local testing only: publishes
one command to the same topic hello_world.py listens on, so you can see the
whole loop work without a real CrowdDrop backend running. Uses the shared
DroneCommandEvent wire format from crowddrop_sdk, but talks to Pub/Sub via
the raw google-cloud-pubsub client instead of crowddrop-pubsub-sdk's
GenericPublisher - GenericPublisher.publish() returns True as soon as the
client's internal batching layer *accepts* the message, not once it's
actually been sent, which is invisible in a long-lived server process but
drops messages silently in a short one-shot script like this one that exits
right after. Calling .result() on the raw publish future blocks until
delivery is actually confirmed - nothing here is how the real backend
actually works internally, it's just enough to prove your subscriber
receives what a real command would look like.

Usage: python send_test_command.py [command]   # defaults to "take_off"
"""
import datetime
import os
import sys

from crowddrop_sdk.cloud_brain.events import DRONE_COMMANDS, DroneCommandEvent
from google.cloud import pubsub_v1

DRONE_ID = os.environ.get("DRONE_ID", "hello-world-drone")
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "hello-world")
DRONE_COMMAND_TOPIC_ID = os.environ.get("DRONE_COMMAND_TOPIC_ID", "drone-command-events")


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else "take_off"
    if command not in DRONE_COMMANDS:
        print(f"'{command}' isn't one of {DRONE_COMMANDS}")
        sys.exit(1)

    event = DroneCommandEvent(
        drone_id=DRONE_ID, command=command, issued_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    data, attributes = event.to_pubsub_message()

    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(GCP_PROJECT_ID, DRONE_COMMAND_TOPIC_ID)
    future = publisher.publish(topic_path, data, **attributes)
    try:
        future.result(timeout=10)  # blocks until the emulator/GCP actually confirms delivery
    except Exception as e:
        print(f"Publish failed: {e}")
        print("Is PUBSUB_EMULATOR_HOST set, the emulator running, and setup_emulator_topics.py already run?")
        sys.exit(1)

    print(f"Published '{command}' for drone_id='{DRONE_ID}'.")


if __name__ == "__main__":
    main()
