from passlib.context import CryptContext


# Initialize the password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes a string by creating a random salt and hashing the string with that
    random salt. The returned string contains information about the hashing
    algorithm used, the salt, and the complete hash needed for verification.

    Using a salt, and computationally-intensive algorithms, avoids rainbow table
    attacks
    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """
    Uses the salt from hashed_password and plain_password to rehash the two
    together and compare the results to the original hashed_password, verifying
    if two plaintext passwords are equivalent.
    """
    return pwd_context.verify(plain_password, hashed_password)
