
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGO_ROOT_USERNAME = os.getenv("MONGO_ROOT_USERNAME")
MONGO_ROOT_PASSWORD = os.getenv("MONGO_ROOT_PASSWORD")

MONGODB_URL = (
    f"mongodb://{MONGO_ROOT_USERNAME}:{MONGO_ROOT_PASSWORD}"
    "@localhost:27017/smartrecruit?authSource=admin"
)

client = MongoClient(MONGODB_URL)

db = client["smartrecruit"]

users_collection = db["users"]
candidates_collection = db["candidates"]
recruiters_collection = db["recruiters"]
companies_collection = db["companies"]

company_members_collection = db["company_members"]
job_offers_collection = db["job_offers"]
applications_collection = db["applications"]