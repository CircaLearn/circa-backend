import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from app.helpers.secrets import JWT_SECRET_KEY
from fastapi import Request, HTTPException, status, Depends
from app.db.database import DbDep
from app.models.models import UserModel
from typing import Annotated
from bson import ObjectId


SECRET_KEY = JWT_SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 
# TODO: implement a second longer JWT and a place to blacklist old JWTs in the
# case of a "unlog all accounts"

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

# Removed oauth2scheme dependency, since I am no longer keeping track of login
# sessions on the fastapi side. 
# Rather, fastapi is an api that accepts requests and cookies and does what its 
# asked to do with them, but doesn't care where its coming from really.
async def get_current_user(db: DbDep, token: str):
    """
    Retrieves the current user based on the provided token.
    Args:
        db (DbDep): An injected database dependency used to retrieve user information.
        token (str): The token used to authenticate the user.
    Raises:
        HTTPException: If the token is invalid or the user cannot be found in the database.
    Returns:
        UserModel: The user information corresponding to the provided token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    user_id = decode_token(token)
    if not user_id:
        raise credentials_exception

    # always convert to ObjectID when finding by _id, as that's how its
    # always stored in MongoDB
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        print("User not found")
        raise credentials_exception

    return UserModel(**user)


# can be used as a depenency in routes to get the current user
async def get_user_from_request(request: Request, db: DbDep):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    # Call get_current_user with the token extracted from the cookie
    user = await get_current_user(db=db, token=token)
    return user

userDep = Annotated[UserModel, Depends(get_user_from_request)]
