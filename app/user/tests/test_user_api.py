"""
Tests for User API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """
    Helper method to create a new user
    """
    return get_user_model().objects.create_user(**params)


class TestPublicUserAPI(TestCase):
    """Public features of the User API"""
    def setUp(self):
        self.client = APIClient()

    def test_create_new_user(self):
        """test creating a new user"""
        payload = {
            "email": "test@example.com",
            "password": "testpass@123",
            "name": "Test Name",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test if user already exists"""
        payload = {
            "email": "test@example.com",
            "password": "testpass@123",
            "name": "Test Name",
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password(self):
        """Test if the password is too short"""
        payload = {
            "email": "test@example.com",
            "password": "test",
            "name": "Test Name",
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """test creating token for users"""
        user_details = {
            "email": "test@example.com",
            "password": "test",
            "name": "Test Name",
        }
        create_user(**user_details)

        payload = {
            k: v for k, v in user_details.items() if k in ['email', 'password']
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_bad_token(self):
        """test returns error if credentials invalid"""
        create_user(email='test@example.com', password='goodpass@123')

        payload = {
            'email': 'test@example.com',
            'password': 'badpass@123'
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_blank_password(self):
        """test error for blank password"""
        payload = {
            'email': 'test@example.com',
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """test auth is required for users."""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAPITests(TestCase):
    """Test API requests after authentication"""
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass@123'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """get profile for logged in users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data,
            {'name': self.user.name,
             'email': self.user.email}
        )

    def test_post_me_not_allowed(self):
        """posting to ME end point is not allowed"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_updating_user_profile(self):
        """updating user profile"""
        payload = {'name': 'updated_name', "password": "newpass@123"}
        res = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
