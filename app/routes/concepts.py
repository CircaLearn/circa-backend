from app.models.models import ConceptModel, UpdateConceptModel
from app.routes.common_imports import *
from app.helpers.similarity import calculate_normalized_embeddings, tensor_to_list
from app.helpers.security import userDep
from typing import List


router = APIRouter()


async def find_concept_by_id(db: DbDep, id: str) -> ConceptModel:
    """
    Finds a concept by id and returns it.

    Raises exceptions for invalid ID format and non-existant concepts.
    """
    try:
        object_id = ObjectId(id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail=f"Invalid concept ID format: {id}")

    concept_data = await db.concepts.find_one({"_id": object_id})
    if not concept_data:
        raise HTTPException(status_code=404, detail=f"Concept not found with id={id}")
    return ConceptModel(**concept_data)


@router.post(
    "/concepts",
    response_description="Insert new concept on their user id",
    status_code=status.HTTP_201_CREATED,
    # can return either ConceptModel(**created_concept) or created_concept, as
    # specifying response_model as ConceptModel lets FastAPI know what to expect
    response_model=ConceptModel,
    response_model_by_alias=False,
)
async def add_concept(
    db: DbDep,
    cur_user: userDep,
    concept: ConceptModel = Body(...),
):
    """
    Insert a concept record (id ignored) and return it.
    A unique `id` will be created.
    """
    new_concept = concept.model_dump(by_alias=True, exclude="id")
    new_concept["user_id"] = cur_user.id
    await db.concepts.insert_one(
        new_concept
    )
    return new_concept


@router.get(
    "/concepts",
    response_description="Fetch all concepts from a user",
    response_model=List[ConceptModel],
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_concepts(db: DbDep, cur_user: userDep):
    """
    Fetch all concepts in the database

    Results limited to 1000 records
    """
    concepts_cursor = db.concepts.find({"user_id" : cur_user.id})
    concepts = await concepts_cursor.to_list(length=1000)
    output = [ConceptModel(**concept) for concept in concepts]
    return output


@router.get(
    "/concepts/{id}",
    response_description="Fetch a concept by id for authenticated user",
    response_model=ConceptModel,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def get_concept_by_id(db: DbDep, cur_user: userDep, id: str):
    """
    Find one concept record by id, if the correct user is logged in
    """
    concept = await find_concept_by_id(db, id)
    # I believe this works and we can use dot notation to compare user_id here
    # It is untested though!
    if concept.user_id != cur_user.id:
        raise HTTPException(401, detail=f"Unauthorized request")

    return concept


@router.put(
    "/concepts/{id}",
    response_description="Update a concept for a user",
    response_model=ConceptModel,
    response_model_by_alias=False,
    status_code=status.HTTP_200_OK,
)
async def update_concept(
    db: DbDep,  # Dependency
    cur_user: userDep,
    id: str,  # Path parameter
    update_data: UpdateConceptModel = Body(...),  # Request body
):
    """
    Updates an existing concept on name or usage, or returns the existing
    concept without any update_data provided.

    The normalized_embedding, if the concept is updated, is automatically
    recalculated.
    """
    concept = await find_concept_by_id(db, id)
    # if we got this far, the concept exists
    if concept.user_id != cur_user.id:
        raise HTTPException(401, detail=f"Unauthorized request")

    update_data_dict = {
        k: v for k, v in update_data.model_dump(by_alias=True).items() if v is not None
    }

    # Recalculate the normalized_embedding if name or usage is updated
    if "name" in update_data_dict or "usage" in update_data_dict:
        embed_string = f"{update_data_dict.get('name', concept['name'])}: {update_data_dict.get('usage', concept['usage'])}"
        update_data_dict["normalized_embedding"] = tensor_to_list(
            calculate_normalized_embeddings(embed_string)
        )

    if update_data_dict:
        await db.concepts.update_one(
            {"_id": concept["_id"]},
            {"$set": update_data_dict},
        )
        updated_concept = await db.concepts.find_one({"_id": concept["_id"]})
        return updated_concept

    return concept


@router.delete(
    "/concepts/{id}",
    response_description="Delete a concept by id for a user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_concept(db: DbDep, cur_user: userDep, id: str):
    """
    Delete a concept by id if the correct user is logged in and owns the concept.
    """
    # Find the concept by id and get it as a ConceptModel instance
    concept = await find_concept_by_id(db, id)

    # Check if the current user owns the concept
    if concept.user_id != cur_user.id:
        raise HTTPException(status_code=401, detail="Unauthorized request")

    # Delete the concept if it belongs to the user
    delete_result = await db.concepts.delete_one({"_id": concept.id})

    if delete_result.deleted_count == 1:
        return JSONResponse(
            content={"message": f"Concept with id={id} deleted."},
            status_code=status.HTTP_200_OK,
        )

    raise HTTPException(
        status_code=500, detail=f"Failed to delete concept with id={id}."
    )
