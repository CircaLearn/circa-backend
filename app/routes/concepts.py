from app.db.tables.concepts import fetch_concepts
from app.models.models import Concept
from bson import ObjectId
from app.routes.common_imports import APIRouter, Depends, get_db, AsyncIOMotorDatabase

router = APIRouter()


@router.get("/concepts")
async def get_concepts(db: AsyncIOMotorDatabase = Depends(get_db)):
    output = await fetch_concepts(db)
    # Cast to string as ObjectID has no JSON encoder specified
    return {str(obj["_id"]): str(obj) for obj in output}


@router.get('/concepts/{id}')
async def get_concept_by_id(id : ObjectId, db: AsyncIOMotorDatabase = Depends(get_db)):
    return 1


@router.post("/concepts")
async def add_concepts(concept : Concept, db: AsyncIOMotorDatabase = Depends(get_db)):
    return 1


@router.put('/concepts/{id}')
async def update_concept(id : ObjectId, db: AsyncIOMotorDatabase = Depends(get_db)):
    return 1


@router.delete('/concepts/{id}')
async def delete_concept(id: ObjectId, db: AsyncIOMotorDatabase = Depends(get_db)):
    return 1
