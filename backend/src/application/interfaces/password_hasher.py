from typing import Protocol


class PasswordHasher(Protocol):
    def hash_password(self, raw_password: str) -> str: ...

    def verify_password(self, raw_password: str, hashed_password: str) -> bool: ...
