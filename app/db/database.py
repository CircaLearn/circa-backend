from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

# Load environment variables from the .env file located in the project root
# Gets route to project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

# Connecting to database
URI_KEY = os.getenv("MONGO_URI")
PRODUCTION = os.getenv("PRODUCTION")

# separate production and local database by name on the same cluster
# 'local' is a reserved database name in mongodb, so we use 'dev' instead
db_name = "production" if PRODUCTION == "true" else "dev"
# disable need for SSL certificate on local development

client = MongoClient(URI_KEY, tlsCAFile=certifi.where())
db = client[db_name]

# method used by fastapi to connect to db with dependency
def get_db():
    return db
