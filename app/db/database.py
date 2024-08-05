import motor.motor_asyncio
from typing import Annotated
from dotenv import load_dotenv
from fastapi import Depends
import os
import certifi
import asyncio

# Load environment variables from the .env file located in the project root
# Gets route to project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

# Connecting to database
# NOTE: IP of connection MUST be added in MongoDB Atlas
URI_KEY = os.getenv("MONGO_URI")
PRODUCTION = True if os.getenv("PRODUCTION") == "true" else False

# Separate production and local database by name on the same cluster
# 'local' is a reserved database name in mongodb, so we use 'dev' instead
db_name = "production" if PRODUCTION else "dev"

# Create an async MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(
    URI_KEY,
    tlsCAFile=certifi.where(),
    serverSelectionTimeoutMS=10000,  # Time to wait for server selection
    connectTimeoutMS=10000,  # Time to wait for db connection to be established
)
db = client[db_name]


# Method used by FastAPI to connect to db with dependency
async def get_db() -> motor.motor_asyncio.AsyncIOMotorDatabase:
    """Return MongoDB database of our connection"""
    return db


# Create a shorthand for the database dependency to use in routes
# This leverages FastAPI's feature to interpret Annotated types for dependency injection,
# simplifying the route definitions by reducing repetitive code.
# This is what you should import and add as an argument to all db routes.
DbDep = Annotated[motor.motor_asyncio.AsyncIOMotorDatabase, Depends(get_db)]


async def ping_client():
    """Test MongoDB connection"""
    try:
        await client.admin.command("ping")
        print(f"Successfully connected to MongoDB! {db_name=}")
    except Exception as e:
        print("ERROR: Unable to connect to MongoDB", str(e))


# Example to test the connection: run python3 -m app.db.database
if __name__ == "__main__":
    try:
        asyncio.run(ping_client())
    # okay this exception doesn't actually work since it's not a typical error
    # we can catch -- but the advice is just as valid!
    except Exception as e:
        print("ERROR: Failed to connect")
        print("Ensure IP Address of Connection is Configured in MongoDB Atlas\n\n" + e)
