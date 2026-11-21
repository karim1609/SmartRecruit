"""
Idempotent migration script: Updates existing MongoDB users without is_verified field.
Sets is_verified = True and email_verified_at = None for pre-existing accounts so they
can continue to log in without interruption.
"""

import sys
from pymongo import MongoClient

from app.core.config import settings


def migrate_existing_users() -> None:
    print(f"Connecting to MongoDB at {settings.MONGODB_URI}...")
    client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
    db = client[settings.MONGODB_DATABASE]
    users_coll = db["users"]

    # Target users where is_verified field does NOT exist
    query = {"is_verified": {"$exists": False}}
    total_unmigrated = users_coll.count_documents(query)

    print(f"Found {total_unmigrated} user(s) missing 'is_verified' field.")

    if total_unmigrated == 0:
        print("All users already have 'is_verified' field. Migration is up to date.")
        client.close()
        return

    result = users_coll.update_many(
        query,
        {
            "$set": {
                "is_verified": True,
                "email_verified_at": None,
            }
        },
    )

    print(f"Successfully migrated {result.modified_count} user(s).")
    client.close()


if __name__ == "__main__":
    try:
        migrate_existing_users()
    except Exception as exc:
        print(f"Migration error: {exc}", file=sys.stderr)
        sys.exit(1)
