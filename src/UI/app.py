from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from src.Credentials.credential_store import CredentialStore
from src.UI.house_service import HouseService
from src.UI.screens.base import Screen


class AppController:
    def __init__(self, service: HouseService, credential_store: CredentialStore) -> None:
        self.service = service
        self.credential_store = credential_store
        self._current_screen: Screen | None = None
        self._app: Application | None = None  # type: ignore[type-arg]

    def switch_to(self, screen: Screen) -> None:
        self._current_screen = screen
        if self._app is not None:
            self._app.layout = self._build_layout(screen)
            self._app.key_bindings = screen.key_bindings()
            self._app.invalidate()

    def run(self, initial_screen: Screen) -> None:
        self._current_screen = initial_screen
        self._app = Application(
            layout=self._build_layout(initial_screen),
            key_bindings=initial_screen.key_bindings(),
            full_screen=True,
            mouse_support=False,
        )
        self._app.run()

    def _build_layout(self, screen: Screen) -> Layout:
        header = Window(
            height=Dimension.exact(1),
            content=FormattedTextControl(
                text=FormattedText([("reverse bold", " CleverHome Platform ")])
            ),
        )
        body = screen.container()
        footer = Window(
            height=Dimension.exact(1),
            content=FormattedTextControl(
                text=lambda: FormattedText([("reverse", screen.bottom_toolbar())])
            ),
        )
        return Layout(HSplit([header, body, footer]))