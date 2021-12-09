from django.test import TestCase
from django.contrib.auth import get_user_model


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
