from fastapi import FastAPI
from similarity import compute_similarity, pretty_print_similarities

# run local sever with `fastapi dev api.py`
app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World!"}

@app.get("/compare/{ref}/{other}")
def compare(ref: str, other : str):
    similarity = compute_similarity(ref, [other])
    pretty_print_similarities(ref, similarity)
    return {"similarity": similarity}


