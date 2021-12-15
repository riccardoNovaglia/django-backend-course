from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientsApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_ingredients_api_requires_authentication(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApi(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user("test@test.com", "irrelevant")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_can_create_and_get_ingredients_through_the_api(self):
        payload = {"name": "sugar"}
        create_res = self.client.post(INGREDIENTS_URL, payload)
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)

        self.assertTrue(Ingredient.objects.filter(name=payload["name"]).exists())
        get_res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(len(get_res.data), 1)
        self.assertEqual(get_res.data[0]["name"], payload["name"])

    def only_returns_ingredients_created_by_the_requesting_user(self):
        other_user = get_user_model().objects.create_user(
            "another@user.com", "irrelevant"
        )
        ingredient = Ingredient.objects.create(name="to be found", user=self.user)
        Ingredient.objects.create("not found", user=other_user)

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
