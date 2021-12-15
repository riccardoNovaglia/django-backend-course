from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe, Tag

RECIPES_URL = reverse("recipe:recipe-list")


def recipe_detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


def save_sample_ingredient(user, name='Cinnamon'):
    return Ingredient.objects.create(user=user, name=name)


def save_sample_tag(user, name='main'):
    return Tag.objects.create(user=user, name=name)


def get_sample_recipe(**params) -> dict:
    defaults = {'title': 'things', 'time_minutes': 10, 'price': 2.15}
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
        self.tag = save_sample_tag(self.user)
        self.ingredient = save_sample_ingredient(self.user)

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

    def test_returns_a_recipe_details(self):
        recipe = get_sample_recipe()
        saved_recipe = Recipe.objects.create(user=self.user, **recipe)
        saved_recipe.tags.add(self.tag)
        saved_recipe.ingredients.add(self.ingredient)

        res = self.client.get(recipe_detail_url(saved_recipe.id))

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('ingredients', res.data)
        self.assertEqual(len(res.data['ingredients']), 1)
        self.assertEqual(res.data['ingredients'][0]['name'],
                         self.ingredient.name)
        self.assertIn('tags', res.data)
        self.assertEqual(len(res.data['tags']), 1)
        self.assertEqual(res.data['tags'][0]['name'], self.tag.name)

    def test_recipe_can_be_created_and_given_tags_and_ingredients(self):
        recipe = get_sample_recipe()
        recipe.update({
            'tags': [self.tag.id],
            'ingredients': [self.ingredient.id]
        })

        res = self.client.post(RECIPES_URL, recipe)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe_id = res.data['id']

        res = self.client.get(recipe_detail_url(recipe_id))

        self.assertEqual(len(res.data['ingredients']), 1)
        self.assertEqual(res.data['ingredients'][0]['name'],
                         self.ingredient.name)
        self.assertEqual(len(res.data['tags']), 1)
        self.assertEqual(res.data['tags'][0]['name'], self.tag.name)

    def test_recipe_fields_can_be_updated_using_patch(self):
        original_recipe = get_sample_recipe()
        res = self.client.post(RECIPES_URL, original_recipe)
        created_recipe_id = res.data['id']

        update = {
            'time_minutes': original_recipe['time_minutes'] + 10
        }

        self.client.patch(recipe_detail_url(created_recipe_id), update)

        res = self.client.get(recipe_detail_url(created_recipe_id))
        for key in original_recipe.keys():
            if key == 'time_minutes':
                self.assertEqual(res.data[key], update[key])
            else:
                self.assertEqual(res.data[key], str(original_recipe[key]))

    def test_saves_all_given_fields_using_put_as_long_as_not_required(self):
        recipe_with_tag = get_sample_recipe(tags=[self.tag.id])
        res = self.client.post(RECIPES_URL, recipe_with_tag)
        self.assertEqual(res.data['tags'][0], self.tag.id)
        created_recipe_id = res.data['id']

        bad_update = {'time_minutes': recipe_with_tag['time_minutes'] + 10}
        res = self.client.put(recipe_detail_url(created_recipe_id), bad_update)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        recipe_without_tag = get_sample_recipe()
        res = self.client.put(recipe_detail_url(created_recipe_id),
                              recipe_without_tag)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data['tags']), 0)
