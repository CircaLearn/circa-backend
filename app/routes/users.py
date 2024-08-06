from app.models.models import (
    UserModel,
    UserCreateModel,
    UserResponseModel,
    UpdateUserModel,
)
from passlib.context import CryptContext
from app.routes.common_imports import *
from typing import List, Annotated
from fastapi.security import OAuth2PasswordRequestForm

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


async def find_user_by_id(db: DbDep, id: str):
    """
    Finds a user by id and returns it.

    Raises exceptions for invalid ID format and non-existent users.
    """
    try:
        object_id = ObjectId(id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid user ID format: {id}")

    user = await db.users.find_one({"_id": object_id})
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found with id={id}")
    return user


@router.post(
    "/users",
    response_description="Insert new user",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseModel,
    response_model_by_alias=False,
)
async def create_user(db: DbDep, created_user: UserCreateModel = Body(...)):
    """
    Insert a user (ignore id) and return it.
    A unique `id` will be created.
    """
    existing_user = await db.users.find_one({"email": created_user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists.",
        )
    # Hash the password before inserting the user
    hashed_password = hash_password(created_user.password)

    # Create UserModel instance to ensure defaults are set
    user_data = UserModel(
        email=created_user.email,
        username=created_user.username,
        hashed_password=hashed_password,
    )

    # important to dump by_alias so an unnecessary "id" field is not created
    new_user = await db.users.insert_one(user_data.model_dump(by_alias=True, 
                                                              exclude="_id"))
    created_user = await db.users.find_one({"_id": new_user.inserted_id})
    return UserResponseModel(**created_user)


@router.get(
    "/users",
    response_description="Fetch all users",
    response_model=List[UserResponseModel],
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
    output = [UserResponseModel(**user) for user in users]
    return output


@router.get(
    "/users/{id}",
    response_description="Fetch a user by id",
    response_model=UserResponseModel,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_user_by_id(db: DbDep, id: str):
    """
    Find one user record by id.
    """
    user = await find_user_by_id(db, id)
    return UserResponseModel(**user)


@router.put(
    "/users/{id}",
    response_description="Update a user",
    response_model=UserResponseModel,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def update_user(db: DbDep, id: str, update_data: UpdateUserModel = Body(...)):
    """
    Updates an existing user's username, password, or profile picture, or
    returns the existing user without any update_data provided.
    """
    existing_user = await find_user_by_id(db, id)

    # Extract only the fields that are present in the update_data
    update_data_dict = {
        k: v for k, v in update_data.model_dump(by_alias=True).items() if v is not None
    }

    # Hash the password if it's being updated
    if update_data_dict.get("password"):
        update_data_dict["hashed_password"] = hash_password(
            update_data_dict.pop("password")
        )

    # Update the user document if there are changes
    if update_data_dict:
        await db.users.update_one(
            {"_id": existing_user["_id"]},
            {"$set": update_data_dict},
        )
        updated_user = await db.users.find_one({"_id": existing_user["_id"]})
        return UserResponseModel(**updated_user)

    # Return the existing user document if no updates were made
    return UserResponseModel(**existing_user)


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


@router.post("/token")
async def login(db: DbDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Fetch user from the database
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
