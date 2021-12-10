from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_requires_authentication(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            'some@email.com',
            'irrelevant'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get_tags(self):
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Vegetarian')
        all_tags = Tag.objects.all().order_by('-name')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, TagSerializer(all_tags, many=True).data)

    def test_only_users_tags_are_returned(self):
        another_user = get_user_model().objects.create_user(
            'other@test.com', 'irrelevant'
        )
        user_tag = Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=another_user, name='Vegetarian')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0], {
            'id': user_tag.id,
            'name': user_tag.name
        })

    def test_tags_creation(self):
        payload = {'name': 'some tag'}
        self.client.post(TAGS_URL, payload)

        self.assertTrue(
            Tag.objects.filter(
                user=self.user,
                name=payload['name']
            ).exists()
        )
