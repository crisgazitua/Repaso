from src.Credentials.credential_store import CredentialStore
from src.Server.tcp_server import CleverHomeTCPServer, HubConnectionError
from src.UI.command import Command


class ListHubsCommand(Command):
    def __init__(self, server: CleverHomeTCPServer) -> None:
        self._server = server

    @property
    def name(self) -> str:
        return "list-hubs"

    @property
    def description(self) -> str:
        return "List all currently connected hubs."

    def execute(self, arguments: list[str]) -> str:
        hubs = self._server.list_connected_hubs()
        if not hubs:
            return "No hubs are currently connected."
        lines = ["Connected hubs:"]
        for home_name in sorted(hubs):
            lines.append(f"  - {home_name}")
        return "\n".join(lines)


class StatusCommand(Command):
    def __init__(self, server: CleverHomeTCPServer) -> None:
        self._server = server

    @property
    def name(self) -> str:
        return "status"

    @property
    def description(self) -> str:
        return "Get the current state of a hub. Usage: status <home_name>"

    def execute(self, arguments: list[str]) -> str:
        if len(arguments) != 1:
            return "Usage: status <home_name>"

        home_name = arguments[0]
        hub = self._server.get_hub(home_name)
        if hub is None:
            return f"No connected hub named '{home_name}'."

        try:
            state = hub.send_get_state()
        except HubConnectionError as exc:
            return f"Failed to query hub '{home_name}': {exc}"

        if not state:
            return f"Hub '{home_name}' returned no state."

        lines = [f"State of '{home_name}':"]
        for key in sorted(state.keys()):
            lines.append(f"  {key} = {state[key]}")
        return "\n".join(lines)


class SetStateCommand(Command):
    def __init__(self, server: CleverHomeTCPServer) -> None:
        self._server = server

    @property
    def name(self) -> str:
        return "set"

    @property
    def description(self) -> str:
        return (
            "Set one or more state values on a hub. "
            "Usage: set <home_name> <KEY>=<VALUE> [<KEY>=<VALUE> ...]"
        )

    def execute(self, arguments: list[str]) -> str:
        if len(arguments) < 2:
            return "Usage: set <home_name> <KEY>=<VALUE> [<KEY>=<VALUE> ...]"

        home_name = arguments[0]
        updates: dict[str, str] = {}
        for token in arguments[1:]:
            if "=" not in token:
                return f"Invalid update '{token}'. Expected format KEY=VALUE."
            key, value = token.split("=", 1)
            if not key or not value:
                return f"Invalid update '{token}'. Expected format KEY=VALUE."
            updates[key] = value

        hub = self._server.get_hub(home_name)
        if hub is None:
            return f"No connected hub named '{home_name}'."

        try:
            accepted = hub.send_set_state(updates)
        except HubConnectionError as exc:
            return f"Failed to send set-state to hub '{home_name}': {exc}"
        except ValueError as exc:
            return f"Invalid request: {exc}"

        if accepted:
            return f"Hub '{home_name}' accepted the new state."
        return f"Hub '{home_name}' rejected the new state (ERR)."


class ListCredentialsCommand(Command):
    def __init__(self, credential_store: CredentialStore) -> None:
        self._credential_store = credential_store

    @property
    def name(self) -> str:
        return "list-credentials"

    @property
    def description(self) -> str:
        return "List all registered credentials (passwords are masked)."

    def execute(self, arguments: list[str]) -> str:
        credentials = self._credential_store.list_credentials()
        if not credentials:
            return "No credentials registered."

        lines = ["Registered credentials:"]
        for credential in sorted(
            credentials, key=lambda c: (c.username, c.home_name)
        ):
            masked = "*" * len(credential.password)
            lines.append(
                f"  - username={credential.username}  "
                f"home={credential.home_name}  password={masked}"
            )
        return "\n".join(lines)


class HelpCommand(Command):
    def __init__(self, commands: list[Command]) -> None:
        self._commands = commands

    @property
    def name(self) -> str:
        return "help"

    @property
    def description(self) -> str:
        return "Show this help message."

    def execute(self, arguments: list[str]) -> str:
        lines = ["Available commands:"]
        for command in sorted(self._commands, key=lambda c: c.name):
            lines.append(f"  {command.name:<20} {command.description}")
        return "\n".join(lines)


class QuitCommand(Command):
    @property
    def name(self) -> str:
        return "quit"

    @property
    def description(self) -> str:
        return "Exit the platform."

    def execute(self, arguments: list[str]) -> str:
        return "Goodbye."
