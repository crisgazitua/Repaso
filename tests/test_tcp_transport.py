from types import TracebackType

from src.Server.tcp_server import CleverHomeTCPServer
from src.Server.protocol_handler import ConnectedHub, SessionContext


class StubProtocolHandler:
    def __init__(self) -> None:
        self.processed_messages: list[str] = []
        self.cleaned_up = False

    def process_incoming(self, raw_message: str, session: SessionContext) -> tuple[str, bool]:
        self.processed_messages.append(raw_message)
        if raw_message == "GS.":
            return "SU:TR=20.", False
        return "ERR.", True

    def cleanup_session(self, session: SessionContext) -> None:
        self.cleaned_up = True

    def list_connected_hubs(self) -> list[str]:
        return []

    def get_hub(self, home_name: str) -> ConnectedHub | None:
        return None


class FakeSocket:
    def __init__(self, chunks: list[bytes]) -> None:
        self._chunks = chunks
        self.sent_data: list[bytes] = []

    def recv(self, _size: int) -> bytes:
        if not self._chunks:
            return b""
        return self._chunks.pop(0)

    def sendall(self, data: bytes) -> None:
        self.sent_data.append(data)

    def __enter__(self) -> "FakeSocket":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None


def test_handle_client_frames_messages_and_sends_responses() -> None:
    handler = StubProtocolHandler()
    server = CleverHomeTCPServer(host="127.0.0.1", port=9000, protocol_handler=handler)

    fake_client = FakeSocket([b"GS.", b"SS:LS0=1.", b""])
    server._handle_client(fake_client)  # low-level transport behavior test

    assert handler.processed_messages == ["GS.", "SS:LS0=1."]
    assert fake_client.sent_data == [b"SU:TR=20.", b"ERR."]
    assert handler.cleaned_up is True
