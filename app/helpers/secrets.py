from dotenv import load_dotenv
import os

# Load environment variables from the .env file located in the project root
# Gets route to project root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
dotenv_path = os.path.join(project_root, ".env")
load_dotenv(dotenv_path)

URI_KEY = os.getenv("MONGO_URI")
PRODUCTION = True if os.getenv("PRODUCTION") == "true" else False
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
