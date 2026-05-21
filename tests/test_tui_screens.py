from src.Credentials.credential import Credential
from src.Credentials.in_memory_credential_store import InMemoryCredentialStore
from src.Server.tcp_server import CleverHomeTCPServer
from src.UI.app import AppController
from src.UI.house_service import HouseService
from src.UI.screens.credentials import CredentialsScreen
from src.UI.screens.house_view import HouseViewScreen
from src.UI.screens.hubs_list import HubsListScreen


def _build_controller() -> AppController:
    store = InMemoryCredentialStore(
        initial_credentials=[
            Credential(username="hub1", password="pass", home_name="home-a")
        ]
    )
    server = CleverHomeTCPServer(host="127.0.0.1", port=19998, credential_store=store)
    service = HouseService(server)
    return AppController(service=service, credential_store=store)


class TestHubsListScreen:
    def test_container_builds_without_error(self) -> None:
        controller = _build_controller()
        screen = HubsListScreen(controller)
        container = screen.container()
        assert container is not None

    def test_key_bindings_are_registered(self) -> None:
        controller = _build_controller()
        screen = HubsListScreen(controller)
        kb = screen.key_bindings()
        assert len(kb.bindings) > 0

    def test_bottom_toolbar_mentions_navigation_keys(self) -> None:
        controller = _build_controller()
        screen = HubsListScreen(controller)
        toolbar = screen.bottom_toolbar()
        assert "↑" in toolbar
        assert "↓" in toolbar
        assert "Enter" in toolbar

    def test_renders_no_hubs_message_when_empty(self) -> None:
        controller = _build_controller()
        screen = HubsListScreen(controller)
        rendered = "".join(item[1] for item in screen._render())
        assert "no hubs" in rendered.lower()


class TestHouseViewScreen:
    def test_container_builds_without_error(self) -> None:
        controller = _build_controller()
        screen = HouseViewScreen(controller, "home-a")
        container = screen.container()
        assert container is not None

    def test_key_bindings_are_registered(self) -> None:
        controller = _build_controller()
        screen = HouseViewScreen(controller, "home-a")
        kb = screen.key_bindings()
        assert len(kb.bindings) > 0

    def test_bottom_toolbar_mentions_back_key(self) -> None:
        controller = _build_controller()
        screen = HouseViewScreen(controller, "home-a")
        toolbar = screen.bottom_toolbar()
        assert "b" in toolbar.lower()

    def test_renders_disconnected_message_when_hub_not_connected(self) -> None:
        controller = _build_controller()
        screen = HouseViewScreen(controller, "home-a")
        rendered = "".join(item[1] for item in screen._render())
        assert "not connected" in rendered.lower()

    def test_rows_returns_empty_when_hub_not_connected(self) -> None:
        controller = _build_controller()
        screen = HouseViewScreen(controller, "home-a")
        rows = screen._rows()
        assert rows == []


class TestCredentialsScreen:
    def test_container_builds_without_error(self) -> None:
        controller = _build_controller()
        screen = CredentialsScreen(controller)
        container = screen.container()
        assert container is not None

    def test_renders_registered_credentials(self) -> None:
        controller = _build_controller()
        screen = CredentialsScreen(controller)
        rendered = "".join(item[1] for item in screen._render())
        assert "hub1" in rendered
        assert "home-a" in rendered

    def test_passwords_are_masked_in_render(self) -> None:
        controller = _build_controller()
        screen = CredentialsScreen(controller)
        rendered = "".join(item[1] for item in screen._render())
        assert "pass" not in rendered
        assert "****" in rendered

    def test_bottom_toolbar_mentions_back_key(self) -> None:
        controller = _build_controller()
        screen = CredentialsScreen(controller)
        toolbar = screen.bottom_toolbar()
        assert "b" in toolbar.lower()