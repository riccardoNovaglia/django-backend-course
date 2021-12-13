from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

RECIPES_URL = reverse("recipe:recipe-list")


def get_sample_recipe(**params):
    defaults = {'title': 'things', 'time_minutes': 10, 'price': 2.00}
    defaults.update(params)
    return defaults


class PublicRecipesApi(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_recipes_api_requires_authentication(self):
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipesApi(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            "test@test.com", "irrelevant"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_can_create_and_get_recipes_through_the_api(self):
        payload = get_sample_recipe()
        create_res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            Recipe.objects.filter(title=payload['title']).exists()
        )
        get_res = self.client.get(RECIPES_URL)
        self.assertEqual(len(get_res.data), 1)
        self.assertEqual(get_res.data[0]['title'], payload['title'])

    def test_only_returns_recipes_created_by_the_requesting_user(self):
        other_user = get_user_model().objects.create_user('another@user.com',
                                                          'irrelevant')
        recipe = Recipe.objects.create(user=self.user, **get_sample_recipe())
        Recipe.objects.create(user=other_user, **get_sample_recipe())

        res = self.client.get(RECIPES_URL)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], recipe.title)
