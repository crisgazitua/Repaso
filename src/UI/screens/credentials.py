from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings, KeyPressEvent
from prompt_toolkit.layout.containers import AnyContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from src.UI.screens.base import Screen


class CredentialsScreen(Screen):
    def _render(self) -> FormattedText:
        lines: list[tuple[str, str]] = []
        lines.append(("bold", "  Registered Credentials\n"))
        lines.append(("", "  " + "─" * 50 + "\n"))

        credentials = self._controller.credential_store.list_credentials()

        if not credentials:
            lines.append(("", "  (no credentials registered)\n"))
            return FormattedText(lines)

        lines.append(("bold", f"  {'USERNAME':<15}{'HOME':<15}{'PASSWORD':<20}\n"))
        for cred in sorted(credentials, key=lambda c: (c.username, c.home_name)):
            masked = "*" * len(cred.password)
            lines.append(("", f"  {cred.username:<15}{cred.home_name:<15}{masked:<20}\n"))

        return FormattedText(lines)

    def container(self) -> AnyContainer:  
        return HSplit([
            Window(content=FormattedTextControl(text=self._render), wrap_lines=False),
        ])

    def bottom_toolbar(self) -> str:
        return " [b Back]  [q Quit] "

    def key_bindings(self) -> KeyBindings:
        kb = KeyBindings()

        @kb.add("b")
        @kb.add("escape")
        def _(event: KeyPressEvent) -> None:  
            from src.UI.screens.hubs_list import HubsListScreen
            self._controller.switch_to(HubsListScreen(self._controller))

        @kb.add("q")
        @kb.add("c-c")
        def _(event: KeyPressEvent) -> None:  
            event.app.exit()

        return kb