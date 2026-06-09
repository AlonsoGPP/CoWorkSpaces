from infrastructure.security.scrypt_password_hasher import ScryptPasswordHasher


def test_hash_and_verify_password() -> None:
    hasher = ScryptPasswordHasher()

    password_hash = hasher.hash_password("Admin123!")

    assert password_hash.startswith("scrypt$")
    assert hasher.verify_password("Admin123!", password_hash)


def test_verify_password_returns_false_for_invalid_password() -> None:
    hasher = ScryptPasswordHasher()
    password_hash = hasher.hash_password("Admin123!")

    assert not hasher.verify_password("WrongPassword", password_hash)
