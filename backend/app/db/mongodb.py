from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings


##debug
print("Connecting to database at mongodb: " + settings.MONGODB_URI)
client = AsyncIOMotorClient(settings.MONGODB_URI)
mongo_db = client[settings.MONGODB_DB]

async def init_mongo_indexes():
    # cria índice em site_id e TTL em expires_at, se quiser expirar logs antigos
    await mongo_db.leaks.create_index("site_id")
    # exemplo de TTL, se quiser limpar documentos após X segundos
    # await mongo_db.leaks.create_index("created_at", expireAfterSeconds=86400)
