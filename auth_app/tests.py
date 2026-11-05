
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from auth_app.models import Profile


User = get_user_model()


class AuthenticationTests(APITestCase):

    def setUp(self):
        self.customer = User.objects.create_user(
            username="test_customer",
            email="customer@example.com",
            password="TestPassword123!"
        )
        self.business = User.objects.create_user(
            username="test_business",
            email="business@example.com",
            password="TestPassword123!"
        )
        Profile.objects.create(user=self.customer, type="customer")
        Profile.objects.create(user=self.business, type="business")
        self.token = Token.objects.create(user=self.customer)

    def authenticate_customer(self):
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Token {self.token.key}"
        )

    def test_registration_success(self):
        data = {
            "username": "new_customer",
            "email": "new@example.com",
            "password": "TestPassword123!",
            "repeated_password": "TestPassword123!",
            "type": "customer",
        }
        response = self.client.post("/api/registration/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

    def test_registration_password_mismatch(self):
        data = {
            "username": "new_customer",
            "email": "new@example.com",
            "password": "TestPassword123!",
            "repeated_password": "WrongPassword123!",
            "type": "customer",
        }
        response = self.client.post("/api/registration/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        data = {
            "username": "test_customer",
            "password": "TestPassword123!",
        }
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_wrong_password(self):
        data = {
            "username": "test_customer",
            "password": "WrongPassword",
        }
        response = self.client.post("/api/login/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_profile_without_token(self):
        url = f"/api/profile/{self.customer.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_own_profile(self):
        self.authenticate_customer()
        url = f"/api/profile/{self.customer.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_own_profile(self):
        self.authenticate_customer()
        url = f"/api/profile/{self.customer.id}/"
        response = self.client.patch(url, {"location": "Solingen"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.customer.profile.refresh_from_db()
        self.assertEqual(self.customer.profile.location, "Solingen")

    def test_cannot_update_foreign_profile(self):
        self.authenticate_customer()
        url = f"/api/profile/{self.business.id}/"
        response = self.client.patch(url, {"location": "Berlin"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
