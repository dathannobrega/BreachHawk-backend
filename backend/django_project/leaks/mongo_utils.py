from motor.motor_asyncio import AsyncIOMotorClient
from django.conf import settings

from .documents import LeakDoc

client = AsyncIOMotorClient(settings.MONGODB_URI)
mongo_db = client[settings.MONGODB_DB]


async def insert_leak(doc: LeakDoc) -> str:
    result = await mongo_db.leaks.insert_one(doc.model_dump())
    return str(result.inserted_id)


async def find_leaks_by_site(site_id: int, skip: int = 0, limit: int = 50) -> list[LeakDoc]:
    cursor = mongo_db.leaks.find({"site_id": site_id}).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [LeakDoc(**d) for d in docs]


async def init_mongo_indexes() -> None:
    await mongo_db.leaks.create_index("site_id")
