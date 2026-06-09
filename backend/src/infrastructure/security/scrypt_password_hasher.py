import base64
import binascii
import hashlib
import hmac
import os

from application.interfaces.password_hasher import PasswordHasher


class ScryptPasswordHasher(PasswordHasher):
    _PREFIX = "scrypt"
    _N = 2**14
    _R = 8
    _P = 1
    _SALT_BYTES = 16
    _DKLEN = 64

    def hash_password(self, plain_password: str) -> str:
        salt = os.urandom(self._SALT_BYTES)
        derived_key = hashlib.scrypt(
            plain_password.encode("utf-8"),
            salt=salt,
            n=self._N,
            r=self._R,
            p=self._P,
            dklen=self._DKLEN,
        )

        salt_encoded = base64.urlsafe_b64encode(salt).decode("ascii")
        key_encoded = base64.urlsafe_b64encode(derived_key).decode("ascii")
        return (
            f"{self._PREFIX}${self._N}${self._R}${self._P}"
            f"${salt_encoded}${key_encoded}"
        )

    def verify_password(self, plain_password: str, password_hash: str) -> bool:
        parsed = self._parse_password_hash(password_hash)
        if parsed is None:
            return False

        n, r, p, salt, expected_key = parsed
        current_key = hashlib.scrypt(
            plain_password.encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=len(expected_key),
        )
        return hmac.compare_digest(current_key, expected_key)

    def _parse_password_hash(
        self,
        password_hash: str,
    ) -> tuple[int, int, int, bytes, bytes] | None:
        parts = password_hash.split("$")
        if len(parts) != 6:
            return None

        prefix, n_raw, r_raw, p_raw, salt_raw, key_raw = parts
        if prefix != self._PREFIX:
            return None

        try:
            n = int(n_raw)
            r = int(r_raw)
            p = int(p_raw)
            salt = base64.urlsafe_b64decode(salt_raw.encode("ascii"))
            key = base64.urlsafe_b64decode(key_raw.encode("ascii"))
        except (ValueError, TypeError, binascii.Error):
            return None

        return n, r, p, salt, key
