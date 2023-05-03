"""
Test for Models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_success(self):
        """test creating user"""
        email = 'test@example.com'
        passwd = 'testpass@123'
        user = get_user_model().objects.create_user(
            email=email, password=passwd
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(passwd))

    def test_new_user_email_normalize(self):
        """Normalize email addresses"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]

        for real, expected in sample_emails:
            user = get_user_model().objects.create_user(real, 'pass@123')
            self.assertEqual(user.email, expected)

    def test_new_user_email_valid(self):
        """Check if user has a valid email address"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'oass@123')

    def test_create_superuser(self):
        """test for creating a super user"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test@123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
