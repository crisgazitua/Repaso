import threading
from src.Credentials.credential import Credential
from src.Credentials.in_memory_credential_store import InMemoryCredentialStore
from src.Server.tcp_server import CleverHomeTCPServer
from src.UI.console_ui import ConsoleUI


def _build_credential_store() -> InMemoryCredentialStore:
    return InMemoryCredentialStore(
        initial_credentials=[
            Credential(username="hub1", password="password123", home_name="home-a"),
            Credential(username="hub2", password="password456", home_name="home-b"),
        ]
    )


def main() -> None:
    credential_store = _build_credential_store()
    server = CleverHomeTCPServer(
        host="0.0.0.0", port=9000, credential_store=credential_store
    )

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print("CleverHome TCP server listening on 0.0.0.0:9000")

    ui = ConsoleUI(server=server, credential_store=credential_store)
    ui.run()


if __name__ == "__main__":
    main()
