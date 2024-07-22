from app.db.tables.concepts import fetch_concepts
from app.routes.common_imports import APIRouter, Depends, get_db, AsyncIOMotorDatabase

router = APIRouter()


@router.get("/concepts")
async def concepts(db: AsyncIOMotorDatabase = Depends(get_db)):
    output = await fetch_concepts(db)
    # Cast to string as ObjectID has no JSON encoder specified
    return {str(obj["_id"]): str(obj) for obj in output}
