from app.models.models import UserModel, UpdateUserModel
from app.routes.common_imports import *

router = APIRouter()

@router.get("/users",
            response_description="Insert new user",
            status_code=status.HTTP_201_CREATED,
            response_model=UserModel,
            response_model_by_alias=False,)
async def create_user(user : UserModel, db = Depends(get_db)):
    """
    Insert a user (ignore id) and return it.
    A unique `id` will be created.
    """
    # TODO hash password before inserted
    # Return the session by calling the login function?
    new_user = await db.users.insert_one(
        user.model_dump(by_alias=True, exclude=["id"])
    )
    created_user = await db.users.find_one({"_id": new_user.inserted_id})
    return created_user
