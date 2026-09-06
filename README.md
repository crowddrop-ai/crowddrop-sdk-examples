# crowddrop-sdk-examples

## What is CrowdDrop?

CrowdDrop runs **embodied agents** - each one an LLM-driven "brain" (a
persona: a name, a character, a system prompt) paired with a "body" that
can act and report status. CrowdDrop's own backend already runs several
kinds of body today (humanoid, drone, vehicle, ...), but those are
simulated, running inside CrowdDrop's own process. `crowddrop-sdk` is what
lets **your own, real hardware** be the body for a persona instead -
without you needing access to CrowdDrop's backend codebase at all.

## What's in this repo

This is the getting-started guide for connecting your own device via
`crowddrop-sdk` - not just "the drone examples," even though it's organized
around one concrete device (a drone) today, because that's the first
physical device CrowdDrop connected this way. Most of what's here isn't
drone-specific:

- **Registering a persona** (`register_agent_persona.py`, `POST /agents/create`)
  is completely generic - a `robot` spec (identifier, model name, location,
  battery) and a free-text description of your device's character. Nothing
  about it assumes a drone, or any particular physical form.
- **Bringing your own MCP server** (Option B, below) is also generic - the
  persona it creates has no built-in movement or sensing of any kind.
  Your own tools *are* the persona's
  capabilities, whatever they are - flight controls, a robotic arm, a
  vehicle's drive-by-wire interface, a warehouse conveyor, anything. The
  recommended way to describe them is a `crowddrop_sdk.robot_protocol.RobotProtocol`
  subclass - this is CrowdDrop's suggested starting point for *any* device,
  not just this repo's drone example (see `mcp/README.md`'s "Describing
  your device with `RobotProtocol`").
- The one genuinely drone-specific piece is **Option A** (the Pub/Sub
  transport) - its wire contract is a fixed eight-command flight vocabulary
  (`take_off`, `land`, `forward`, ...). If your device isn't a drone, this
  option isn't for you as written.

**Building a humanoid, a ground vehicle, or anything else?** Use Option B:
follow [`cloud_brain/drone/mcp/README.md`](cloud_brain/drone/mcp/README.md)
exactly, just describe your own device in `persona.yml`
(`register_agent_persona.py`'s persona definition) and write your own
`RobotProtocol` subclass instead of the eight drone methods. The folder
is named `drone/` because that's the
example CrowdDrop built and verified first, not because the mechanism
only works for drones.

- **[`cloud_brain/drone/`](cloud_brain/drone/)** - the *cloud-brain*
  scenario: the LLM/tool-calling brain stays in CrowdDrop's cloud, your
  device is a thin actuator/sensor bridge. This is the category most
  companion-computer-class hardware (Raspberry-Pi class, full Linux +
  Python, no local LLM) falls into. Start with `register_agent_persona.py`, then
  pick **Option A** (Google Cloud Pub/Sub) or **Option B** (your own MCP
  server) - see that folder's [README](cloud_brain/drone/README.md) for the
  full comparison, including **Option C** (edge-brain, not implemented
  yet - the LLM runs on-device instead of in CrowdDrop's cloud).

### Supported embodiments today

| | Option A (Pub/Sub) | Option B (your own MCP server) |
|---|---|---|
| Drone | ✅ the example this repo ships | ✅ `RobotProtocol` (`dummy_robot.py`) |
| Humanoid / ground vehicle / other | ❌ `DRONE_COMMANDS` is a drone-specific vocabulary | ✅ works today - no dedicated example folder yet, subclass `RobotProtocol` following the drone one as a template |

More scenarios (e.g. *edge-brain* - Option C above) will get their own
top-level folder here as `crowddrop-sdk` grows to support them.

## Getting started

Requires [`crowddrop-sdk`](https://pypi.org/project/crowddrop-sdk/) 0.3.0 or
later - `requirements.txt` already pins that floor, but if you're installing
some other way (e.g. `pip install "crowddrop-sdk[mcp]>=0.3.0"` directly, skipping
Step 1 below), make sure you're not on an older cached version. Earlier
releases don't match what these examples' READMEs describe: 0.1.0's
`edge_agent.py` raised a blanket `NotImplementedError` for every command
instead of dispatching to per-command stand-ins (fixed in 0.1.1), didn't log
the telemetry values it published (fixed in 0.1.2), and
`crowddrop_sdk.robot_protocol` - `RobotProtocol`/`command_handlers_from_robot()`,
the recommended way to describe a device on Option B - doesn't exist at all
before 0.3.0.

Already a registered CrowdDrop developer? Skip to Step 3. Just want to see
the wiring work first, with zero CrowdDrop credentials at all? Skip straight
to Option A's ["Run it against a local emulator"](cloud_brain/drone/pubsub/README.md#run-it-against-a-local-emulator-no-gcp-account-needed)
section instead - it needs nothing from Steps 2-3 below.

### Step 1: set up your environment

macOS/Linux (bash/zsh):
```bash
git clone <this-repo>
cd crowddrop-sdk-examples
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Windows (PowerShell):
```powershell
git clone <this-repo>
cd crowddrop-sdk-examples
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
If `Activate.ps1` is blocked by execution policy, run PowerShell as
Administrator once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
(or activate via `.venv\Scripts\activate.bat` in `cmd.exe` instead).

### Step 2: become a registered developer

macOS/Linux (bash/zsh):
```bash
export BACKEND_URL=<your CrowdDrop backend's base URL>
python register_developer.py "Your Name or Org" you@example.com
```
Windows (PowerShell):
```powershell
$env:BACKEND_URL = "<your CrowdDrop backend's base URL>"
python register_developer.py "Your Name or Org" you@example.com
```
This calls `POST /developers/register` and writes your reusable
`DEVELOPER_CREDENTIAL` straight to a local `.env` file - load it into your
shell before Step 3:
```bash
export $(cat .env | xargs)   # macOS/Linux
```
```powershell
# Windows (PowerShell)
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') { Set-Item "env:$($matches[1])" $matches[2] }
}
```
**MVP note:** registration is currently open, with no email
verification - see ["Getting credentials"](#getting-credentials) below.

### Step 3: register your agent persona

```bash
cd cloud_brain/drone
```
Open `cloud_brain/drone/persona.yml` and describe your own device there
(name, character, the `robot` block's identifier/model/location/battery) -
`register_agent_persona.py` sends that whole file as the request body
below. Or run it as-is first to see the shipped demo persona work, and
come back and edit it before Step 4:
```bash
python register_agent_persona.py
```
This registers a new **agent persona** - the thing your device embodies on
CrowdDrop, distinct from the developer account you just created in Step 2.
`BACKEND_URL` carries over from Step 2; `register_agent_persona.py` reads
`DEVELOPER_CREDENTIAL` from your shell the same way. This calls
`POST /agents/create` once and writes the response's device key to a local
`.env` file as `DRONE_DEVICE_KEY=...` - load it into your shell before
Step 4, the same way as above (`DRONE_DEVICE_KEY` instead of
`DEVELOPER_CREDENTIAL`). See
[`cloud_brain/drone/README.md`](cloud_brain/drone/README.md#step-1-register-your-agent-persona-register_agent_personapy)'s
Step 1 for how re-running this script updates an existing agent persona
instead of minting a second device key (one `DEVELOPER_CREDENTIAL` can
register any number of agent personas - re-run this step per device), and
`persona.yml`'s own header comment for its full field-by-field shape.

### Step 4: implement and run your device

This is where your device's real behavior lives - implement your own
robot's methods, exposed either as Pub/Sub command handlers (Option A) or
MCP tools via a `RobotProtocol` subclass (Option B). Pick whichever option
fits your device (see "What's in this repo" above) - each one is its own
self-contained folder, and each already ships a working dummy
implementation you can either **extend in place** or **replace outright**
with your own - neither is just a demo to run as-is and leave untouched:

- **Option A (Pub/Sub):** `pubsub/hello_world.py` is the smallest working
  example - start there and add to its `COMMAND_HANDLERS`, or copy
  `pubsub/drone_implementation.py` (the next step up, closer to a real
  drone's shape) as your own module instead.

  macOS/Linux (bash/zsh):
  ```bash
  cd pubsub
  export DRONE_ID=hello-world-drone
  python hello_world.py
  ```
  Windows (PowerShell):
  ```powershell
  cd pubsub
  $env:DRONE_ID = "hello-world-drone"
  python hello_world.py
  ```
  Full walkthrough, including how to send it a test command:
  [`pubsub/README.md`](cloud_brain/drone/pubsub/README.md).
- **Option B (your own MCP server):** `mcp/dummy_robot.py`'s `DummyDrone`
  is a `RobotProtocol` subclass - subclass `RobotProtocol` yourself
  (following `DummyDrone` as a template) with your own device's real
  action methods, or edit it directly if you'd rather adapt it in place.
  ```bash
  cd mcp
  pip install "crowddrop-sdk[mcp]>=0.3.0"
  python verify_mcp_locally.py take_off
  ```
  Full walkthrough, including running it for real against your CrowdDrop
  backend: [`mcp/README.md`](cloud_brain/drone/mcp/README.md).

## Getting credentials

Getting a **developer credential** is self-service (Step 2 above,
`register_developer.py`/`POST /developers/register`) - and, for now, open:
this is an MVP with no verification gate yet, so a `developer_name` and
`email` are all it takes. That's a deliberate, temporary trade-off, not the
intended end state - email verification is planned but not built (nothing
stops a false name/email being submitted today). The credential is
reusable either way: create and update any number of your own personas
yourself via `POST /agents/create` (Step 3, `register_agent_persona.py`), no
further manual step per persona.

An **agent device key** is one per physical device/persona, minted
automatically the first time you self-service-create a persona this way
(the older path - a human handing you one directly - is still supported
for personas CrowdDrop's own team defines).

Your device never handles a raw GCP service-account key file either way -
it trades its device key for a short-lived GCP access token automatically
(the Pub/Sub option) or presents it when registering your own MCP server
(the MCP option) - see
[`cloud_brain/drone/README.md`](cloud_brain/drone/README.md) for both.

## License

[MIT](LICENSE).
