"""One-time, local-emulator-only setup: creates the topics/subscription
hello_world.py and send_test_command.py need. Uses the plain
google-cloud-pubsub client directly (already a transitive dependency) rather
than the gcloud CLI, so this repo never needs anything beyond `pip install`.

Not needed against real GCP - there, these resources are provisioned ahead
of time by CrowdDrop's own infra, the same way any production Pub/Sub setup
works.
"""
import os

from google.api_core.exceptions import AlreadyExists
from google.cloud import pubsub_v1

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "hello-world")
COMMAND_TOPIC_ID = os.environ.get("DRONE_COMMAND_TOPIC_ID", "drone-command-events")
COMMAND_SUBSCRIPTION_ID = "drone-command-events-drone"
TELEMETRY_TOPIC_ID = os.environ.get("DRONE_TELEMETRY_TOPIC_ID", "drone-telemetry-events")


def main() -> None:
    if not os.environ.get("PUBSUB_EMULATOR_HOST"):
        print("PUBSUB_EMULATOR_HOST is not set - refusing to run against real GCP.")
        raise SystemExit(1)

    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()

    command_topic_path = publisher.topic_path(PROJECT_ID, COMMAND_TOPIC_ID)
    telemetry_topic_path = publisher.topic_path(PROJECT_ID, TELEMETRY_TOPIC_ID)
    command_subscription_path = subscriber.subscription_path(PROJECT_ID, COMMAND_SUBSCRIPTION_ID)

    for topic_path in (command_topic_path, telemetry_topic_path):
        try:
            publisher.create_topic(name=topic_path)
            print(f"Created topic {topic_path}")
        except AlreadyExists:
            print(f"Topic already exists: {topic_path}")

    try:
        subscriber.create_subscription(name=command_subscription_path, topic=command_topic_path)
        print(f"Created subscription {command_subscription_path}")
    except AlreadyExists:
        print(f"Subscription already exists: {command_subscription_path}")


if __name__ == "__main__":
    main()
