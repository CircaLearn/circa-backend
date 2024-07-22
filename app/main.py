from fastapi import FastAPI
from app.helpers.similarity import compute_similarity
from app.routes import concepts

# run local sever with `fastapi dev app/main.py` in /circa-backend
app = FastAPI()

# add outside defined routes to main app
app.include_router(concepts.router)


@app.get("/")
def root():
    return {"message": "Hello World!"}


# Route to quickly compare two sentences
@app.get("/compare/{ref}/{other}")
def compare(ref: str, other: str):
    # turn dashes "-" into spaces " "
    ref = " ".join(ref.split("-"))
    other = " ".join(other.split("-"))
    similarity = compute_similarity(ref, [other])
    return {"similarity": similarity}
