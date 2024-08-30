from datetime import timedelta
from app.routes.common_imports import *
from fastapi import Response
from fastapi.security import OAuth2PasswordRequestForm
from app.models.models import UserModel, Token
from app.helpers.security import (
    hash_password,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
)
# from fastapi.security import OAuth2PasswordBearer

# # for swagger authentication in top right UI
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

router = APIRouter()


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


@router.post("/login", response_model=Token)
async def login_for_access_token(
    response: Response,
    db: DbDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
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
