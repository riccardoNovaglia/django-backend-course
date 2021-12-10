from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@test.com', password='irrelevant'):
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        email = "test@something.com"
        password = "Testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertNotEqual(user.password, password)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalised(self):
        email = "test@SOMETHING.com"
        user = get_user_model().objects.create_user(email, "not important")

        self.assertEqual(user.email, email.lower())

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'not important')

    def test_superuser_created(self):
        user = get_user_model().objects.create_superuser("test@t.com", "test")

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_turns_into_correct_string(self):
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan'
        )
        self.assertEqual(str(tag), tag.name)
