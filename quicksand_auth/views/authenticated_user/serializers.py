from rest_framework import serializers
from django.conf import settings
from django.utils.translation import gettext as _

from quicksand.settings import USERNAME_MAX_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH, PROFILE_NAME_MAX_LENGTH, \
    PROFILE_AVATAR_MAX_SIZE, PROFILE_COVER_MAX_SIZE
from quicksand_auth.models import User, UserProfile
from quicksand_auth.validators import username_characters_validator, \
    email_not_taken_validator
from django.contrib.auth.password_validation import validate_password

from quicksand_common.models import Language
from quicksand_common.serializers_fields.request import FriendlyUrlField, RestrictedImageFileSizeField

from quicksand_common.validators import name_characters_validator, language_id_exists


class GetAuthenticatedUserProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(max_length=None, use_url=True, allow_null=True, required=False)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'name',
            'avatar',
            'cover',
            'is_of_legal_age'
        )


class UserLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = (
            'id',
            'code',
            'name',
        )


class GetAuthenticatedUserSerializer(serializers.ModelSerializer):
    profile = GetAuthenticatedUserProfileSerializer(many=False)

    language = UserLanguageSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'uuid',
            'email',
            'username',
            'profile',
            'language',
            'date_joined',
            'are_guidelines_accepted'
        )


class UpdateAuthenticatedUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH,
                                     allow_blank=False,
                                     validators=[username_characters_validator],
                                     required=False)
    avatar = RestrictedImageFileSizeField(allow_empty_file=False, required=False, allow_null=True,
                                          max_upload_size=PROFILE_AVATAR_MAX_SIZE)
    cover = RestrictedImageFileSizeField(allow_empty_file=False, required=False, allow_null=True,
                                         max_upload_size=PROFILE_COVER_MAX_SIZE)
    password = serializers.CharField(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH,
                                     validators=[validate_password], required=False, allow_blank=False)
    name = serializers.CharField(max_length=PROFILE_NAME_MAX_LENGTH,
                                 required=False,
                                 allow_blank=False, validators=[name_characters_validator])


class DeleteAuthenticatedUserSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH,
                                     validators=[validate_password], required=True, allow_blank=False)


class UpdateAuthenticatedUserSettingsSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH,
                                         validators=[validate_password], required=False, allow_blank=False)
    current_password = serializers.CharField(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH,
                                             validators=[validate_password], required=False, allow_blank=False)
    email = serializers.EmailField(validators=[email_not_taken_validator], required=False)

    def validate(self, data):
        if 'new_password' not in data and 'current_password' in data:
            raise serializers.ValidationError(_('New password must be supplied together with the current password'))

        if 'new_password' in data and 'current_password' not in data:
            raise serializers.ValidationError(_('Current password must be supplied together with the new password'))

        return data


class AuthenticatedUserLanguageSerializer(serializers.Serializer):
    language_id = serializers.IntegerField(validators=[language_id_exists], required=True)


class AuthenticatedUserAllLanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = (
            'id',
            'code',
            'name',
        )
