from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
from src.Credentials.credential import Credential

if TYPE_CHECKING:
    from src.Credentials.postgres_credential_store import PostgresCredentialStore

DATABASE_URL = os.environ.get("DATABASE_URL")
requires_db = pytest.mark.skipif(
    DATABASE_URL is None,
    reason="DATABASE_URL not set — skipping PostgreSQL integration tests",
)


@pytest.fixture
def store() -> PostgresCredentialStore:
    from sqlalchemy import text
    from src.Credentials.postgres_credential_store import PostgresCredentialStore

    assert DATABASE_URL is not None
    s = PostgresCredentialStore(database_url=DATABASE_URL, create_tables=True)
    with s._engine.begin() as conn:
        conn.execute(text("DELETE FROM credentials"))

    return s


@requires_db
class TestPostgresCredentialStoreValidation:
    def test_validate_returns_true_for_valid_credential(
        self, store: PostgresCredentialStore
    ) -> None:
        store._seed([Credential("hub1", "pass123", "home-a")])

        result = store.validate("hub1", "pass123", "home-a")

        assert result is True

    def test_validate_returns_false_for_wrong_password(
        self, store: PostgresCredentialStore
    ) -> None:
        store._seed([Credential("hub1", "pass123", "home-a")])

        result = store.validate("hub1", "wrong", "home-a")

        assert result is False

    def test_validate_returns_false_for_unknown_user(
        self, store: PostgresCredentialStore
    ) -> None:
        result = store.validate("ghost", "pass", "home-a")

        assert result is False

    def test_validate_returns_false_for_unknown_home(
        self, store: PostgresCredentialStore
    ) -> None:
        store._seed([Credential("hub1", "pass123", "home-a")])

        result = store.validate("hub1", "pass123", "home-x")

        assert result is False


@requires_db
class TestPostgresCredentialStoreListing:
    def test_list_credentials_returns_all_seeded(
        self, store: PostgresCredentialStore
    ) -> None:
        credentials = [
            Credential("hub1", "pass1", "home-a"),
            Credential("hub2", "pass2", "home-b"),
        ]
        store._seed(credentials)

        result = store.list_credentials()

        assert len(result) == 2

    def test_list_credentials_empty_when_no_data(
        self, store: PostgresCredentialStore
    ) -> None:
        result = store.list_credentials()

        assert result == []

    def test_seed_does_not_duplicate_existing_credentials(
        self, store: PostgresCredentialStore
    ) -> None:
        cred = Credential("hub1", "pass1", "home-a")
        store._seed([cred])
        store._seed([cred])
        result = store.list_credentials()
        assert len(result) == 1