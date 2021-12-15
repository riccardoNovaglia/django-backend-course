from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


# Without auth
class PublicUserApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successfully(self):
        payload = {
            'email': 'irrelevant@email.com',
            'password': 'irrelevant',
            'name': 'test name'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_returns_400_if_user_already_exists(self):
        payload = {
            'email': 'test@test.com',
            'password': 'irrelevant',
            'name': 'name'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_short_passwords(self):
        payload = {
            'email': 'test@test.com',
            'password': 'p',
            'name': 'name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_token_created_for_user(self):
        payload = {'email': 'some@email.com', 'password': 'irrelevant'}
        create_user(**payload)

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_return_400_when_creds_are_invalid(self):
        create_user(email='test@test.com', password='good pass')
        payload = {'email': 'test@test.com', 'password': 'bad pass'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_return_400_if_user_not_found(self):
        payload = {'email': "test@test.com", 'password': 'irrelevant'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_400_if_password_not_in_req(self):
        res = self.client.post(TOKEN_URL, {'email': 'test@test.com'})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_me_endpoint_requires_authentication(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    def setUp(self):
        self.user = create_user(
            email='some@email.com',
            password='irrelevant',
            name='some-name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_gets_profile_when_authenticated(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_is_not_allowed(self):
        res = self.client.post(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_updates_email_when_sent(self):
        new_email = 'new@test.com'
        old_email = self.user.email
        res = self.client.patch(ME_URL, {'email': new_email, })

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], new_email)
        self.assertEqual(self.user.email, new_email)

        self.assertFalse(
            get_user_model().objects.filter(email=old_email).exists()
        )
        self.assertTrue(
            get_user_model().objects.filter(email=new_email).exists()
        )

    def test_updates_password_when_sent(self):
        new_password = 'new-password'
        res = self.client.patch(ME_URL, {'password': new_password, })

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn('password', res.data['email'])
        self.assertTrue(self.user.check_password(new_password))
