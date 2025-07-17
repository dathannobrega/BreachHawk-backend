"""MongoDB utility helpers."""

from pymongo import MongoClient
from django.conf import settings
from .documents import LeakDoc

client = MongoClient(settings.MONGODB_URI)
mongo_db = client[settings.MONGODB_DB]


def insert_leak(doc: LeakDoc) -> str:
    """Insert a leak document into MongoDB."""
    # ``model_dump(mode="json")`` ensures all fields are JSON serialisable,
    # converting types like ``HttpUrl`` to plain strings.
    result = mongo_db.leaks.insert_one(doc.model_dump(mode="json"))
    return str(result.inserted_id)


def find_leaks_by_site(
    site_id: int, skip: int = 0, limit: int = 50
) -> list[LeakDoc]:
    cursor = mongo_db.leaks.find({"site_id": site_id}).skip(skip).limit(
        limit
    )
    docs = list(cursor)
    return [LeakDoc(**d) for d in docs]


def search_leaks(query: str, skip: int = 0, limit: int = 50) -> list[LeakDoc]:
    """Return leaks matching the given text query."""
    cursor = (
        mongo_db.leaks.find({"$text": {"$search": query}})
        .skip(skip)
        .limit(limit)
    )
    docs = list(cursor)
    return [LeakDoc(**d) for d in docs]


def init_mongo_indexes() -> None:
    mongo_db.leaks.create_index("site_id")
    mongo_db.leaks.create_index(
        [
            ("company", "text"),
            ("information", "text"),
            ("comment", "text"),
        ]
    )
