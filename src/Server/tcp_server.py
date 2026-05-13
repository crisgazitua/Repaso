from dataclasses import dataclass
import socket
import threading
from src.Credentials.credential_store import CredentialStore
from src.Protocol import Message, ProtocolParseError, parse_message, serialize_message


@dataclass
class SessionContext:
    authenticated: bool = False
    home_name: str | None = None


class HubConnectionError(RuntimeError):
    """Raised when an operation requires a connected hub but it is unavailable."""


class ConnectedHub:
    def __init__(self, server: "CleverHomeTCPServer", home_name: str) -> None:
        self._server = server
        self._home_name = home_name

    def send_get_state(self) -> dict[str, str]:
        return self._server._get_state_for_home(self._home_name)

    def send_set_state(self, updates: dict[str, str]) -> bool:
        return self._server._apply_state_update_for_home(self._home_name, updates)


class CleverHomeTCPServer:
    def __init__(self, host: str, port: int, credential_store: CredentialStore) -> None:
        self._host = host
        self._port = port
        self._credential_store = credential_store
        self._connected_homes: set[str] = set()
        self._home_states: dict[str, dict[str, str]] = {}
        self._lock = threading.Lock()
        self._server_socket: socket.socket | None = None

    def serve_forever(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self._host, self._port))
            server_socket.listen()
            self._server_socket = server_socket
            while True:
                client_socket, _addr = server_socket.accept()
                thread = threading.Thread(
                    target=self._handle_client, args=(client_socket,), daemon=True
                )
                thread.start()

    def _handle_client(self, client_socket: socket.socket) -> None:
        session = SessionContext()
        buffer = ""
        with client_socket:
            try:
                while True:
                    chunk = client_socket.recv(1024)
                    if not chunk:
                        break
                    buffer += chunk.decode("utf-8", errors="ignore")
                    while "." in buffer:
                        raw_without_dot, buffer = buffer.split(".", 1)
                        raw_message = f"{raw_without_dot}."
                        response, should_close = self.process_incoming(raw_message, session)
                        client_socket.sendall(response.encode("utf-8"))
                        if should_close:
                            return
            finally:
                self._cleanup_session(session)

    def process_incoming(self, raw_message: str, session: SessionContext) -> tuple[str, bool]:
        try:
            message = parse_message(raw_message)
        except ProtocolParseError:
            return "ERR.", False

        if not session.authenticated:
            if message.message_type != "HL":
                return "REF.", True
            return self._handle_hello(message, session)

        return self._handle_authenticated(message, session)

    def _handle_hello(self, message: Message, session: SessionContext) -> tuple[str, bool]:
        username = message.parameters["USR"]
        password = message.parameters["PWD"]
        home_name = message.parameters["HOM"]

        if not self._credential_store.validate(username, password, home_name):
            return "REF.", True

        with self._lock:
            if home_name in self._connected_homes:
                return "REF.", True
            self._connected_homes.add(home_name)

        session.authenticated = True
        session.home_name = home_name
        self._home_states.setdefault(home_name, _default_house_state())
        return "ACC.", False

    def _handle_authenticated(
        self, message: Message, session: SessionContext
    ) -> tuple[str, bool]:
        if session.home_name is None:
            return "ERR.", True

        if message.message_type == "GS":
            state = self._home_states[session.home_name]
            su_message = Message(message_type="SU", parameters=state.copy())
            return serialize_message(su_message), False

        if message.message_type == "SS":
            current = self._home_states[session.home_name]
            updates = message.parameters
            if "AO" in updates and updates["AO"] == "0":
                return "ERR.", False

            merged = current.copy()
            merged.update(updates)
            if merged.get("HS") == "1" and merged.get("CS") == "1":
                return "ERR.", False

            self._home_states[session.home_name] = merged
            return "OK.", False

        return "ERR.", False

    def _cleanup_session(self, session: SessionContext) -> None:
        if session.home_name is None:
            return
        with self._lock:
            self._connected_homes.discard(session.home_name)

    def list_connected_hubs(self) -> list[str]:
        with self._lock:
            return sorted(self._connected_homes)

    def get_hub(self, home_name: str) -> ConnectedHub | None:
        with self._lock:
            if home_name not in self._connected_homes:
                return None
        return ConnectedHub(self, home_name)

    def _get_state_for_home(self, home_name: str) -> dict[str, str]:
        with self._lock:
            if home_name not in self._connected_homes:
                raise HubConnectionError(f"Hub '{home_name}' is not connected.")
            state = self._home_states.get(home_name)
            if state is None:
                raise HubConnectionError(f"No state found for hub '{home_name}'.")
            return state.copy()

    def _apply_state_update_for_home(self, home_name: str, updates: dict[str, str]) -> bool:
        with self._lock:
            if home_name not in self._connected_homes:
                raise HubConnectionError(f"Hub '{home_name}' is not connected.")
            current = self._home_states.get(home_name)
            if current is None:
                raise HubConnectionError(f"No state found for hub '{home_name}'.")

            if "AO" in updates and updates["AO"] == "0":
                return False

            merged = current.copy()
            merged.update(updates)
            if merged.get("HS") == "1" and merged.get("CS") == "1":
                return False

            self._home_states[home_name] = merged
            return True


def _default_house_state() -> dict[str, str]:
    # Minimal initial state so GS can always return a valid SU.
    return {
        "TR": "20",
        "DS1": "1",
        "LS1": "0",
        "PS1": "0",
        "AS": "0",
        "AO": "0",
        "HS": "0",
        "CS": "0",
    }
