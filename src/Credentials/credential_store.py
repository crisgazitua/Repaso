from abc import ABC, abstractmethod
from src.Credentials.credential import Credential

class CredentialStore(ABC):
    @abstractmethod
    def validate(self, username: str, password: str, home_name: str) -> bool:
        """Check whether a (username, password, home_name) triple is valid.

        Args:
            username: Username from the HL message.
            password: Password from the HL message.
            home_name: Home identifier from the HL message.

        Returns:
            True if a matching credential exists, False otherwise.
        """

    @abstractmethod
    def list_credentials(self) -> list[Credential]:
        """Return all stored credentials.

        Returns:
            A list with all credentials currently in the store. The list
            is a copy; modifying it does not affect the store.
        """
