from dataclasses import dataclass

@dataclass(frozen=True)
class Credential:
    username: str
    password: str
    home_name: str
