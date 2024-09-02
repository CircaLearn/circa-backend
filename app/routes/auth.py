from datetime import timedelta
from app.routes.common_imports import *
from fastapi import Response, Form
from app.models.models import UserModel, Token
from app.helpers.security import (
    hash_password,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
)
from app.helpers.secrets import PRODUCTION

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
    username: str = Form(...),
    password: str = Form(...),
) -> Token:
    user = await authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            # headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    # The cookie can be viewed in Dev Tools > Application > Cookies on frontend
    response.set_cookie(
        key="access_token",
        value=f"{access_token}",
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",  # ensures cookie is sent with all requests in domain
        samesite=None,
        secure=PRODUCTION, # this could cause issues, but it assumes https on prod
    )

    return Token(access_token=access_token, token_type="bearer")
