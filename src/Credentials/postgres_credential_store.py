from sqlalchemy import Boolean, Column, MetaData, String, Table, create_engine, select
from sqlalchemy.engine import Engine
from src.Credentials.credential import Credential
from src.Credentials.credential_store import CredentialStore

_metadata = MetaData()
_credentials_table = Table(
    "credentials",
    _metadata,
    Column("username", String(255), primary_key=True, nullable=False),
    Column("home_name", String(255), primary_key=True, nullable=False),
    Column("password", String(255), nullable=False),
)

class PostgresCredentialStore(CredentialStore):
    def __init__(
        self,
        database_url: str,
        initial_credentials: list[Credential] | None = None,
        create_tables: bool = True,
    ) -> None:
        self._engine: Engine = create_engine(database_url)
        if create_tables:
            _metadata.create_all(self._engine)
        if initial_credentials:
            self._seed(initial_credentials)

    def validate(self, username: str, password: str, home_name: str) -> bool:
        with self._engine.connect() as conn:
            stmt = select(_credentials_table).where(
                _credentials_table.c.username == username,
                _credentials_table.c.home_name == home_name,
            )
            row = conn.execute(stmt).fetchone()
            if row is None:
                return False
            return str(row.password) == password

    def list_credentials(self) -> list[Credential]:
        with self._engine.connect() as conn:
            rows = conn.execute(select(_credentials_table)).fetchall()
        return [
            Credential(
                username=str(row.username),
                home_name=str(row.home_name),
                password=str(row.password),
            )
            for row in rows
        ]

    def _seed(self, credentials: list[Credential]) -> None:
        with self._engine.begin() as conn:
            for credential in credentials:
                exists_stmt = select(_credentials_table).where(
                    _credentials_table.c.username == credential.username,
                    _credentials_table.c.home_name == credential.home_name,
                )
                existing = conn.execute(exists_stmt).fetchone()
                if existing is None:
                    conn.execute(
                        _credentials_table.insert().values(
                            username=credential.username,
                            home_name=credential.home_name,
                            password=credential.password,
                        )
                    )