import threading

from src.Credentials.credential import Credential
from src.Credentials.in_memory_credential_store import InMemoryCredentialStore
from src.Server import CleverHomeProtocolHandler, CleverHomeTCPServer
from src.UI.app import AppController
from src.UI.house_service import HouseService
from src.UI.screens.hubs_list import HubsListScreen


def _build_credential_store() -> InMemoryCredentialStore:
    return InMemoryCredentialStore(
        initial_credentials=[
            Credential(username="hub1", password="password123", home_name="home-a"),
            Credential(username="hub2", password="password456", home_name="home-b"),
        ]
    )


def main() -> None:
    credential_store = _build_credential_store()
    protocol_handler = CleverHomeProtocolHandler(credential_store=credential_store)
    server = CleverHomeTCPServer(
        host="0.0.0.0", port=9000, protocol_handler=protocol_handler
    )

    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    service = HouseService(server)
    controller = AppController(service=service, credential_store=credential_store)
    controller.run(HubsListScreen(controller))


if __name__ == "__main__":
    main()