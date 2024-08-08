from datetime import timedelta
from app.routes.common_imports import *
from fastapi.security import OAuth2PasswordRequestForm
from app.models.models import UserModel, TokenData, Token
from app.helpers.security import (
    hash_password,
    verify_password,
    decode_token,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from fastapi.security import OAuth2PasswordBearer

# for swagger authentication in top right UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

router = APIRouter()


async def get_current_user(db: DbDep, token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Retrieves the current user based on the provided token.
    Args:
        db (DbDep): An injected database dependency used to retrieve user information.
        token (Annotated[str, Depends(oauth2_scheme)]): The token used to authenticate the user.
    Raises:
        HTTPException: If the token is invalid or the user cannot be found in the database.
    Returns:
        UserModel: The user information corresponding to the provided token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_token(token)
    # Ensure token contains ID
    if not user_id:
        raise credentials_exception

    token_data = TokenData(id=user_id)
    # Use id when comparing to str, and _id when comparing to ObjectId
    user = await db.users.find_one({"id": token_data.id})
    if not user:
        raise credentials_exception

    return UserModel(**user)


async def authenticate_user(db: DbDep, email: str, password: str):
    user_data = await db.users.find_one({"email": email})
    if not user_data:
        # use dummy hash to avoid timing attacks
        hash_password("DUMMY")
        return None
    user = UserModel(**user_data)  # cast to UserModel for Intellisense

    # Verify password
    if not verify_password(password, user.hashed_password):
        return None

    return user


@router.post("/token")
async def login_for_access_token(
    db: DbDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    # Fetch user from the database by 'username' = email
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        # use dummy hash to avoid timing attacks
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    # Encode user ID as JWT 'subject'
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/current",
    response_model=UserModel,
    response_model_by_alias=False,
    response_description="Gets current user",
)
async def read_current_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    # We use DbDep throughout our helpers so we don't have to pass it around,
    # since each dependency above (here get_current_user) will inject into lower
    # level dependencies whatever is needed
    return current_user
