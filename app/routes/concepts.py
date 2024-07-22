from app.routes.common_imports import APIRouter, Depends, run_in_threadpool, get_db
from app.db.collections.concepts import fetch_concepts

router = APIRouter()

# must pass db to each route using it, to ensure dependency injection
@router.get("/concepts")
async def concepts(db=Depends(get_db)):
    # args are passed as **args, rather than calling the func with them
    output = await run_in_threadpool(fetch_concepts, db)
    # cast to string as ObjectID has no JSON encoder specifed
    return {str(obj["_id"]): str(obj) for obj in output}
