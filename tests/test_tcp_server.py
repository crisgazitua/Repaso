from src.Credentials.credential import Credential
from src.Credentials.in_memory_credential_store import InMemoryCredentialStore
from src.Server import CleverHomeTCPServer, SessionContext


def _build_server() -> CleverHomeTCPServer:
    store = InMemoryCredentialStore(
        initial_credentials=[
            Credential(username="u1", password="p1", home_name="home1"),
            Credential(username="u2", password="p2", home_name="home2"),
        ]
    )
    return CleverHomeTCPServer(host="127.0.0.1", port=9000, credential_store=store)


def test_non_hl_before_auth_is_refused() -> None:
    server = _build_server()
    session = SessionContext()
    response, should_close = server.process_incoming("GS.", session)
    assert response == "REF."
    assert should_close is True


def test_hl_valid_credentials_returns_acc() -> None:
    server = _build_server()
    session = SessionContext()
    response, should_close = server.process_incoming(
        "HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session
    )
    assert response == "ACC."
    assert should_close is False
    assert session.authenticated is True


def test_hl_invalid_credentials_returns_ref() -> None:
    server = _build_server()
    session = SessionContext()
    response, should_close = server.process_incoming(
        "HL:USR=u1;PWD=wrong;HOM=home1;TT=20.", session
    )
    assert response == "REF."
    assert should_close is True


def test_duplicate_home_connection_is_refused() -> None:
    server = _build_server()
    session_one = SessionContext()
    session_two = SessionContext()

    first_response, _ = server.process_incoming(
        "HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session_one
    )
    second_response, should_close = server.process_incoming(
        "HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session_two
    )
    assert first_response == "ACC."
    assert second_response == "REF."
    assert should_close is True


def test_gs_returns_su_after_authentication() -> None:
    server = _build_server()
    session = SessionContext()
    server.process_incoming("HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session)
    response, should_close = server.process_incoming("GS.", session)
    assert response.startswith("SU:")
    assert response.endswith(".")
    assert should_close is False


def test_ss_updates_state_and_returns_ok() -> None:
    server = _build_server()
    session = SessionContext()
    server.process_incoming("HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session)
    response, should_close = server.process_incoming("SS:LS1=1;AS=1.", session)
    assert response == "OK."
    assert should_close is False

    state_response, _ = server.process_incoming("GS.", session)
    assert "LS1=1" in state_response
    assert "AS=1" in state_response


def test_ss_rejects_ao_zero() -> None:
    server = _build_server()
    session = SessionContext()
    server.process_incoming("HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session)
    response, should_close = server.process_incoming("SS:AO=0.", session)
    assert response == "ERR."
    assert should_close is False


def test_ss_rejects_heater_chiller_enabled_together() -> None:
    server = _build_server()
    session = SessionContext()
    server.process_incoming("HL:USR=u1;PWD=p1;HOM=home1;TT=20.", session)
    response, should_close = server.process_incoming("SS:HS=1;CS=1.", session)
    assert response == "ERR."
    assert should_close is False
