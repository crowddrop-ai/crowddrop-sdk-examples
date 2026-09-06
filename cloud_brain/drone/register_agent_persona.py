"""Step 1 of the self-service developer flow this folder's README documents:
call CrowdDrop's POST /agents/create once to bring a persona into
existence, and get back a device key. Requires a developer credential -
get one first (Step 0, self-service, no human review) via
../../register_developer.py at this repo's top level - see
crowddrop_sdk/README.md's "Getting credentials" section for the full
request/response shape.

Run this ONCE per persona, not on every process start - it is a
provisioning step, not something pubsub/hello_world.py,
pubsub/drone_implementation.py, or mcp/mcp_example.py (the sibling option
folders) ever call themselves. Re-running it for the same config_key
updates that persona's config in place (persona_body, about_me, etc.)
without minting a new device key - your existing .env stays valid.

The device key is shown exactly once, in the response, and is never
recoverable after that - this script writes it straight into a local .env
file (DRONE_DEVICE_KEY=...) instead of only printing it, since that's the
exact variable name both option folders' scripts already read. .gitignore
in this folder already excludes .env - never commit it.

Usage:
    export BACKEND_URL="https://your-crowddrop-backend.example"
    python register_agent_persona.py

DEVELOPER_CREDENTIAL doesn't need exporting by hand - it's auto-loaded
from ../../.env (the top-level register_developer.py's output) if you
haven't already exported one yourself; an explicit export still wins.

Edit persona.yml (next to this script) to describe your own device instead
of this folder's demo persona - see that file's own comments for the exact
shape, and PERSONA_YAML_PATH below if you'd rather keep your own device's
definition somewhere else entirely. persona.yml's optional `enabled: false`
soft-disables a persona (still live in Firestore, just pulled out of
CrowdDrop's active agents) without deleting it - flip it back to re-enable.

Only the DEVELOPER_CREDENTIAL that created a config_key can update it -
a mismatched credential gets a 403. There's no delete here; see this
folder's README's "Updating, disabling, or deleting your persona" section
for the DELETE /agents/{config_key} call that removes a persona (and its
device key) outright.
"""
import os
import sys
from typing import Any, Dict

import requests
import yaml
from dotenv import load_dotenv

# The top-level .env register_developer.py (Step 0) wrote
# DEVELOPER_CREDENTIAL into - load_dotenv() never overrides a variable
# already set in the real environment, so an explicit `export`/`$env:`
# still takes precedence over this.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

DEVELOPER_CREDENTIAL = os.environ.get("DEVELOPER_CREDENTIAL")
BACKEND_URL = os.environ.get("BACKEND_URL")
DRONE_ID = os.environ.get("DRONE_ID")
PERSONA_YAML_PATH = os.environ.get(
    "PERSONA_YAML_PATH", os.path.join(os.path.dirname(__file__), "persona.yml")
)
ENV_FILE_PATH = os.environ.get("ENV_FILE_PATH", os.path.join(os.path.dirname(__file__), ".env"))


def _load_persona() -> Dict[str, Any]:
    """Loads persona.yml (or PERSONA_YAML_PATH) and, if DRONE_ID is set in
    the environment, overrides config_key and robot[0].identifier with it -
    the same variable pubsub/hello_world.py and mcp/mcp_example.py already
    read, so setting it once keeps this persona and whichever option
    script you run identifying the same device without editing the YAML."""
    with open(PERSONA_YAML_PATH, "r", encoding="utf-8") as f:
        persona = yaml.safe_load(f)

    if DRONE_ID:
        persona["config_key"] = DRONE_ID
        if persona.get("robot"):
            persona["robot"][0]["identifier"] = DRONE_ID

    return persona


def _write_device_key_to_env_file(device_key: str) -> None:
    """Sets DRONE_DEVICE_KEY=<device_key> in ENV_FILE_PATH, replacing any
    existing DRONE_DEVICE_KEY line rather than duplicating it - safe to
    re-run this script."""
    lines = []
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
            lines = [line for line in f.read().splitlines() if not line.startswith("DRONE_DEVICE_KEY=")]

    lines.append(f"DRONE_DEVICE_KEY={device_key}")

    with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    try:
        os.chmod(ENV_FILE_PATH, 0o600)
    except OSError:
        pass  # best-effort - not all filesystems support chmod (e.g. some CI runners)


def main() -> None:
    if not DEVELOPER_CREDENTIAL:
        print("DEVELOPER_CREDENTIAL is not set - see this file's module docstring for how to get one.", file=sys.stderr)
        sys.exit(1)
    if not BACKEND_URL:
        print("BACKEND_URL is not set - the URL of the CrowdDrop backend to register against.", file=sys.stderr)
        sys.exit(1)

    persona = _load_persona()
    config_key = persona["config_key"]

    response = requests.post(
        f"{BACKEND_URL.rstrip('/')}/agents/create",
        json=persona,
        headers={"X-Developer-Credential": DEVELOPER_CREDENTIAL},
        timeout=30,
    )

    if response.status_code == 401:
        print("Rejected: invalid or missing developer credential.", file=sys.stderr)
        sys.exit(1)
    if response.status_code == 403:
        print(
            f"Rejected: config_key '{config_key}' was created by a different developer credential "
            "and cannot be updated with this one.",
            file=sys.stderr,
        )
        sys.exit(1)
    if response.status_code == 409:
        print(f"Rejected: {response.json().get('detail', response.text)}", file=sys.stderr)
        sys.exit(1)
    response.raise_for_status()

    body = response.json()
    print(f"config_key: {body['config_key']}")
    print(f"mcp_url:    {body['mcp_url']}")

    if body.get("created"):
        _write_device_key_to_env_file(body["device_key"])
        print(f"\nCreated a new persona. Its device key has been written to {ENV_FILE_PATH} as DRONE_DEVICE_KEY.")
        print("This is the only time it is shown - it cannot be recovered later. Do not commit .env.")
    else:
        print(
            f"\nUpdated the existing persona '{config_key}' - no new device key was minted. "
            f"Your existing DRONE_DEVICE_KEY in {ENV_FILE_PATH} (if any) is still valid."
        )


if __name__ == "__main__":
    main()
