import pytest
from src.Credentials import Credential, InMemoryCredentialStore

@pytest.fixture
def sample_credentials() -> list[Credential]:
    return [
        Credential(username="hub1", password="password123", home_name="home-a"),
        Credential(username="hub2", password="password456", home_name="home-b"),
        Credential(username="hub1", password="differentpass", home_name="home-c"),
    ]

@pytest.fixture
def populated_store(sample_credentials: list[Credential]) -> InMemoryCredentialStore:
    return InMemoryCredentialStore(initial_credentials=sample_credentials)

@pytest.fixture
def empty_store() -> InMemoryCredentialStore:
    return InMemoryCredentialStore()
