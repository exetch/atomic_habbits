import os
import sys
import django
sys.path.append('C:/Users/ASUS/PycharmProjects/online_academy')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from rest_framework.test import APITestCase
from users.models import CustomUser
from rest_framework import status


class CustomUserAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(email='testuser@example.com', password='testpass123')
        self.client.force_authenticate(user=self.user)
        self.user_data = {
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '123456789',
            'country': 'Test Country'
        }

    def test_create_user(self):
        response = self.client.post(f'/users/', self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CustomUser.objects.count(), 2)

    def test_retrieve_user(self):
        response = self.client.get(f'/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_user(self):
        self.client.force_authenticate(user=self.user)
        updated_data = {'first_name': 'Updated'}
        response = self.client.patch(f'/users/{self.user.id}/', updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_delete_user(self):
        response = self.client.delete(f'/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CustomUser.objects.count(), 0)
