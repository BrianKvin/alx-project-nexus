import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import CustomUser, Profile
from .serializers import CustomUserSerializer, ProfileSerializer

class AccountTests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            email='test@example.com',
            password='testpassword123'
        )
        # Create a test profile
        self.profile = Profile.objects.create(
            user=self.user,
            user_type='job_seeker',
            first_name='Test',
            last_name='User'
        )

    def test_user_registration(self):
        """Test user registration with valid data."""
        url = reverse('user-list')
        data = {
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123',
            'user_type': 'job_seeker',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 2)
        self.assertEqual(Profile.objects.count(), 2)

    def test_user_registration_invalid_email(self):
        """Test user registration with invalid email."""
        url = reverse('user-list')
        data = {
            'email': 'invalid-email',
            'password': 'newpassword123',
            'password_confirm': 'newpassword123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test user login."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_profile_update(self):
        """Test updating user profile."""
        url = reverse('profile-detail', args=[self.user.id])
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.first_name, 'Updated')

    def test_profile_update_unauthorized(self):
        """Test updating other user's profile."""
        # Create another user
        other_user = CustomUser.objects.create_user(
            email='other@example.com',
            password='otherpassword123'
        )
        url = reverse('profile-detail', args=[other_user.id])
        data = {
            'first_name': 'Unauthorized',
            'last_name': 'Update'
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_password_reset_request(self):
        """Test requesting password reset."""
        url = reverse('password_reset:reset-password-request')
        data = {'email': 'test@example.com'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_file_upload(self):
        """Test profile picture upload."""
        import tempfile
        from PIL import Image
        
        # Create a test image
        with tempfile.NamedTemporaryFile(suffix='.jpg') as test_image:
            image = Image.new('RGB', (100, 100))
            image.save(test_image, format='JPEG')
            test_image.seek(0)
            
            url = reverse('profile-detail', args=[self.user.id])
            data = {
                'profile_picture': test_image
            }
            self.client.force_authenticate(user=self.user)
            response = self.client.patch(url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.profile.refresh_from_db()
            self.assertIsNotNone(self.profile.profile_picture)

    def test_rate_limiting(self):
        """Test rate limiting."""
        url = reverse('token_obtain_pair')
        data = {
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        
        # Make 5 successful requests
        for _ in range(5):
            response = self.client.post(url, data)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            
        # 6th request should be rate limited
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_admin_only_endpoints(self):
        """Test admin-only endpoints."""
        url = reverse('user-list')
        
        # Test as non-admin user
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Create admin user
        admin_user = CustomUser.objects.create_superuser(
            email='admin@example.com',
            password='adminpassword123'
        )
        
        # Test as admin user
        self.client.force_authenticate(user=admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
