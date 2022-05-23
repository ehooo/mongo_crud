from category.tests.base import *


class TestCreateCategory(TestAPI):
    ADD_DATA = {"name": "test", "parent_id": 1}

    def test_create_exist(self, db: AsyncIOMotorDatabase):
        initials = self.count_items(db)
        response = client.post(self.LIST_CREATE_PATH, json={"name": "Men", "parent_id": 1})
        assert response.status_code == 409
        response_data = response.json()
        assert response_data == {"detail": "Conflict"}
        assert initials == self.count_items(db)

    def test_create_without_parent(self, db: AsyncIOMotorDatabase):
        initials = self.count_items(db)
        response = client.post(self.LIST_CREATE_PATH, json={"name": "Clothes"})
        assert response.status_code == 400
        response_data = response.json()
        assert response_data == {"detail": "Field parent_id required"}
        assert initials == self.count_items(db)

    def test_create_not_exist(self, db: AsyncIOMotorDatabase):
        initials = self.count_items(db)
        response = client.post(self.LIST_CREATE_PATH, json=self.ADD_DATA)
        assert response.status_code == 201
        response_data = response.json()
        assert response_data == {"name": "test", "parent_id": 1, "category_id": 10}

        loop = db.client.get_io_loop()
        on_db = loop.run_until_complete(db[self.collection_name].find_one({"_id": "10"}))
        assert on_db == {"_id": "10", "name": "test", "parent_id": 1}
        assert initials + 1 == self.count_items(db)

    def test_create_not_payload(self, db: AsyncIOMotorDatabase):
        initials = self.count_items(db)
        response = client.post(self.LIST_CREATE_PATH)
        assert response.status_code == 400
        response_data = response.json()
        assert response_data == {"detail": "Payload required"}
        assert initials == self.count_items(db)

    def test_create_parent_not_exist(self, db: AsyncIOMotorDatabase):
        initials = self.count_items(db)
        data = self.ADD_DATA.copy()
        data["parent_id"] = 500
        response = client.post(self.LIST_CREATE_PATH, json=data)
        assert response.status_code == 400
        response_data = response.json()
        assert response_data == {"detail": "Invalid parent category"}
        assert initials == self.count_items(db)

    def test_create_invalid_fields(self, db: AsyncIOMotorDatabase):
        initials = self.count_items(db)
        data = self.ADD_DATA.copy()
        data["parent_id"] = "invalid"
        response = client.post(self.LIST_CREATE_PATH, json=data)
        assert response.status_code == 400
        response_data = response.json()
        assert response_data == {"detail": "Invalid type in parent_id"}
        assert initials == self.count_items(db)
