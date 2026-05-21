import socket
import threading
from types import TracebackType
from typing import Any, Protocol

from src.Credentials.credential_store import CredentialStore
from src.Server.protocol_handler import CleverHomeProtocolHandler, ConnectedHub, SessionContext
from src.Protocol import MESSAGE_TERMINATOR

RECV_CHUNK_SIZE = 1024
ENCODING = "utf-8"


class TransportProtocolHandler(Protocol):
    def process_incoming(
        self, raw_message: str, session: SessionContext
    ) -> tuple[str, bool]: ...

    def cleanup_session(self, session: SessionContext) -> None: ...

    def list_connected_hubs(self) -> list[str]: ...

    def get_hub(self, home_name: str) -> ConnectedHub | None: ...


class CleverHomeTCPServer:
    def __init__(
        self,
        host: str,
        port: int,
        protocol_handler: TransportProtocolHandler | None = None,
        credential_store: CredentialStore | None = None,
    ) -> None:
        if protocol_handler is None:
            if credential_store is None:
                raise ValueError(
                    "Either protocol_handler or credential_store must be provided."
                )
            protocol_handler = CleverHomeProtocolHandler(
                credential_store=credential_store
            )
        self._host = host
        self._port = port
        self._protocol_handler = protocol_handler
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

    def _handle_client(self, client_socket: Any) -> None:
        session = SessionContext()
        buffer = ""
        with client_socket:
            try:
                while True:
                    chunk = client_socket.recv(RECV_CHUNK_SIZE)
                    if not chunk:
                        break

                    buffer += chunk.decode(ENCODING, errors="ignore")
                    while MESSAGE_TERMINATOR in buffer:
                        raw_without_terminator, buffer = buffer.split(MESSAGE_TERMINATOR, 1)
                        raw_message = f"{raw_without_terminator}{MESSAGE_TERMINATOR}"
                        response, should_close = self._protocol_handler.process_incoming(
                            raw_message, session
                        )
                        client_socket.sendall(response.encode(ENCODING))
                        if should_close:
                            return
            finally:
                self._protocol_handler.cleanup_session(session)

    # Backward-compatible façade for callers/tests that still use the old API.
    def list_connected_hubs(self) -> list[str]:
        return self._protocol_handler.list_connected_hubs()

    # Backward-compatible façade for callers/tests that still use the old API.
    def get_hub(self, home_name: str) -> ConnectedHub | None:
        return self._protocol_handler.get_hub(home_name)
