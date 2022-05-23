from category.tests.base import *


class TestGetCategory(TestAPI):
    def test_get_exist(self, db: AsyncIOMotorDatabase):
        response = client.get(self.ITEM_PATH.format(category_id=5))
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == {"name": "Sport", "parent_id": 2}

    def test_get_not_exist(self, db: AsyncIOMotorDatabase):
        response = client.get(self.ITEM_PATH.format(category_id=500))
        assert response.status_code == 404
        response_data = response.json()
        assert response_data == {"detail": "Not Found"}

    def test_get_wrong_path(self, db: AsyncIOMotorDatabase):
        response = client.get(self.ITEM_PATH.format(category_id="abc"))
        assert response.status_code == 404
        response_data = response.json()
        assert response_data == {"detail": "Not Found"}
