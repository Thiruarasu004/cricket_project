from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token
from rest_framework import status


class AuthenticationTestCase(APITestCase):

    def test_registration(self):
        data = {
            "username": "thiru",
            "email": "thiru@gmail.com",
            "password": "123456",
            "password_2": "123456"
        }

        response = self.client.post(reverse("register"),data)
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)

    def test_login(self):
        User.objects.create_user(
            username="thiru",
            email="thiru@gmail.com",
            password="123456"
        )

        data = {"username": "thiru","password": "123456"}
        response = self.client.post(reverse("login"),data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)


    def test_logout(self):
        user = User.objects.create_user(username="thiru",password="123456")
        token = Token.objects.get(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertFalse(Token.objects.filter(user=user).exists())