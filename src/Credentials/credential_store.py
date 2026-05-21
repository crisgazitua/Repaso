from abc import ABC, abstractmethod

from src.Credentials.credential import HubCredential


class CredentialStore(ABC):
    @abstractmethod
    def validate(self, username: str, password: str, home_name: str) -> bool:
        pass

    @abstractmethod
    def list_credentials(self) -> list[HubCredential]:
        pass
