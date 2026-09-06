"""Step 0, before register_agent_persona.py or anything embodiment-specific:
become a CrowdDrop developer and get a reusable DEVELOPER_CREDENTIAL. Lives
at the top level of this repo (not under cloud_brain/drone/) because it has
nothing to do with drones specifically - every embodiment's "Getting
started" guide starts here.

MVP: registration is currently open, with no email verification - anyone
who calls this gets a credential immediately. That's a deliberate,
temporary trade-off (see docs/plans/first_citizen_drone_connectivity/
04-code-implementation.md's Workstream J in the crowddrop_ai_agents repo
for the real, email-verified design this is a placeholder for), not the
intended end state - don't rely on this remaining unverified.

Usage:
    export BACKEND_URL="https://your-crowddrop-backend.example"
    python register_developer.py "Your Name or Org" you@example.com

The credential is shown exactly once, in the response, and is never
recoverable after that - this script writes it straight into a local .env
file instead of only printing it, the same pattern
cloud_brain/drone/register_agent_persona.py uses for its device key.
"""
import os
import sys

import requests

BACKEND_URL = os.environ.get("BACKEND_URL")
ENV_FILE_PATH = os.environ.get("ENV_FILE_PATH", os.path.join(os.path.dirname(__file__), ".env"))


def _write_developer_credential_to_env_file(credential: str) -> None:
    """Sets DEVELOPER_CREDENTIAL=<credential> in ENV_FILE_PATH, replacing
    any existing DEVELOPER_CREDENTIAL line rather than duplicating it -
    safe to re-run this script (e.g. after registering a second time)."""
    lines = []
    if os.path.exists(ENV_FILE_PATH):
        with open(ENV_FILE_PATH, "r", encoding="utf-8") as f:
            lines = [line for line in f.read().splitlines() if not line.startswith("DEVELOPER_CREDENTIAL=")]

    lines.append(f"DEVELOPER_CREDENTIAL={credential}")

    with open(ENV_FILE_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    try:
        os.chmod(ENV_FILE_PATH, 0o600)
    except OSError:
        pass  # best-effort - not all filesystems support chmod (e.g. some CI runners)


def main() -> None:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <developer_name> <email>", file=sys.stderr)
        sys.exit(1)
    if not BACKEND_URL:
        print("BACKEND_URL is not set - the URL of the CrowdDrop backend to register against.", file=sys.stderr)
        sys.exit(1)

    developer_name, email = sys.argv[1], sys.argv[2]

    response = requests.post(
        f"{BACKEND_URL.rstrip('/')}/developers/register",
        json={"developer_name": developer_name, "email": email},
        timeout=30,
    )
    if response.status_code == 422:
        print(f"Rejected: {response.json()}", file=sys.stderr)
        sys.exit(1)
    response.raise_for_status()

    body = response.json()
    _write_developer_credential_to_env_file(body["developer_credential"])
    print(f"Registered as '{body['developer_name']}'.")
    print(f"Developer credential written to {ENV_FILE_PATH} as DEVELOPER_CREDENTIAL.")
    print("This is the only time it is shown - it cannot be recovered later. Do not commit .env.")
    print("\nNext: cd cloud_brain/drone && python register_agent_persona.py")


if __name__ == "__main__":
    main()
