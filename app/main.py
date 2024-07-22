from fastapi import FastAPI
from app.helpers.similarity import compute_similarity
from app.routes import concepts

app = FastAPI()

# Outside API Routes
app.include_router(concepts.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Hello World!"}


# Route to quickly compare two sentences
@app.get("/compare/{ref}/{other}")
def compare(ref: str, other: str):
    # Turn dashes "-" into spaces " "
    ref = " ".join(ref.split("-"))
    other = " ".join(other.split("-"))
    similarity = compute_similarity(ref, [other])
    return {"similarity": similarity}


# For fast local development
# Use `uvicorn app.main:app --reload` to start
# For production, we will need to use Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
