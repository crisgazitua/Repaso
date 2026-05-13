from src.Credentials.credential import Credential
from src.Credentials.credential_store import CredentialStore

class InMemoryCredentialStore(CredentialStore):
    def __init__(self, initial_credentials: list[Credential] | None = None) -> None:
        self._credentials: dict[tuple[str, str], Credential] = {}
        if initial_credentials is not None:
            for credential in initial_credentials:
                key = (credential.username, credential.home_name)
                self._credentials[key] = credential

    def validate(self, username: str, password: str, home_name: str) -> bool:
        key = (username, home_name)
        stored = self._credentials.get(key)
        if stored is None:
            return False
        return stored.password == password

    def list_credentials(self) -> list[Credential]:
        return list(self._credentials.values())
