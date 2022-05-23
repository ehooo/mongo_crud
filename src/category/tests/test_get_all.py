from category.tests.base import *


class TestGetAll(TestAPI):
    def test_get_all(self, db: AsyncIOMotorDatabase):
        response = client.get(self.LIST_CREATE_PATH)
        assert response.status_code == 200
        with open(os.path.join(CURRENT_PATH, "fixtures.json")) as f:
            items = json.load(f)
        response_data = response.json()
        for item in items:
            assert item in response_data
        assert len(items) == len(response_data)

    def test_get_all_filter_main_category(self, db: AsyncIOMotorDatabase):
        response = client.get(self.LIST_CREATE_PATH, params={"parent": 1})
        assert response.status_code == 200
        with open(os.path.join(CURRENT_PATH, "fixtures.json")) as f:
            items = json.load(f)
        response_data = response.json()
        for item in items:
            if item.get('parent_id', None) is None:
                continue
            assert item in response_data
        assert len(items) - 1 == len(response_data)

    def test_get_all_with_filter(self, db: AsyncIOMotorDatabase):
        response = client.get(self.LIST_CREATE_PATH, params={"parent": 2})
        assert response.status_code == 200
        expected_result = [
            {
                "category_id": 4,
                "name": "Business Casual",
                "parent_id": 2
            }, {
                "category_id": 5,
                "name": "Sport",
                "parent_id": 2
            }, {
                "category_id": 8,
                "name": "Running",
                "parent_id": 5
            }
        ]
        response_data = response.json()
        for item in expected_result:
            assert item in response_data
        assert len(response_data) == len(expected_result)

    def test_get_all_with_wrong_parent(self, db: AsyncIOMotorDatabase):
        response = client.get(self.LIST_CREATE_PATH, params={"parent": "a"})
        assert response.status_code == 200
        response_data = response.json()
        assert response_data == []

    def test_get_all_with_invalid_arg(self, db: AsyncIOMotorDatabase):
        response = client.get(self.LIST_CREATE_PATH, params={"invalid": "arg"})
        assert response.status_code == 200
        with open(os.path.join(CURRENT_PATH, "fixtures.json")) as f:
            items = json.load(f)
        response_data = response.json()
        for item in items:
            assert item in response_data
        assert len(items) == len(response_data)
