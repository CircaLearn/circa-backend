from app.models.models import ConceptModel
from app.routes.common_imports import (
    APIRouter,
    Depends,
    status,
    get_db,
    AsyncIOMotorDatabase,
    HTTPException,
)
from fastapi.encoders import jsonable_encoder
from bson import ObjectId

router = APIRouter()


@router.post(
    "/concepts",
    response_description="Insert new concept",
    status_code=status.HTTP_201_CREATED,
    # can return either ConceptModel(**created_concept) or created_concept, as
    # specifying response_model as ConceptModel lets FastAPI know what to expect
    response_model=ConceptModel,
    response_model_by_alias=False,
)
async def add_concept(
    concept: ConceptModel, db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Insert a concept record (id ignored) and return it.
    A unique `id` will be created.
    """
    # returns InsertOneResult, which has inserted_id attribute
    # exclude "id" so MongoDB can create its own
    new_concept = await db.concepts.insert_one(
        concept.model_dump(by_alias=True, exclude=["id"])
    )
    created_concept = await db.concepts.find_one({"_id": new_concept.inserted_id})
    return created_concept


@router.get("/concepts")
async def get_concepts(db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Fetch all concepts in the database

    Results limited to 1000 records
    """
    concepts_cursor = db.concepts.find()
    concepts = await concepts_cursor.to_list(length=1000)
    output = [ConceptModel(**concept) for concept in concepts]
    return jsonable_encoder(output)


@router.get("/concepts/{id}")
async def get_concept_by_id(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Find one concept record by id
    """
    concept = await db.concepts.find_one({"_id": ObjectId(id)})
    if not concept:
        raise HTTPException(404, detail=f"Concept not found {id=}")
    return jsonable_encoder(ConceptModel(**concept))


@router.put("/concepts/{id}")
async def update_concept(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    return 1


@router.delete("/concepts/{id}")
async def delete_concept(id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    return 1
