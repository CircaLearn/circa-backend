import bcrypt

def hash_password(password: str) -> str:
    """
    Hashes a string by creating a random salt and hashing the string with that
    random salt. The returned string contains information about the hashing
    algorithm used, the salt, and the complete hash needed for verification.

    Using a salt, and computationally-intensive algorithms, avoids rainbow table
    attacks
    """
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8') # Convert to string for storage


def verify_password(plain_password, hashed_password):
    """
    Uses the salt from hashed_password and plain_password to rehash the two
    together and compare the results to the original hashed_password, verifying
    if two plaintext passwords are equivalent.
    """
    # convert both to bytes
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_byte_enc, hashed_password_bytes)

# TODO: create a general authentication dependency (verifies tokens and all)
# that I can inject into all routes requiring authentication without ever having
# to access properties of the injection (unlike DbDep, which I'll always have to
# use inside the routes and can't just be injected in main.py)
