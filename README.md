<!--
  INSTRUCTIONS FOR STUDENTS:
  - This is a report of what was delivered in THIS submission only, and whatever doesn't change between submissions.
  - Do not append and leave outdated data; replace or upadate all content below.
  - Fill every <!-- REQUIRED - -> and <!-- TODO - -> marker.
-->

<!-- REQUIRED: Replace with your team name -->
# Team Name
FULL AURA

<!-- SECTION: Team -->
## Team Members
Cristobal Gazitua
Diego Llull
Carlos Rencoret


|       Name        | GitHub User |
|-------------------|-------------|
|Cristobal Gazitua  |crisgazitua  |
|Diego Llull        |Im-diegollull|
|Carlos Rencoret    |cjrenco      |

---

<!-- SECTION: Work Division -->
## Work Division

Diego llull — Documentación y diseño: lidera diagramas (domain, C4, sequence), QAS, constraints, README.
Carlos Rencoret — Core / Backend: parser del protocolo, TCP server, credential store, refactor a DeviceFactory (Simple Factory).
Cristobal Gazitua — Infra y UI: Terminal UI (prompt_toolkit), Dockerfile, docker-compose, GitHub Actions, tests, bonus PostgreSQL store.


---

<!-- SECTION: Incomplete Items -->
## Incomplete Items

None. All required deliverables for P1B are included:
- TUI (replaces the P1A Console UI) with arrow-key navigation and hotkeys always visible.
- Simple Factory (`DeviceFactory`) is the only place where concrete device classes are referenced.
- Design diagrams (Domain, C4, Sequence) and QAS were updated to reflect the new design and address P1A feedback.

The optional **PostgreSQL bonus** is also delivered: a `PostgresCredentialStore` adapter behind the existing `CredentialStore` interface, selected at runtime via `DATABASE_URL`, with the database running locally as a sibling container in `docker-compose.yml`.

---

<!-- SECTION: Requirements  -->
## Requirements

### Functionalities

This iteration of the CleverHome Platform delivers the following functionalities:

- **CleverHub authentication over TCP/IP**: the platform listens for incoming TCP connections from CleverHubs and validates them through an HL handshake, accepting connections with valid credentials (ACC) and rejecting unauthorized or duplicate ones (REF).
- **Pluggable credential store**: a pre-loaded set of (username, password, home_name) credentials is used to authorize CleverHub connections. Two interchangeable implementations are provided behind the abstract `CredentialStore` interface: an in-memory store (default) and a PostgreSQL-backed store (P1B bonus). Selection happens at startup via the `DATABASE_URL` environment variable, with zero changes required in the Server, Protocol, Domain, or UI layers.
- **House state monitoring (GS)**: through the TUI, the operator selects a connected hub and inspects its full state. The platform reads the locally tracked house state — built from the SU messages the hub has sent — and renders all sensor and actuator values grouped by category (Climate, Lights, Doors, Sensors, Security).
- **House state control (SS)**: through the TUI, the operator can request the platform to send state updates to a connected hub. The platform serializes an SS message and reports whether the hub accepted (OK) or rejected (ERR) the change.
- **Terminal-based UI (TUI) for the platform operator**: an interactive full-screen terminal interface built on `prompt_toolkit`. The operator navigates with arrow keys and triggers actions through hotkeys; the available key combinations are always visible in a bottom toolbar, so the operator never has to remember commands or type long input strings.
- **Concurrent hub support**: the TCP server accepts multiple CleverHubs simultaneously, each on its own thread, and tracks them by their unique home_name.
- **Simple Factory for device construction**: all smart-device instantiation flows through a single `DeviceFactory.create_device(type, **kwargs)`. The rest of the codebase never references concrete device classes (`Light`, `DoorLock`, `ProximitySensor`, `Alarm`, `HVAC`, `TemperatureSensor`) directly, which makes adding a new device type a localized change.

### Quality Attribute Scenarios

**QAS 1 — Security (Authentication)**
Aspect:    Description

Source: Unauthorized CleverHub OR external 
Stimulus: Attempts to connect with invalid or missing credentials
Artifact: TCP Server + Credential Store
Environment: Runtime, platform is online and accepting connections
Response: The platform validates credentials against the store and responds with REF (refused), closing the connection without exposing any internal information
Response Measure: 100% of unauthorized connection attempts are rejected, and no data from other houses is leaked

Justification: The platform will manage real homes with sensitive data (door locks, alarm states, occupancy patterns). Ensuring that only authenticated CleverHubs can connect is a fundamental requirement for user trust and data privacy. A breach here could allow an attacker to unlock doors or disable alarms remotely.

**QAS 2 - Maintainability/Modifiability**:

Aspect:           Description

Source:           Development team
Stimulus:         Replace the in-memory credential store with an external database (e.g., PostgreSQL)
Artifact:         Credential Store module
Environment:      Development time

Response:         The change is implemented by adding a new concrete implementation of the existing CredentialStore interface, without altering the TCP Server, TUI, Protocol Codec, or Domain layer.

Response Measure: Source code changes are confined to the src/Credentials/ package. A new file is added (e.g., postgres_credential_store.py) implementing the existing CredentialStore interface, with zero modifications in src/Server/, src/Protocol/, src/Domain/, or src/UI/. Changes in src/main.py are limited to the `_build_credential_store()` factory (no other consumer of the store is modified). Zero modifications to existing tests; new integration tests are added only for the new adapter. Configuration files (requirements.txt, docker-compose.yml) are updated as needed; these are treated as infrastructure dependencies, not design-level changes.

Justification:    The project description explicitly states that the credential store will be migrated to external storage in the future. This QAS enforces the Dependency Inversion Principle: the rest of the codebase depends on the abstract CredentialStore interface, not on its concrete implementation, so swapping the underlying storage has no propagation effect through the system. This keeps maintenance costs low and enables independent evolution of the storage layer. The QAS is empirically validated by the PostgreSQL implementation delivered as part of the P1B bonus, which required exactly the changes described above.

> **Note:** This QAS received full marks in P1A. The Response Measure was voluntarily improved in P1B to be more precise and objectively verifiable — replacing the original time-based metric with concrete, code-level constraints that can be confirmed directly from the diff. The core scenario and justification remain unchanged.


### Technical Constraints

**1. Mandatory use of Python (Tecnical Constraints )**

Description: The plataform must be developed in python, with a strict
requirement to use python hints and pass static type checking using mypy library

Justification:  This constrains the technology choices for frameworks, libraries, and tooling (e.g., mypy for type checking, pytest for testing). While Python offers excellent readability and a rich ecosystem, it may impose performance limitations for high-throughput TCP connections compared to other languages (Go, Rust, node.js). 

**2. CleverHub communication protocol over TCP/IP (Tecnical Constraints)**
Description:The communication protocol between the platform and CleverHubs is pre-defined by the CleverHub development team and cannot be modified.

Justification: The platform must implement this exact text-based protocol over TCP/IP sockets. This constrains the communication layer to work with raw sockets and custom message parsing rather than using standard protocols like HTTP/REST or MQTT. Any future changes to the protocol will be dictated by the external CleverHub team, and the platform must adapt accordingl


### Domain Model

![Domain Model](docs/images/DM.png)

The domain model represents the problem space of the CleverHome Platform from a business perspective. The platform enables users to remotely monitor and control smart devices installed in their homes. Each home has a single CleverHub — a hardware controller that acts as the sole communication bridge between the platform and the devices inside the house. The platform never interacts directly with any smart device; all communication flows through the CleverHub.
Smart devices are categorized into two families: sensors, which are read-only and report environmental data, and actuators, which can be controlled remotely to perform physical actions. The platform also keeps a historical log of sensor readings and actions performed on each house.

**CleverHome Platform**: The central system that manages houses and authenticates users

**User**: A person who accesses the platform to monitor and control their homes

**House**: A registered home in the platform, associated with users and one CleverHub

**CleverHub**: The hardware controller in each house that bridges the platform and the devices

**Log**: A historical record of sensor readings and actions performed on a house

**SmartDevice**: A general entity representing any device connected to a CleverHub

**Sensor**: A read-only device that reports data (TemperatureSensor, ProximitySensor)

**Actuator**: A controllable device that executes actions (SmartLight, DoorLock, Alarm, HVAC)

> **Note:** The professor flagged the device hierarchy as "on edge" since smart devices are mostly an implementation detail abstracted away by the CleverHub team. We chose to keep the model as is because it received full marks in P1A and the entities are still conceptually valid at the domain level — they represent the types of devices the platform is designed to understand and control, even if the CleverHub mediates all direct communication with them.

---

<!-- SECTION: Design Overview -->
## Design Overview

### C4 System Context Diagram

![System Context Diagram](docs/images/c4_system_context.png)

### C4 Containers Diagram

![Containers Diagram](docs/images/c4_containers2.png)

The system contains two containers:
- **CleverHome Platform Application** [Container: Python]: the main application process. Runs the TCP server and the Terminal UI (TUI) in the same process. Accepts incoming CleverHub connections, performs the authentication handshake, and exposes interactive screens to the operator via the terminal.
- **Credentials Database** [Container: PostgreSQL 16]: stores known CleverHubs, their associated houses, and user credentials. Accessed by the application via SQL/TCP.

The **CleverHub** and the **Home Owner** are external to the platform — the CleverHub connects over TCP/IP using the custom text protocol, and the Home Owner interacts through the terminal.

> **Note (P1B correction):** The P1A version of this diagram incorrectly showed the Console UI and the In-Memory Credential Store as separate containers. Following feedback, this was corrected. In C4, a container is a separately deployable/runnable unit. The UI and the TCP server run in the same Python process — they are not separate containers. The credential store has been moved to a real external container (PostgreSQL), which correctly justifies the cylinder shape in the diagram.

### UML Sequence Diagrams

**Authentication Flow** — shows how a CleverHub connects and authenticates against the platform. The TCP Server buffers the incoming message until the terminator, then delegates to the Protocol Handler, which uses the Codec to parse the HL message and validates credentials against the Credential Store. Three outcomes are shown: invalid credentials (REF), duplicate home name (REF), and successful authentication (ACC), after which the TCP connection persists.

![Authentication Flow](docs/images/Authentication_flow2.png)

**Monitoring Flow** — shows how the platform operator requests the current state of a connected house. The TUI calls HouseService, which asks the Protocol Handler for the local state. The handler reads from HouseRegistry (the platform's in-memory state model) and returns it as a Message(SU). HouseService then converts the wire-format state map into a House domain object via `_dict_to_house` and the TUI renders it. No TCP message is sent to the real CleverHub — state is managed locally by the platform.

![Monitoring Flow](docs/images/Monitoring_flow2.png)

**Control Flow** — shows how the platform operator sets state on a connected house. The TUI calls HouseService, which sends a Message(SS) to the Protocol Handler. The handler applies the update through HouseRegistry, which delegates to the House domain entity. House uses DeviceFactory (Simple Factory pattern) to instantiate the concrete device object (Light, DoorLock, or ProximitySensor). On success the handler returns Message(OK) and the TUI refreshes; on failure it returns Message(ERR). The same flow applies to DOOR_LOCK and PROXIMITY_SENSOR — note that ProximitySensor is read-only in production; the simulator allows forcing its value for testing purposes.

![Control Flow](docs/images/Control_flow2.png)

### Program Structure

The codebase is organized into focused modules under `src/`, each with a single responsibility:

- **`src/Protocol/`** — pure functions and data classes for the CleverHub text protocol. Contains the `Message` dataclass, `parse_message` (string → Message), and `serialize_message` (Message → string). No I/O, no sockets — fully testable in isolation.
- **`src/Credentials/`** — credential storage. Defines the abstract `CredentialStore` interface and two concrete implementations: `InMemoryCredentialStore` (default) and `PostgresCredentialStore` (selected at runtime via `DATABASE_URL`). The abstraction is the empirical anchor of the Maintainability QAS.
- **`src/Domain/`** — domain entities (`House`, `Light`, `DoorLock`, `ProximitySensor`, `TemperatureSensor`, `Alarm`, `HVAC`) and the **Simple Factory** that constructs them: `DeviceFactory.create_device(device_type, **kwargs)`. This is the only place in the codebase where concrete device classes are referenced — every other module asks the factory for devices via the `DeviceFactory.LIGHT`, `DeviceFactory.DOOR_LOCK`, ... constants.
- **`src/Server/`** — the TCP server. `CleverHomeTCPServer` is a thin transport layer that frames messages on the wire terminator and delegates parsing/dispatch to `CleverHomeProtocolHandler`. The handler authenticates hubs against the credential store, tracks connected hubs, applies state updates through the domain registry, and serializes responses.
- **`src/UI/`** — the **Terminal UI (TUI)** built on `prompt_toolkit`. `AppController` owns the screen stack and the live application loop. Each screen (`HubsListScreen`, `HouseViewScreen`, `CredentialsScreen`) implements the `Screen` interface (`container()`, `key_bindings()`, `bottom_toolbar()`), so adding a new screen is a localized change. `HouseService` adapts the wire-format state map returned by the protocol handler into rich `House` domain objects for rendering.
- **`src/main.py`** — the entry point. Builds the credential store (Postgres if `DATABASE_URL` is set, in-memory otherwise), starts the TCP server in a background daemon thread, and runs the TUI on the main thread.

The dependency direction is one-way: UI depends on Server and CredentialStore (interface), Server depends on Protocol, Domain, and CredentialStore (interface), and Protocol/Domain depend on nothing. This makes each module independently testable and replaceable.


### Dockerized Structure

The CleverHome Platform runs as two containers orchestrated by Docker Compose: the platform itself (TCP server + TUI in the same Python process) and a PostgreSQL container that backs the credential store. Splitting the TCP server from the TUI would require introducing inter-process communication that adds no value at this stage, since they share the in-memory registry of connected hubs.

- **`Dockerfile`** — builds the platform image from `python:3.12-slim`, installs dependencies from `requirements.txt`, copies the `src/` directory, and starts the application with `python -m src.main`. A `.dockerignore` excludes tests, caches, and version control metadata to keep the image small.
- **`docker-compose.yml`** — defines two services:
  - **`db`** — `postgres:16-alpine` with a healthcheck on `pg_isready` and a named volume `cleverhome_db_data` that persists credentials across restarts.
  - **`platform`** — the application container. Maps TCP port `9000` to the host, enables an interactive TTY (required by the TUI), depends on `db` being healthy, and receives the `DATABASE_URL` environment variable pointing at the `db` service so it picks the PostgreSQL credential store at startup.

The CleverHub simulator is intentionally **not** included in this compose file: the simulator represents external hardware that connects to the platform from outside. To run the simulator and connect it to the platform, the operator executes a separate `docker run` command, as documented in the next section.

---

<!-- SECTION: Usage -->
## How to Run and Use

### Prerequisites

- **Docker** (24.0 or later) with Docker Compose v2. Required to build and run the platform image, the PostgreSQL container, and the CleverHub simulator.
- **Python 3.14.3+** (only required if running the platform natively without Docker, e.g. for development).
- **A terminal with TTY support**. The TUI takes over the terminal in full-screen mode.

No other dependencies are required: the Docker image bundles Python and all Python dependencies.

### Running the Platform and Dependencies

From the repository root, build and start the platform together with the PostgreSQL container:

```bash
docker compose run --rm --service-ports platform
```

This will start the `db` container first, wait for its healthcheck to pass, and then start the `platform` container with the TUI attached to your terminal. The flag `--service-ports` is required for the TCP port `9000` to be exposed; `--rm` removes the container after it exits.

Alternatively, to run the platform natively (useful during development, falls back to the in-memory credential store):

```bash
pip install -r requirements.txt
python -m src.main
```

To run natively against a real PostgreSQL, export `DATABASE_URL` first:

```bash
export DATABASE_URL=postgresql+psycopg://cleverhome:cleverhome_pass@localhost:5432/cleverhome
python -m src.main
```

In a **separate terminal**, launch the simulator pointing at the platform:

```bash
docker run --rm -it secheverriag/cleverhub-sim:p1a host.docker.internal 9000 hub1 password123 home-a
```

- `host.docker.internal` is the special hostname that lets a container reach the host machine, where the platform is listening.
- `hub1` / `password123` / `home-a` are the username, password, and home name. They must match a registered credential in the platform's credential store.

The platform ships with the following pre-loaded credentials (see `src/main.py`):

| Username | Password       | Home Name |
|----------|----------------|-----------|
| hub1     | password123    | home-a    |
| hub2     | password456    | home-b    |

### Using the Platform

Once the platform is running, the TUI takes over the terminal in full-screen mode. There are no commands to type — every action is triggered with arrow keys or single-letter hotkeys, and the available keys for the current screen are always shown in the bottom toolbar.

The TUI has three screens:

- **Hubs List** (entry screen) — lists every currently connected CleverHub with a compact summary of its state (temperature, lights on/total, alarm status). Use `↑` / `↓` to navigate, `Enter` to inspect a hub, `c` to view registered credentials, `r` to refresh, `q` to quit.
- **House View** — shows the full state of the selected hub grouped by category: Climate (temperature, HVAC), Lights, Doors, Sensors (proximity, marked as read-only), and Security (alarm). Use `↑` / `↓` to navigate the rows, `b` to go back, `r` to refresh, `q` to quit.
- **Credentials** — lists every registered credential (`username @ home_name`) with the password masked. Use `b` to go back, `q` to quit.

### UI Screenshots

**Hubs List with no hubs connected** — shows the empty state and the bottom toolbar with all available keys.

![Hubs List — empty](docs/images/Screenshot_TUI_UI1.png)

**Hubs List with a connected CleverHub** — `home-a` is connected, showing its summary (temperature, light count, alarm status) inline.

![Hubs List — connected hub](docs/images/Screenshot_TUI_UI2.png)

**House View** — full state of `home-a` grouped by category (Climate, Lights, Doors, Sensors, Security). Read-only devices are flagged in the toolbar and inline.

![House View](docs/images/Screenshot_TUI_Ui3.png)

---

<!-- SECTION: Tests -->
## Tests

### Description

The test suite covers all core modules of the platform: protocol parsing/serialization, credential storage (both implementations), TCP transport and protocol handling, the domain model and its Simple Factory, the house service that bridges wire format and domain, and the TUI screens. All tests follow the arrange/act/assert structure explicitly, and the suite mixes unit tests (for pure logic such as the parser, the domain, and the in-memory credential store) with integration tests (for the TCP server over real sockets, and for the PostgreSQL adapter against a live database).

The suite includes both valid cases and invalid cases. The latter are essential because the platform must be robust against malformed protocol messages, wrong credentials, duplicate hub names, and missing or malformed user input. Specifically:

- **Protocol tests** validate parsing of well-formed messages (HL, GS, SS, SU, OK, ERR), serialization round-trips, and rejection of malformed input (missing terminator, unknown message type, malformed parameters).
- **Credential store tests** validate the in-memory store: correct authentication for valid credentials, rejection of wrong passwords, unknown usernames, unknown homes, and empty inputs. They also verify the encapsulation of the store (the returned credential list cannot be used to mutate internal state) and the immutability of the `Credential` dataclass.
- **PostgreSQL credential store tests** validate the database-backed adapter: schema bootstrap, `validate` against seeded rows, `list_credentials`, and idempotent seeding (re-seeding the same credential does not create duplicates). These tests run against a live PostgreSQL instance and are skipped automatically when `DATABASE_URL` is not set.
- **Domain and factory tests** validate the Simple Factory: every supported `device_type` constant produces the correct concrete class with the expected initial state, and unknown types raise `UnknownDeviceTypeError`. The house domain tests cover state transitions on lights, doors, alarms, HVAC, and the read-only invariant of sensors.
- **TCP transport and protocol handler tests** validate the full HL handshake against a running server (ACC for valid credentials, REF for invalid credentials, REF for duplicate home names, REF for non-HL first messages), as well as message framing on the wire terminator and rejection of malformed SS payloads.
- **House service tests** validate the conversion from wire-format state maps to `House` domain objects across every device category.
- **TUI screen tests** validate that each screen builds its `prompt_toolkit` container without error, registers the expected key bindings, and renders the expected content (passwords masked, empty states, disconnected hub messages).

### Running Tests

From the repository root:

```bash
pip install -r requirements.txt
pytest
```

Pytest will discover all tests under `tests/` and run them with verbose output. The same suite is executed automatically on every push and pull request via GitHub Actions.

#### Note on skipped tests

A plain `pytest` run reports `96 passed, 7 skipped`. The 7 skipped tests are the **PostgreSQL integration tests** in `tests/test_postgres_credential_store.py`, marked with `pytest.mark.skipif(DATABASE_URL is None, ...)`. They are skipped — not failed — because they require a live PostgreSQL instance to run against. This is a deliberate design choice that follows the standard separation between fast unit tests (which run anywhere, anytime) and integration tests with external dependencies (which run only when explicitly asked).

There are two ways to execute the 7 skipped tests against a real database.

**Option A — recommended: run the test suite inside the platform container.** This does not require installing `sqlalchemy` or `psycopg` on the host machine and works identically on macOS, Linux, and Windows:

```bash
docker compose up -d --wait db
export DATABASE_URL=postgresql+psycopg://cleverhome:cleverhome_pass@cleverhome-db:5432/cleverhome
docker run --rm --network sd-project-group-8-full-aura_default -v "$(pwd):/app" -w /app -e DATABASE_URL --entrypoint pytest cleverhome-platform:p1b
```

Expected output: `103 passed` (all 96 regular tests plus the 7 PostgreSQL integration tests).

**Option B — native: run pytest on the host.** Requires `sqlalchemy` and `psycopg[binary]` to be installed locally (`pip install -r requirements.txt`):

```bash
docker compose up -d --wait db
export DATABASE_URL=postgresql+psycopg://cleverhome:cleverhome_pass@localhost:5432/cleverhome
pytest tests/test_postgres_credential_store.py -v
```

All 7 tests should report `PASSED` once the database is reachable. The bonus PostgreSQL implementation is also exercised end-to-end whenever the platform is launched via `docker compose run --rm --service-ports platform`, since the `platform` container connects to the `db` container at startup and uses it as the live credential store.

When done, tear down the database container with:

```bash
docker compose down -v
```

**Why GitHub Actions does not run the 7 PostgreSQL tests automatically.** The CI workflow in `.github/workflows/ci.yml` does not spin up a PostgreSQL service, so on every push the 7 integration tests are reported as `SKIPPED`. This is intentional: enabling them would require adding a `services: postgres` block to the workflow, which is straightforward but goes beyond what the assignment explicitly requires for the bonus. The bonus itself is empirically validated in two ways that do not depend on CI — (a) running the snippet above against a local `db` container, and (b) launching the platform via `docker compose run --rm --service-ports platform`, which connects to the live PostgreSQL container at startup. Future iterations may add the `services: postgres` block to the CI workflow so that the 7 tests run on every push as well.


### Type Checking

The project uses strict mypy type checking, configured in `mypy.ini`. To run it locally:

```bash
mypy src/ tests/
```

Type checking must complete with no errors. The same check is enforced in CI through a dedicated GitHub Actions job.

---

<!-- SECTION: AI Use -->
## AI Use

See [AI.md](./AI.md) for the AI use declaration for this submission.
