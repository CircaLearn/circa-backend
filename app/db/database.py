import motor.motor_asyncio
from dotenv import load_dotenv
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
client = motor.motor_asyncio.AsyncIOMotorClient(URI_KEY, tlsCAFile=certifi.where())
db = client[db_name]


# Method used by FastAPI to connect to db with dependency
async def get_db():
    """Return MongoDB database of our connection"""
    return db


async def ping_client():
    """Test MongoDB connection"""
    try:
        await client.admin.command("ping")
        print(f"Successfully connected to MongoDB! {db_name=}")
    except Exception as e:
        print("ERROR: Unable to connect to MongoDB", str(e))


# Example to test the connection: run python3 -m app.db.database
if __name__ == "__main__":
    asyncio.run(ping_client())
