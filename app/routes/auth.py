from app.routes.common_imports import *
from fastapi.security import OAuth2PasswordRequestForm
from app.models.models import UserModel
from app.helpers.security import hash_password, verify_password
from fastapi.security import OAuth2PasswordBearer

# for swagger authentication in top right UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

router = APIRouter()

async def get_user_by_email(db: DbDep, email: str):
    user = await db.users.find_one({"email": email})
    if user:
        return UserModel(**user)

async def decode_token(db: DbDep, token : str):
    # No security here, just for testing
    user = await get_user_by_email(db, token)
    return user

async def get_current_user(db: DbDep, token: Annotated[str, Depends(oauth2_scheme)]):
    user = await decode_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}, # part of OAuth2 spec
        )
    return user

@router.post("/token")
async def login(db: DbDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Fetch user from the database by 'username' = email
    user_data = await db.users.find_one({"email": form_data.username})
    if not user_data:
        # use dummy hash to avoid timing attacks
        hash_password("DUMMY")
        raise HTTPException(status_code=400, detail="Invalid username or password")
    user = UserModel(**user_data)  # cast to UserModel for Intellisense

    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"access_token": user.email, "token_type": "bearer"}

@router.get("/users/me")
async def read_users_me(
    current_user: Annotated[UserModel, Depends(get_current_user)],
):
    # We use DbDep throughout our helpers so we don't have to pass it around,
    # since each dependency above (here get_current_user) will inject into lower
    # level dependencies whatever is needed
    return current_user
