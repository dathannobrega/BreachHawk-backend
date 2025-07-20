"""MongoDB utility helpers."""

from pymongo import MongoClient
from django.conf import settings
from .documents import LeakDoc
from .models import Leak
from sites.models import Site

client = MongoClient(settings.MONGODB_URI)
mongo_db = client[settings.MONGODB_DB]

INDEXES_INITIALIZED = False


def insert_leak(doc: LeakDoc) -> str:
    """Insert a leak document into MongoDB."""
    # ``model_dump(mode="json")`` ensures all fields are JSON serialisable,
    # converting types like ``HttpUrl`` to plain strings.
    if not INDEXES_INITIALIZED:
        init_mongo_indexes()
    result = mongo_db.leaks.insert_one(doc.model_dump(mode="json"))

    # Create relational DB entry, avoiding duplicates based on unique fields
    try:
        site = Site.objects.get(id=doc.site_id)
    except Site.DoesNotExist:  # pragma: no cover - should not happen in tests
        site = None

    defaults = {
        "site": site,
        "country": doc.country,
        "found_at": doc.found_at,
        "views": doc.views,
        "publication_date": doc.publication_date,
        "amount_of_data": doc.amount_of_data,
        "information": doc.information,
        "comment": doc.comment,
        "download_links": [str(url) for url in doc.download_links]
        if doc.download_links
        else None,
        "rar_password": doc.rar_password,
    }
    Leak.objects.get_or_create(
        company=doc.company,
        source_url=str(doc.source_url),
        defaults=defaults,
    )

    return str(result.inserted_id)


def find_leaks_by_site(
    site_id: int, skip: int = 0, limit: int = 50
) -> list[LeakDoc]:
    if not INDEXES_INITIALIZED:
        init_mongo_indexes()
    cursor = mongo_db.leaks.find({"site_id": site_id}).skip(skip).limit(
        limit
    )
    docs = list(cursor)
    return [LeakDoc(**d) for d in docs]


def search_leaks(query: str, skip: int = 0, limit: int = 50) -> list[LeakDoc]:
    """Return leaks matching the given text query.

    The search is case-insensitive and performs a ``contains`` lookup across
    the ``company``, ``information`` and ``comment`` fields.
    """
    if not INDEXES_INITIALIZED:
        init_mongo_indexes()
    regex = {"$regex": query, "$options": "i"}
    cursor = (
        mongo_db.leaks.find(
            {
                "$or": [
                    {"company": regex},
                    {"information": regex},
                    {"comment": regex},
                ]
            }
        )
        .skip(skip)
        .limit(limit)
    )
    docs = list(cursor)
    return [LeakDoc(**d) for d in docs]


def init_mongo_indexes() -> None:
    """Ensure MongoDB indexes needed by the application exist."""
    global INDEXES_INITIALIZED
    indexes = mongo_db.leaks.index_information()
    site_index_spec = [("site_id", 1)]
    has_site_idx = any(
        index.get("key") == site_index_spec
        for index in indexes.values()
    )
    if not has_site_idx:
        mongo_db.leaks.create_index("site_id", name="site_id_idx")

    text_index_spec = [
        ("company", "text"),
        ("information", "text"),
        ("comment", "text"),
    ]
    expected_weights = {
        "company": 1,
        "information": 1,
        "comment": 1,
    }
    has_text_idx = any(
        index.get("weights") == expected_weights for index in indexes.values()
    )
    if not has_text_idx:
        mongo_db.leaks.create_index(text_index_spec, name="text_search")
    INDEXES_INITIALIZED = True
