from src.Credentials.credential_store import CredentialStore
from src.Server import CleverHomeProtocolHandler, HubConnectionError
from src.UI.command import Command


class ListHubsCommand(Command):
    def __init__(self, handler: CleverHomeProtocolHandler) -> None:
        self._handler = handler

    @property
    def name(self) -> str:
        return "list-hubs"

    @property
    def description(self) -> str:
        return "List all currently connected hubs."

    def execute(self, arguments: list[str]) -> str:
        hubs = self._handler.list_connected_hubs()
        if not hubs:
            return "No hubs are currently connected."
        lines = ["Connected hubs:"]
        for home_name in sorted(hubs):
            lines.append(f"  - {home_name}")
        return "\n".join(lines)


class StatusCommand(Command):
    def __init__(self, handler: CleverHomeProtocolHandler) -> None:
        self._handler = handler

    @property
    def name(self) -> str:
        return "status"

    @property
    def description(self) -> str:
        return "Get domain state view. Usage: status <home_name>"

    def execute(self, arguments: list[str]) -> str:
        if len(arguments) != 1:
            return "Usage: status <home_name>"

        home_name = arguments[0]
        hub = self._handler.get_hub(home_name)
        if hub is None:
            return f"No connected hub named '{home_name}'."

        try:
            lines = hub.describe_state()
        except HubConnectionError as exc:
            return f"Failed to query hub '{home_name}': {exc}"

        if not lines:
            return f"Hub '{home_name}' returned no state."

        return "\n".join([f"State of '{home_name}':", *[f"  {line}" for line in lines]])


class SetStateCommand(Command):
    def __init__(self, handler: CleverHomeProtocolHandler) -> None:
        self._handler = handler

    @property
    def name(self) -> str:
        return "set"

    @property
    def description(self) -> str:
        return (
            "Apply domain action. Usage: set <home> light <i> <on|off> | "
            "door <i> <lock|unlock> | alarm <arm|disarm> | hvac <heat|cool|idle>"
        )

    def execute(self, arguments: list[str]) -> str:
        if len(arguments) < 3:
            return (
                "Usage: set <home> light <i> <on|off> | door <i> <lock|unlock> | "
                "alarm <arm|disarm> | hvac <heat|cool|idle>"
            )

        home_name = arguments[0]
        action = arguments[1].lower()
        hub = self._handler.get_hub(home_name)
        if hub is None:
            return f"No connected hub named '{home_name}'."

        try:
            if action == "light" and len(arguments) == 4:
                index = int(arguments[2])
                value = arguments[3].lower()
                if value not in {"on", "off"}:
                    return "Light value must be 'on' or 'off'."
                accepted = hub.set_light(index, value == "on")
            elif action == "door" and len(arguments) == 4:
                index = int(arguments[2])
                value = arguments[3].lower()
                if value not in {"lock", "unlock"}:
                    return "Door value must be 'lock' or 'unlock'."
                accepted = hub.set_door_lock(index, value == "lock")
            elif action == "alarm" and len(arguments) == 3:
                value = arguments[2].lower()
                if value not in {"arm", "disarm"}:
                    return "Alarm value must be 'arm' or 'disarm'."
                accepted = hub.set_alarm(value == "arm")
            elif action == "hvac" and len(arguments) == 3:
                mode = arguments[2].lower()
                if mode not in {"heat", "cool", "idle"}:
                    return "HVAC mode must be 'heat', 'cool', or 'idle'."
                accepted = hub.set_hvac_mode(mode)
            else:
                return (
                    "Usage: set <home> light <i> <on|off> | door <i> <lock|unlock> | "
                    "alarm <arm|disarm> | hvac <heat|cool|idle>"
                )
        except ValueError:
            return "Index must be an integer."
        except HubConnectionError as exc:
            return f"Failed to update hub '{home_name}': {exc}"

        if accepted:
            return f"Hub '{home_name}' accepted the update."
        return f"Hub '{home_name}' rejected the update (ERR)."


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
        for credential in sorted(credentials, key=lambda c: (c.username, c.home_name)):
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
