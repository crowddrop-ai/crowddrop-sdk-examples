"""Same as mcp_example.py, but tunnels through CrowdDrop's own self-hosted
`frp` relay (Workstream O) instead of a Cloudflare quick tunnel - useful
where cloudflared/localhost.run-style tunnels don't reliably deliver SSE
on your network (see crowddrop_ai_agents' docs/plans/
first_citizen_drone_connectivity/04-code-implementation.md, Workstream O,
for why), or simply to test the relay path itself.

serve_and_register() doesn't call start_crowddrop_relay_tunnel() yet (see
that function's own docstring), so this composes the same four pieces
serve_and_register() does, by hand, swapping in the relay tunnel.

Needs the `mcp` extra: pip install "crowddrop-sdk[mcp]". Also needs the
`frpc` binary on PATH - see https://github.com/fatedier/frp/releases
(same v0.61.1 this workstream's own testing verified).

Before running this against the real backend, try verify_mcp_locally.py -
it exercises the exact same MCP server with no tunnel, device key, or
backend needed at all.

DRONE_DEVICE_KEY doesn't need exporting by hand - it's auto-loaded from
../.env (register_agent_persona.py's output, Step 1) if you haven't
already exported one yourself; an explicit export still wins.

Env vars specific to the relay path (defaults match running
`crowddrop_backend`'s real docker-compose.yaml `frps` locally, with its
default TUNNEL_PARENT_DOMAIN=localhost - see that repo's
docker-compose.override.yml. If you're instead running its separate
docker-compose-pure-local-testing.yaml `frps-local`, override
SUBDOMAIN_HOST to "tunnel.local.test" to match modules/frp/frps.local.toml
there):
    RELAY_SERVER_ADDR  - frps's host, default "127.0.0.1"
    RELAY_SERVER_PORT  - frps's control port, default 7000
    SUBDOMAIN_HOST     - frps's subDomainHost, default "tunnel.localhost"
    PUBLIC_SCHEME      - default "http" - frps's vhostHTTPPort is plain
                          HTTP with no nginx/TLS in front of it locally
                          (unlike a real deployment); set to "https" only
                          once you're pointed at a real, nginx-fronted
                          deployment
    PUBLIC_PORT        - default "8080" - frps's vhostHTTPPort; set to ""
                          (empty) for a real deployment, where nginx's own
                          443 is implicit and no port should be in the URL
"""
import os
import time

from crowddrop_sdk.mcp_tools import (
    build_command_mcp_server,
    register_mcp_server,
    run_mcp_server_in_background,
    start_crowddrop_relay_tunnel,
)
from crowddrop_sdk.robot_protocol import command_handlers_from_robot
from dotenv import load_dotenv
from dummy_robot import DummyDrone

# The cloud_brain/drone/.env register_agent_persona.py (Step 1) wrote
# DRONE_DEVICE_KEY into - load_dotenv() never overrides a variable already
# set in the real environment, so an explicit `export`/`$env:` still wins.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

DRONE_ID = os.environ.get("DRONE_ID", "hello-world-drone")
DEVICE_KEY = os.environ["DRONE_DEVICE_KEY"]
BACKEND_URL = os.environ["BACKEND_URL"]

RELAY_SERVER_ADDR = os.environ.get("RELAY_SERVER_ADDR", "127.0.0.1")
RELAY_SERVER_PORT = int(os.environ.get("RELAY_SERVER_PORT", "7000"))
SUBDOMAIN_HOST = os.environ.get("SUBDOMAIN_HOST", "tunnel.localhost")
PUBLIC_SCHEME = os.environ.get("PUBLIC_SCHEME", "http")
_public_port_raw = os.environ.get("PUBLIC_PORT", "8080")
PUBLIC_PORT = int(_public_port_raw) if _public_port_raw else None

PORT = 8765


def main() -> None:
    server = build_command_mcp_server(
        DRONE_ID, command_handlers_from_robot(DummyDrone()), port=PORT, allow_external_hosts=True
    )
    run_mcp_server_in_background(server)
    print(f"{DRONE_ID}: MCP server listening locally on port {PORT}.")

    with start_crowddrop_relay_tunnel(
        local_port=PORT,
        device_key=DEVICE_KEY,
        subdomain=DRONE_ID,
        relay_server_addr=RELAY_SERVER_ADDR,
        subdomain_host=SUBDOMAIN_HOST,
        relay_server_port=RELAY_SERVER_PORT,
        public_scheme=PUBLIC_SCHEME,
        public_port=PUBLIC_PORT,
    ) as tunnel:
        sse_url = f"{tunnel.url}{server.settings.sse_path}"
        print(f"{DRONE_ID}: tunnel public at {tunnel.url}")

        result = register_mcp_server(DRONE_ID, DEVICE_KEY, sse_url, BACKEND_URL)
        print(
            f"{DRONE_ID}: registered {result.get('success_count', 0)} tool source(s) "
            f"with CrowdDrop at {sse_url}."
        )

        print(f"{DRONE_ID}: serving - Ctrl-C to stop.")
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            print(f"{DRONE_ID}: stopping.")


if __name__ == "__main__":
    main()
