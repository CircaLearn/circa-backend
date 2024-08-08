from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.helpers.similarity import compute_similarity
from app.routes import concepts, users, auth
from app.db.database import PRODUCTION


app = FastAPI()

API_PREFIX = "/api/v1"

if PRODUCTION:
    origins = ["circalearn.net"]  # domain-to-be
else:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a main API router and add all other routers to it
# TODO: Use authentication dependency defined in helpers.security to inject
# general authentication dependency
api_router = APIRouter()
api_router.include_router(concepts.router, tags=["concepts"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(auth.router, tags=["authentication"], prefix="/auth")


# Routes currently for testing -- still at "/api/v1/" not just "/"
@api_router.get("/")
def root():
    return {"message": "Welcome to the Circa API"}


@api_router.get("/compare/{ref}/{other}")
def compare(ref: str, other: str):
    # Turn dashes "-" into spaces " "
    ref = " ".join(ref.split("-"))
    other = " ".join(other.split("-"))
    similarity = compute_similarity(ref, [other])
    return {"similarity": similarity}


# Include the complete api router in the FastAPI app with the api prefix
app.include_router(api_router, prefix=API_PREFIX)

# For fast local development
# Use `uvicorn app.main:app --reload` to start
# For production, we will need to use Uvicorn
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
