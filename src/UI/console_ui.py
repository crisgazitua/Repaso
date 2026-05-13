from src.Credentials.credential_store import CredentialStore
from src.Server.tcp_server import CleverHomeTCPServer
from src.UI.command import Command
from src.UI.commands import (
    HelpCommand,
    ListCredentialsCommand,
    ListHubsCommand,
    QuitCommand,
    SetStateCommand,
    StatusCommand,
)


class ConsoleUI:
    def __init__(
        self,
        server: CleverHomeTCPServer,
        credential_store: CredentialStore,
    ) -> None:
        self._server = server
        self._credential_store = credential_store
        self._commands: dict[str, Command] = {}
        self._register_default_commands()

    def _register_default_commands(self) -> None:
        list_hubs = ListHubsCommand(self._server)
        status = StatusCommand(self._server)
        set_state = SetStateCommand(self._server)
        list_credentials = ListCredentialsCommand(self._credential_store)
        quit_cmd = QuitCommand()

        # Help receives the list of all other commands so it can describe them.
        help_cmd = HelpCommand(
            [list_hubs, status, set_state, list_credentials, quit_cmd]
        )

        for cmd in (
            list_hubs,
            status,
            set_state,
            list_credentials,
            help_cmd,
            quit_cmd,
        ):
            self._commands[cmd.name] = cmd

    def run(self) -> None:
        self._print_banner()
        while True:
            try:
                raw = input("cleverhome> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()  # newline after ^C / ^D
                break

            if not raw:
                continue

            tokens = raw.split()
            command_name = tokens[0]
            arguments = tokens[1:]

            command = self._commands.get(command_name)
            if command is None:
                print(
                    f"Unknown command: '{command_name}'. "
                    f"Type 'help' to see available commands."
                )
                continue

            output = command.execute(arguments)
            print(output)

            if isinstance(command, QuitCommand):
                break

    def _print_banner(self) -> None:
        print("=" * 60)
        print(" CleverHome Platform - Console UI")
        print(" Type 'help' to see available commands.")
        print("=" * 60)
