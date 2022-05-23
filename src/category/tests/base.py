import json
import os.path

import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)

import main
import db_connector


os.environ["DB_NAME"] = "test_db"
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
client = TestClient(main.app)


@pytest.fixture(name="db")
def setup_db():
    db_client = AsyncIOMotorClient(os.environ["ME_CONFIG_MONGODB_URL"])
    db = db_client["test_db"]
    app_db_client = AsyncIOMotorClient(os.environ["ME_CONFIG_MONGODB_URL"])
    db_connector.db = app_db_client["test_db"]
    loop = db_client.get_io_loop()
    with open(os.path.join(CURRENT_PATH, "fixtures.json")) as f:
        items = json.load(f)
        loop.run_until_complete(db_connector.create_bulk_async(items, db))
    yield db
    loop.run_until_complete(db["category"].delete_many({}))
    loop.run_until_complete(db.seqs.delete_many({}))
    db_client.close()
    app_db_client.close()


class TestAPI:
    TREE_PATH = "/api/v1/categories/tree"
    LIST_CREATE_PATH = "/api/v1/categories"
    ITEM_PATH = "/api/v1/categories/{category_id}"
    collection_name = "category"

    def count_items(self, db: AsyncIOMotorDatabase):
        loop = db.client.get_io_loop()
        count = loop.run_until_complete(db[self.collection_name].count_documents({}))
        return count
