from fastapi import FastAPI, Depends
from fastapi.concurrency import run_in_threadpool
from app.db.database import get_db
from app.helpers.similarity import compute_similarity

# run local sever with `fastapi dev app/main.py` in /circa-backend
app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World!"}


def fetch_concepts(db):
    concepts_collection = db.concepts
    return list(concepts_collection.find())


# must pass db to each route using it, to ensure dependency injection
@app.get("/concepts")
async def concepts(db=Depends(get_db)):
    # args are passed as **args, rather than calling the func with them
    output = await run_in_threadpool(fetch_concepts, db)
    print(output)
    # cast to string as ObjectID has no JSON encoder specifed
    return {str(obj['_id']): str(obj) for obj in output}


# Route to quickly compare two sentences
@app.get("/compare/{ref}/{other}")
def compare(ref: str, other: str):
    # turn dashes "-" into spaces " "
    ref = " ".join(ref.split("-"))
    other = " ".join(other.split("-"))
    similarity = compute_similarity(ref, [other])
    return {"similarity": similarity}
