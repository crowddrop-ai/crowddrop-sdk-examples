# cloud-brain / drone examples

This folder walks through connecting **a drone** specifically, as a
concrete example - but if your device isn't a drone, most of it still
applies: Step 1 (registering a persona) and Option B (bringing your own MCP
server) are both embodiment-agnostic already; only Option A's wire contract
is drone-specific. See the top-level [README](../../README.md)'s "What's in
this repo" section for that distinction spelled out, and "Supported
embodiments today" for what's actually generic vs. drone-only.

Connecting a drone to CrowdDrop always starts the same way (Step 1 below),
then splits into independent options for how your drone actually talks to
CrowdDrop. These aren't a primary path and a fallback - they're different
architectures. Pick the one that matches your device; you only need one.

| | **Option A: Pub/Sub** | **Option B: Your own MCP server** | **Option C: edge-brain** |
|---|---|---|---|
| How it works | Your drone subscribes to a Google Cloud Pub/Sub topic and publishes telemetry to another | You run an [MCP](https://modelcontextprotocol.io/) server; CrowdDrop's cloud brain calls its tools directly | The LLM/tool-calling brain *and* the robot's embodiment logic both run entirely on your own device - CrowdDrop's cloud only receives lightweight status signals (location, battery, ...) |
| Your device needs | Outbound network access only (pull-based) | To be *reachable* from CrowdDrop's cloud (a tunnel, typically) | Real local inference capacity to run an LLM/tool-calling loop itself |
| Best for | A device that can't expose a local server at all | A device that can run a real server process and reach the internet | A device that wants to act autonomously and just report status, not receive live commands |
| Guide | **[`pubsub/`](pubsub/)** | **[`mcp/`](mcp/)** | **🚧 Not implemented yet** |

**Option C is not available yet.** It's `crowddrop-sdk`'s planned
`edge_brain` scenario (see `crowddrop_sdk/README.md`'s own "planned, not yet
released" note) - a fundamentally different split of responsibility from
Options A/B above, where CrowdDrop's cloud brain never calls your device's
tools or sends it commands at all, so it isn't just a third transport for
the same `cloud_brain` scenario the way B is an alternative to A. Documented
here now so the comparison is complete, not because there's a package or
example to run today.

Options A and B aren't mutually exclusive at the platform level, but a
given persona uses exactly one, not both at once.

## Step 0: become a registered developer

If you don't already have a `DEVELOPER_CREDENTIAL`, get one first via
`../../register_developer.py` at this repo's top level - self-service, no
human review (MVP: currently open, no email verification yet) - see the
[top-level README](../../README.md#step-2-become-a-registered-developer)'s
Step 2. Everything below assumes you already have one.

## Step 1: register your agent persona (`register_agent_persona.py`)

Both options need the same two things: an **agent persona** registered on
CrowdDrop's backend (the thing your device embodies - distinct from the
developer account Step 0 registered), and a device key to authenticate as
it. `register_agent_persona.py` gets you both in one call, self-service -
it reads its persona definition from **`persona.yml`**, next to it in this
folder, and sends that whole file as the `POST /agents/create` request
body. Open `persona.yml` and describe your own device there (name,
character, the `robot` block's identifier/model/location/battery) before
running this - or run it as-is first to see the demo persona work, and
come back and edit it before Step 4:

```bash
export DEVELOPER_CREDENTIAL=<from register_developer.py's .env - see Step 0 above>
export BACKEND_URL=<your CrowdDrop backend's base URL>
python register_agent_persona.py
```

This calls `POST /agents/create` once, and writes the response's device key
straight into a local `.env` file as `DRONE_DEVICE_KEY=...` (already
`.gitignore`d in this folder - never commit it). Both option guides below
read that same `DRONE_DEVICE_KEY` variable, so load it into your shell
before following either of them (e.g. `export $(cat .env | xargs)` on
macOS/Linux, or open the file and copy the value into
`$env:DRONE_DEVICE_KEY` on Windows).

`DEVELOPER_CREDENTIAL` is a separate, reusable credential from the device
key this call mints (Step 0 above) - a persona-scoped device key proves
"you are this specific persona's physical device," while the developer
credential proves "you're allowed to create personas at all." See
`register_agent_persona.py`'s own module docstring for the exact
request/response shape, and `persona.yml`'s own header comment for the
full field-by-field shape, including how its `config_key`/`robot[0].identifier`
are overridden by a `DRONE_ID` environment variable if you set one, to
stay in sync with whichever option script you run in Step 4.

Re-running this script for the same `config_key` **updates** that persona
(new `persona_body`, `about_me`, etc. take effect immediately, no restart
needed) instead of minting a second device key - your existing `.env` stays
valid.

## Step 2: pick your option

Each option is its own self-contained folder here - own README, own
scripts, nothing shared between them (each folder's dummy command
stand-ins are deliberately duplicated rather than imported across folders,
so you can read and copy just the one you need). `register_agent_persona.py`
above is the one thing genuinely shared, since both options need it before
either will work. Once Step 1 is done, `cd` into whichever folder matches
your device and follow its own README from there:

- **Option A (Pub/Sub) — [`pubsub/`](pubsub/)** (`cd pubsub`) -
  `hello_world.py` (start here) and `drone_implementation.py`, plus the
  local-testing helpers (`send_test_command.py`, `setup_emulator_topics.py`)
  that go with them.
- **Option B (your own MCP server) — [`mcp/`](mcp/)** (`cd mcp`) -
  `mcp_example.py`, plus `verify_mcp_locally.py` for testing it with no
  tunnel/device key/backend needed.
- **Option C (edge-brain)** - not implemented yet, see the table above.

If your device can't expose a local server at all (fully air-gapped except
for outbound Pub/Sub, no way to run a tunnel), Option A is the only one
that fits. Between A and B, it genuinely is a choice - read the table above
and pick.
