from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.helpers.similarity import compute_similarity
from app.routes import concepts, users
from app.db.database import PRODUCTION

app = FastAPI()

if PRODUCTION:
    origins = ["circalearn.net"]  # domain-to-be
elif not PRODUCTION:
    origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include API Routes
app.include_router(concepts.router, prefix="/api/v1", tags=['concepts'])
app.include_router(users.router, prefix="/api/v1", tags=["users"])


@app.get("/")
def root():
    return {"message": "Welcome to the Circa API"}


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
