from app.routes.common_imports import *
from app.db.database import DbDep
from fastapi.security import OAuth2PasswordRequestForm
from app.models.models import UserModel
from app.helpers.security import hash_password, verify_password

router = APIRouter()

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

    return {"access_token": user.username, "token_type": "bearer"}
