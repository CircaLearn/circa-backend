import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from app.helpers.secrets import JWT_SECRET_KEY

SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)):
    """
    Generates a JSON Web Token (JWT) access token with the provided data.
    Args:
        data (dict): A dictionary containing the data to be encoded in the
        token, (e.g. user id)
        expires_delta (datetime.timedelta, optional): The duration for which the token will expire.
            Defaults to 15 minutes.
    Returns:
        str: The encoded JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    # Add expiration date to data
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> str | None:
    """
    Decodes a JSON Web Token (JWT) and returns the user ID grabbed.
    Args:
        token (str): The JWT to be decoded.
    Returns:
        str or None: A string containing the user ID if the token is valid,
        otherwise None.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("sub")
    except InvalidTokenError:
        return None
    return id


# TODO: create a general authentication dependency (verifies tokens and all)
# that I can inject into all routes requiring authentication without ever having
# to access properties of the injection (unlike DbDep, which I'll always have to
# use inside the routes and can't just be injected in main.py)
