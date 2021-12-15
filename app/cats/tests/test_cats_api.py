from rest_framework import status
from rest_framework.test import APITestCase


class TestCatsApi(APITestCase):
    def test_hello_returns_a_200_with_meow(self):
        res = self.client.get("/api/cats/hello")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["message"], "meow")

    def test_greets_returns_a_200_with_meow_and_the_provided_name(self):
        name = "some name"
        res = self.client.post("/api/cats/greet", {"name": name}, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json()["greeting"], f"hello {name}")

    def test_greets_returns_a_400_if_name_is_not_provided(self):
        res = self.client.post("/api/cats/greet", {}, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", res.json())
