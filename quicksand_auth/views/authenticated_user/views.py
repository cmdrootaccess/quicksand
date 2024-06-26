from django.db import transaction
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.translation import gettext as _

from quicksand_auth.views.authenticated_user.serializers import GetAuthenticatedUserSerializer, \
    UpdateAuthenticatedUserSerializer, DeleteAuthenticatedUserSerializer, UpdateAuthenticatedUserSettingsSerializer, \
    AuthenticatedUserLanguageSerializer, AuthenticatedUserAllLanguagesSerializer
from quicksand_common.model_loaders import get_language_model
from quicksand_common.permissions import IsNotSuspended, check_user_is_not_suspended
from quicksand_common.responses import ApiMessageResponse


class AuthenticatedUser(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user_serializer = GetAuthenticatedUserSerializer(request.user, context={"request": request})
        return Response(user_serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        check_user_is_not_suspended(user=request.user)
        serializer = UpdateAuthenticatedUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user

        with transaction.atomic():
            user.update(
                username=data.get('username'),
                name=data.get('name'),
                location=data.get('location'),
                bio=data.get('bio'),
                url=data.get('url'),
                followers_count_visible=data.get('followers_count_visible'),
                community_posts_visible=data.get('community_posts_visible'),
                visibility=data.get('visibility'),
                save=False
            )

            has_avatar = 'avatar' in data
            if has_avatar:
                avatar = data.get('avatar')
                if avatar is None:
                    user.delete_profile_avatar(save=False)
                else:
                    user.update_profile_avatar(avatar, save=False)

            has_cover = 'cover' in data
            if has_cover:
                cover = data.get('cover')
                if cover is None:
                    user.delete_profile_cover(save=False)
                else:
                    user.update_profile_cover(cover, save=False)

            user.profile.save()
            user.save()

        user_serializer = GetAuthenticatedUserSerializer(user, context={"request": request})
        return Response(user_serializer.data, status=status.HTTP_200_OK)


class DeleteAuthenticatedUser(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = DeleteAuthenticatedUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = request.user

        password = data.get('password')

        with transaction.atomic():
            user.delete_with_password(password=password)

        return Response(_('Goodbye 😔'), status=status.HTTP_200_OK)


class AuthenticatedUserAcceptGuidelines(APIView):
    """
    The API to accept the guidelines
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        with transaction.atomic():
            user.accept_guidelines()

        return ApiMessageResponse(_('Guidelines successfully accepted'), status=status.HTTP_200_OK)


class AuthenticatedUserLanguage(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        Language = get_language_model()
        languages = Language.objects.all()
        all_languages_serializer = AuthenticatedUserAllLanguagesSerializer(
            languages, context={'request': request}, many=True)
        return Response(all_languages_serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        request_data = request.data
        serializer = AuthenticatedUserLanguageSerializer(data=request_data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = request.user

        with transaction.atomic():
            user.set_language_with_id(language_id=data.get('language_id'))

        return ApiMessageResponse(_('Language successfully set'), status=status.HTTP_200_OK)
