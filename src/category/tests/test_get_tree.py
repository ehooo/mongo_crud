from category.tests.base import *


class TestGetTree(TestAPI):
    def test_get_tree(self, db: AsyncIOMotorDatabase):
        response = client.get(self.TREE_PATH)
        assert response.status_code == 200
        expected_result = "Clothes#Men#Business Casual\n" \
                          "Clothes#Men#Sport#Running\n" \
                          "Clothes#Women#Dress\n" \
                          "Clothes#Women#Sport#Running"
        assert response.text == expected_result
