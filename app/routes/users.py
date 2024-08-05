from app.models.models import UserModel, UpdateUserModel
from passlib.context import CryptContext
from app.routes.common_imports import *
from typing import List

router = APIRouter()

# Initialize the password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hashes a string by creating a random salt and hashing the string with that
    random salt. The returned string contains information about the hashing
    algorithm used, the salt, and the complete hash needed for verification.

    Using a salt, and computationally-intensive algorithms, avoids rainbow table 
    attacks
    """
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    """
    Uses the salt from hashed_password and plain_password to rehash the two
    together and compare the results to the original hashed_password, verifying
    if two plaintext passwords are equivalent.
    """
    return pwd_context.verify(plain_password, hashed_password)


@router.post(
    "/users",
    response_description="Insert new user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserModel,
    response_model_by_alias=False,
)
async def create_user(db: DbDep, user: UserModel = Body(...)):
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

    new_user = await db.users.insert_one(user.model_dump(by_alias=True, exclude=["id"]))
    created_user = await db.users.find_one({"_id": new_user.inserted_id})
    return created_user


@router.get(
    "/users",
    response_description="Fetch all users",
    response_model=List[UserModel],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_users(db: DbDep):
    """
    Fetch all users in the database.

    Results limited to 1000 records.
    """
    users_cursor = db.users.find()
    users = await users_cursor.to_list(length=1000)
    output = [UserModel(**user) for user in users]
    return output


@router.get(
    "/users/{id}",
    response_description="Fetch a user by id",
    response_model=UserModel,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id(db: DbDep, id: str):
    """
    Find one user record by id.
    """
    try:
        object_id = ObjectId(id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid user ID format: {id}")

    user = await db.users.find_one({"_id": object_id})
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found with id={id}")
    return user


@router.put(
    "/users/{id}",
    response_description="Update a user",
    response_model=UserModel,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def update_user(db: DbDep, id: str, update_data: UpdateUserModel = Body(...)):
    """
    Updates an existing user's username, password, or profile picture, or 
    returns the existing user without any update_data provided.
    """
    user = await db.users.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found {id=}")

    # Extract only the fields that are present in the update_data
    update_data_dict = {
        k: v for k, v in update_data.model_dump(by_alias=True).items() if v is not None
    }

    # Hash the password if it's being updated
    if update_data_dict.get("password"):
        update_data_dict["password"] = hash_password(update_data_dict["password"])

    # Update the user document if there are changes
    if update_data_dict:
        update_result = await db.users.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": update_data_dict},
            return_document=True,
        )
        if update_result:
            return update_result

    # Return the existing user document if no updates were made
    existing_user = await db.users.find_one({"_id": ObjectId(id)})
    if existing_user:
        return existing_user

    raise HTTPException(status_code=404, detail=f"User {id} not found")


@router.delete(
    "/users/{id}",
    response_description="Delete a user by id",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(db: DbDep, id: str):
    """
    Delete a user by id.
    """
    delete_result = await db.users.delete_one({"_id": ObjectId(id)})
    if delete_result.deleted_count == 1:
        return JSONResponse(
            content={"message": f"User with {id=} deleted"},
            status_code=status.HTTP_200_OK,
        )
    raise HTTPException(status_code=404, detail=f"User with {id=} not found")
