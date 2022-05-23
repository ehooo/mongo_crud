from category.tests.base import *


class TestUpdateCategory(TestAPI):
    UPDATE_DATA = {"name": "new_test", "parent_id": 1}

    def test_update_exist(self, db: AsyncIOMotorDatabase):
        response = client.put(self.ITEM_PATH.format(category_id=5), json=self.UPDATE_DATA)
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == self.UPDATE_DATA

        loop = db.client.get_io_loop()
        on_db = loop.run_until_complete(db["category"].find_one({"_id": "5"}))
        assert on_db == {"_id": "5", "name": "new_test", "parent_id": 1}

    def test_update_not_exist(self, db: AsyncIOMotorDatabase):
        response = client.put(self.ITEM_PATH.format(category_id=500), json=self.UPDATE_DATA)
        assert response.status_code == 404
        response_data = response.json()
        assert response_data == {"detail": "Not Found"}

    def test_update_wrong_path(self, db: AsyncIOMotorDatabase):
        response = client.put(self.ITEM_PATH.format(category_id="abc"), json=self.UPDATE_DATA)
        assert response.status_code == 404
        response_data = response.json()
        assert response_data == {"detail": "Not Found"}

    def test_update_not_payload(self, db: AsyncIOMotorDatabase):
        response = client.put(self.ITEM_PATH.format(category_id=5))
        assert response.status_code == 400
        response_data = response.json()
        assert response_data == {"detail": "Payload required"}

    def test_update_parent_not_exist(self, db: AsyncIOMotorDatabase):
        data = self.UPDATE_DATA.copy()
        data["parent_id"] = 500
        response = client.put(self.ITEM_PATH.format(category_id=5), json=data)
        assert response.status_code == 400
        response_data = response.json()
        assert response_data == {"detail": "Invalid parent category"}

    def test_update_without_parent(self, db: AsyncIOMotorDatabase):
        data = self.UPDATE_DATA.copy()
        data.pop("parent_id")
        response = client.put(self.ITEM_PATH.format(category_id=5), json=data)
        assert response.status_code == 400
        response_data = response.json()
        assert response_data == {"detail": "Field parent_id required"}

        loop = db.client.get_io_loop()
        on_db = loop.run_until_complete(db["category"].find_one({"_id": "5"}))
        assert on_db == {"_id": "5", "name": "Sport", "parent_id": 2}

    def test_update_overwrite_exist(self, db: AsyncIOMotorDatabase):
        data = {"name": "Men", "parent_id": 1}
        response = client.put(self.ITEM_PATH.format(category_id=5), json=data)
        assert response.status_code == 409
        response_data = response.json()
        assert response_data == {"detail": "Conflict"}

        loop = db.client.get_io_loop()
        on_db = loop.run_until_complete(db["category"].find_one({"_id": "5"}))
        assert on_db == {"_id": "5", "name": "Sport", "parent_id": 2}
