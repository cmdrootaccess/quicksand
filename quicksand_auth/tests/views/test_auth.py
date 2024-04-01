from rest_framework import status
from rest_framework.test import APITestCase
import json
from django.urls import reverse
from faker import Faker

from quicksand_invitations.models import UserInvite

fake = Faker()


class RegistrationAPITests(APITestCase):
    """
       RegistrationAPI
    """

    def test_token_required(self):
        """
        should return 400 if the token is not present
        """
        url = self._get_url()
        data = {'name': 'Max Mustermann', 'password': 'myPassword145',
                'is_of_legal_age': 'true', 'email': 'max@mustermann.com', 'are_guidelines_accepted': True}
        response = self.client.post(url, data, format='multipart')
        parsed_response = json.loads(response.content)
        self.assertIn('token', parsed_response)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_can_be_used_once(self):
        """
        should return 400 if token already has been used to create an account.
        """
        url = self._get_url()
        token = self._make_user_invite_token()
        first_request_data = {'name': 'Max Mustermann', 'email': 'max@mustermann.com',
                              'password': 'myPassword145', 'is_of_legal_age': 'true', 'token': token,
                              'are_guidelines_accepted': True}
        self.client.post(url, first_request_data, format='multipart')
        second_request_data = {'name': 'Sara Mustermann', 'email': 'sara@mustermann.com',
                               'password': 'saraPassword145', 'is_of_legal_age': 'true', 'token': token,
                               'are_guidelines_accepted': True}
        response = self.client.post(url, second_request_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _make_user_invite_token(self):
        user_invite = UserInvite.create_invite(email=fake.email())
        return user_invite.token

    def _get_url(self):
        return reverse('register-user')
