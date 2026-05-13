import pytest
from src.Credentials import Credential, InMemoryCredentialStore

class TestInMemoryCredentialStoreValidation:
    def test_validate_returns_true_for_valid_credentials(
        self, populated_store: InMemoryCredentialStore
    ) -> None:
        # Arrange
        username = "hub1"
        password = "password123"
        home_name = "home-a"

        # Act
        result = populated_store.validate(username, password, home_name)

        # Assert
        assert result is True

    def test_validate_returns_false_for_wrong_password(
        self, populated_store: InMemoryCredentialStore
    ) -> None:
        # Arrange
        username = "hub1"
        wrong_password = "wrongpassword"
        home_name = "home-a"

        # Act
        result = populated_store.validate(username, wrong_password, home_name)

        # Assert
        assert result is False

    def test_validate_returns_false_for_unknown_username(
        self, populated_store: InMemoryCredentialStore
    ) -> None:
        # Arrange
        unknown_username = "nonexistent_hub"
        password = "password123"
        home_name = "home-a"

        # Act
        result = populated_store.validate(unknown_username, password, home_name)

        # Assert
        assert result is False

    def test_validate_returns_false_for_unknown_home_name(
        self, populated_store: InMemoryCredentialStore
    ) -> None:
        # Arrange
        username = "hub1"
        password = "password123"
        unknown_home = "nonexistent_home"

        # Act
        result = populated_store.validate(username, password, unknown_home)

        # Assert
        assert result is False

    def test_validate_distinguishes_same_username_with_different_homes(
        self, populated_store: InMemoryCredentialStore
    ) -> None:
        # Arrange: hub1 exists for both home-a and home-c with different passwords

        # Act
        result_home_a = populated_store.validate("hub1", "password123", "home-a")
        result_home_c = populated_store.validate("hub1", "differentpass", "home-c")
        cross_result = populated_store.validate("hub1", "password123", "home-c")

        # Assert
        assert result_home_a is True
        assert result_home_c is True
        assert cross_result is False

    def test_validate_returns_false_on_empty_store(
        self, empty_store: InMemoryCredentialStore
    ) -> None:
        # Arrange
        username = "any_user"
        password = "any_password"
        home_name = "any_home"

        # Act
        result = empty_store.validate(username, password, home_name)

        # Assert
        assert result is False

    def test_validate_is_case_sensitive_on_password(
        self, populated_store: InMemoryCredentialStore
    ) -> None:
        # Arrange
        username = "hub1"
        wrong_case_password = "PASSWORD123"
        home_name = "home-a"

        # Act
        result = populated_store.validate(username, wrong_case_password, home_name)

        # Assert
        assert result is False

    def test_validate_rejects_empty_credentials(
        self, populated_store: InMemoryCredentialStore
    ) -> None:
        # Arrange
        empty_username = ""
        empty_password = ""
        empty_home = ""

        # Act
        result = populated_store.validate(empty_username, empty_password, empty_home)

        # Assert
        assert result is False


class TestInMemoryCredentialStoreListing:
    def test_list_credentials_returns_all_loaded_credentials(
        self,
        populated_store: InMemoryCredentialStore,
        sample_credentials: list[Credential],
    ) -> None:
        # Arrange: store is pre-loaded with sample_credentials

        # Act
        result = populated_store.list_credentials()

        # Assert
        assert len(result) == len(sample_credentials)
        for credential in sample_credentials:
            assert credential in result

    def test_list_credentials_returns_empty_list_for_empty_store(
        self, empty_store: InMemoryCredentialStore
    ) -> None:
        # Arrange: empty_store has no credentials

        # Act
        result = empty_store.list_credentials()

        # Assert
        assert result == []

    def test_list_credentials_returns_a_copy_not_internal_reference(
        self, populated_store: InMemoryCredentialStore
    ) -> None:
        # Arrange
        original_count = len(populated_store.list_credentials())

        # Act: try to corrupt the returned list
        returned_list = populated_store.list_credentials()
        returned_list.clear()
        new_count = len(populated_store.list_credentials())

        # Assert: the store was not affected by mutating the returned list
        assert new_count == original_count


class TestInMemoryCredentialStoreConstruction:
    def test_store_can_be_constructed_without_initial_credentials(self) -> None:
        # Arrange & Act
        store = InMemoryCredentialStore()

        # Assert
        assert store.list_credentials() == []

    def test_store_can_be_constructed_with_none_credentials(self) -> None:
        # Arrange & Act
        store = InMemoryCredentialStore(initial_credentials=None)

        # Assert
        assert store.list_credentials() == []

    def test_duplicate_keys_in_initial_credentials_keep_last_one(self) -> None:
        # Arrange: two credentials with same (username, home_name) but different passwords
        first = Credential(username="hub1", password="oldpass", home_name="home-a")
        second = Credential(username="hub1", password="newpass", home_name="home-a")

        # Act
        store = InMemoryCredentialStore(initial_credentials=[first, second])

        # Assert: only the second one survives, and only its password validates
        assert len(store.list_credentials()) == 1
        assert store.validate("hub1", "newpass", "home-a") is True
        assert store.validate("hub1", "oldpass", "home-a") is False


class TestCredentialDataclass:
    def test_credentials_with_same_values_are_equal(self) -> None:
        # Arrange
        credential_a = Credential(
            username="hub1", password="pass", home_name="home-a"
        )
        credential_b = Credential(
            username="hub1", password="pass", home_name="home-a"
        )

        # Act & Assert
        assert credential_a == credential_b

    def test_credential_is_frozen_and_cannot_be_modified(self) -> None:
        # Arrange
        credential = Credential(
            username="hub1", password="pass", home_name="home-a"
        )

        # Act & Assert
        with pytest.raises(Exception):
            credential.password = "new_password"  # type: ignore[misc]
