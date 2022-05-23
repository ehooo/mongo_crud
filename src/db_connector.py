import os

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)
from pymongo.errors import DuplicateKeyError

db_client: [AsyncIOMotorClient] = None
db: [AsyncIOMotorDatabase] = None


def get_db():
    global db_client, db
    if db is None:
        db_client = AsyncIOMotorClient(os.environ["ME_CONFIG_MONGODB_URL"])
        db = db_client[os.environ.get("DB_NAME", "mongo_crud")]
    return db


async def create_bulk_async(items, db_conn):
    last_id = 0
    for item in items:
        category_id = item.pop("category_id")
        last_id = max(last_id, category_id)
        item["_id"] = str(category_id)
        try:
            await db_conn["category"].insert_one(item)
        except DuplicateKeyError:
            pass
    exists = await db_conn.seqs.find_one({"collection": "category"})
    if exists is None:
        await db_conn.seqs.insert_one({
            "collection": "category",
            "id": last_id,
        })


async def create_db_client():
    global db_client, db
    db_client = AsyncIOMotorClient(os.environ["ME_CONFIG_MONGODB_URL"])
    db = db_client[os.environ.get("DB_NAME", "mongo_crud")]


async def shutdown_db_client():
    global db_client
    if isinstance(db_client, AsyncIOMotorClient):
        db_client.close()
