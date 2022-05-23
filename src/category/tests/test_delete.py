from category.tests.base import *


class TestDeleteCategory(TestAPI):
    def test_delete_exist(self, db: AsyncIOMotorDatabase):
        initials = self.count_items(db)
        response = client.delete(self.ITEM_PATH.format(category_id=5))
        assert response.status_code == 200
        assert response.content == b""
        loop = db.client.get_io_loop()
        on_db = loop.run_until_complete(db["category"].find_one({"_id": "5"}))
        assert on_db is None
        on_db = loop.run_until_complete(db["category"].find_one({"_id": "8"}))
        assert on_db is None
        assert initials - 2 == self.count_items(db)

    def test_delete_end_node(self, db: AsyncIOMotorDatabase):
        initials = self.count_items(db)
        response = client.delete(self.ITEM_PATH.format(category_id=8))
        assert response.status_code == 200
        assert response.content == b""
        loop = db.client.get_io_loop()
        on_db = loop.run_until_complete(db["category"].find_one({"_id": "8"}))
        assert on_db is None
        assert initials - 1 == self.count_items(db)

    def test_delete_not_exist(self, db: AsyncIOMotorDatabase):
        initials = self.count_items(db)
        response = client.delete(self.ITEM_PATH.format(category_id=500))
        assert response.status_code == 404
        assert response.content == b""
        assert initials == self.count_items(db)

    def test_delete_wrong_path(self, db: AsyncIOMotorDatabase):
        initials = self.count_items(db)
        response = client.delete(self.ITEM_PATH.format(category_id="abc"))
        assert response.status_code == 404
        assert response.content == b""
        assert initials == self.count_items(db)
