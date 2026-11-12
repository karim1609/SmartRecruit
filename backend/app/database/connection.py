from pymongo import MongoClient
from app.core.config import settings

# Connect to MongoDB using Docker service hostname
client = MongoClient(
    settings.MONGODB_URI,
    serverSelectionTimeoutMS=5000,
)

db = client[settings.MONGODB_DATABASE]

# Collections
users_collection = db["users"]
candidates_collection = db["candidates"]
recruiters_collection = db["recruiters"]
companies_collection = db["companies"]
company_members_collection = db["company_members"]
job_offers_collection = db["job_offers"]
applications_collection = db["applications"]


def initialize_database():
    """Create MongoDB indexes."""
    users_collection.create_index("email", unique=True)
    candidates_collection.create_index("user_id", unique=True)
    recruiters_collection.create_index("user_id", unique=True)


def check_mongodb_connection():
    """Check whether MongoDB is reachable."""
    client.admin.command("ping")
    return True


def close_mongodb_connection():
    """Close the MongoDB client."""
    client.close()