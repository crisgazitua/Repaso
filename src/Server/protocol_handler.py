from dataclasses import dataclass
from typing import cast

from src.Credentials.credential_store import CredentialStore
from src.Domain import HouseRegistry
from src.Protocol import (
    BINARY_ONE,
    BINARY_ZERO,
    KEY_HOM,
    KEY_PWD,
    KEY_USR,
    MESSAGE_TERMINATOR,
    MSG_ACC,
    MSG_ERR,
    MSG_GS,
    MSG_HL,
    MSG_OK,
    MSG_REF,
    MSG_SS,
    MSG_SU,
    Message,
    ProtocolParseError,
    parse_message,
    serialize_message,
)
from src.Protocol.message import MessageType


@dataclass
class SessionContext:
    authenticated: bool = False
    home_name: str | None = None


class HubConnectionError(RuntimeError):
    pass


class ConnectedHub:
    def __init__(self, handler: "CleverHomeProtocolHandler", home_name: str) -> None:
        self._handler = handler
        self._home_name = home_name

    def describe_state(self) -> list[str]:
        self._handler.send_message(
            self._home_name, Message(message_type=cast(MessageType, MSG_GS))
        )
        return self._handler.describe_home(self._home_name)

    def set_light(self, index: int, turn_on: bool) -> bool:
        value = BINARY_ONE if turn_on else BINARY_ZERO
        response = self._handler.send_message(
            self._home_name,
            Message(
                message_type=cast(MessageType, MSG_SS),
                parameters={f"LS{index}": value},
            ),
        )
        return response.message_type == MSG_OK

    def set_door_lock(self, index: int, lock: bool) -> bool:
        value = BINARY_ONE if lock else BINARY_ZERO
        response = self._handler.send_message(
            self._home_name,
            Message(
                message_type=cast(MessageType, MSG_SS),
                parameters={f"DS{index}": value},
            ),
        )
        return response.message_type == MSG_OK

    def set_alarm(self, armed: bool) -> bool:
        value = BINARY_ONE if armed else BINARY_ZERO
        response = self._handler.send_message(
            self._home_name,
            Message(message_type=cast(MessageType, MSG_SS), parameters={"AS": value}),
        )
        return response.message_type == MSG_OK

    def set_hvac_mode(self, mode: str) -> bool:
        if mode == "heat":
            parameters = {"HS": BINARY_ONE, "CS": BINARY_ZERO}
        elif mode == "cool":
            parameters = {"HS": BINARY_ZERO, "CS": BINARY_ONE}
        elif mode == "idle":
            parameters = {"HS": BINARY_ZERO, "CS": BINARY_ZERO}
        else:
            raise ValueError(f"Unknown mode: {mode}")

        response = self._handler.send_message(
            self._home_name,
            Message(message_type=cast(MessageType, MSG_SS), parameters=parameters),
        )
        return response.message_type == MSG_OK

    def send_get_state(self) -> dict[str, str]:
        response = self._handler.send_message(
            self._home_name, Message(message_type=cast(MessageType, MSG_GS))
        )
        return dict(response.parameters)

    def send_set_state(self, updates: dict[str, str]) -> bool:
        response = self._handler.send_message(
            self._home_name,
            Message(message_type=cast(MessageType, MSG_SS), parameters=updates),
        )
        return response.message_type == MSG_OK


class CleverHomeProtocolHandler:
    def __init__(
        self,
        credential_store: CredentialStore,
        house_registry: HouseRegistry | None = None,
    ) -> None:
        self._credential_store = credential_store
        self._house_registry = house_registry if house_registry is not None else HouseRegistry()
        self._connected_homes: set[str] = set()

    def process_incoming(self, raw_message: str, session: SessionContext) -> tuple[str, bool]:
        try:
            message = parse_message(raw_message)
        except ProtocolParseError:
            return _response_text(MSG_ERR), False

        if not session.authenticated:
            if message.message_type != MSG_HL:
                return _response_text(MSG_REF), True
            return self._handle_hello(message, session)

        if session.home_name is None:
            return _response_text(MSG_ERR), True

        response = self.send_message(session.home_name, message)
        return serialize_message(response), False

    def send_message(self, home_name: str, message: Message) -> Message:
        self._ensure_connected(home_name)

        if message.message_type == MSG_GS:
            state = self._house_registry.to_state_map(home_name)
            return Message(message_type=cast(MessageType, MSG_SU), parameters=state)

        if message.message_type == MSG_SS:
            accepted = self._house_registry.apply_wire_update(home_name, message.parameters)
            return Message(
                message_type=cast(MessageType, MSG_OK if accepted else MSG_ERR)
            )

        return Message(message_type=cast(MessageType, MSG_ERR))

    def _handle_hello(self, message: Message, session: SessionContext) -> tuple[str, bool]:
        username = message.parameters[KEY_USR]
        password = message.parameters[KEY_PWD]
        home_name = message.parameters[KEY_HOM]

        if not self._credential_store.validate(username, password, home_name):
            return _response_text(MSG_REF), True
        if home_name in self._connected_homes:
            return _response_text(MSG_REF), True

        self._connected_homes.add(home_name)
        self._house_registry.ensure_house(home_name)
        session.authenticated = True
        session.home_name = home_name
        return _response_text(MSG_ACC), False

    def cleanup_session(self, session: SessionContext) -> None:
        if session.home_name is not None:
            self._connected_homes.discard(session.home_name)

    def list_connected_hubs(self) -> list[str]:
        return sorted(self._connected_homes)

    def get_hub(self, home_name: str) -> ConnectedHub | None:
        if home_name not in self._connected_homes:
            return None
        return ConnectedHub(self, home_name)

    def describe_home(self, home_name: str) -> list[str]:
        self._ensure_connected(home_name)
        return self._house_registry.describe_state(home_name)

    def _ensure_connected(self, home_name: str) -> None:
        if home_name not in self._connected_homes:
            raise HubConnectionError(f"Hub '{home_name}' is not connected.")


def _response_text(message_type: str) -> str:
    return f"{message_type}{MESSAGE_TERMINATOR}"
