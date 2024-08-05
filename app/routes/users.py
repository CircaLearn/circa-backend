from app.models.models import UserModel, UpdateUserModel
from passlib.context import CryptContext
from app.routes.common_imports import *

router = APIRouter()

# Initialize the password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/users",
            response_description="Insert new user",
            status_code=status.HTTP_201_CREATED,
            response_model=UserModel,
            response_model_by_alias=False,)
async def create_user(db: DbDep, user : UserModel = Body(...)):
    """
    Insert a user (ignore id) and return it.
    A unique `id` will be created.
    """
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )
    # Hash the password before inserting the user
    user.password = hash_password(user.password)

    new_user = await db.users.insert_one(
        user.model_dump(by_alias=True, exclude=["id"])
    )
    created_user = await db.users.find_one({"_id": new_user.inserted_id})
    return created_user
