from dataclasses import dataclass


@dataclass(frozen=True)
class HubCredential:
    username: str
    password: str
    home_name: str


# Backward-compatible alias.
Credential = HubCredential
