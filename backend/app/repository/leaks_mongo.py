from db.mongodb import mongo_db
from schemas.leak_mongo import LeakDoc
from typing import List

collection = mongo_db["leaks"]

async def insert_leak(doc: LeakDoc) -> str:
    result = await collection.insert_one(doc.dict())
    return str(result.inserted_id)

async def find_leaks_by_site(site_id: int, skip: int = 0, limit: int = 50) -> List[LeakDoc]:
    cursor = collection.find({"site_id": site_id}).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [LeakDoc(**d) for d in docs]
