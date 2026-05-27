import os
import threading
from src.Credentials.credential import Credential
from src.Credentials.credential_store import CredentialStore
from src.Credentials.in_memory_credential_store import InMemoryCredentialStore
from src.Server.tcp_server import CleverHomeTCPServer
from src.UI.app import AppController
from src.UI.house_service import HouseService
from src.UI.screens.hubs_list import HubsListScreen

_INITIAL_CREDENTIALS = [
    Credential(username="hub1", password="password123", home_name="home-a"),
    Credential(username="hub2", password="password456", home_name="home-b"),
]


def _build_credential_store() -> CredentialStore:
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        from src.Credentials.postgres_credential_store import PostgresCredentialStore
        return PostgresCredentialStore(
            database_url=database_url,
            initial_credentials=_INITIAL_CREDENTIALS,
        )
    return InMemoryCredentialStore(initial_credentials=_INITIAL_CREDENTIALS)


def main() -> None:
    credential_store = _build_credential_store()
    server = CleverHomeTCPServer(
        host="0.0.0.0", port=9000, credential_store=credential_store
    )

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    service = HouseService(server)
    controller = AppController(service=service, credential_store=credential_store)
    controller.run(HubsListScreen(controller))


if __name__ == "__main__":
    main()