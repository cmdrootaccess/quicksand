from rest_framework import serializers
from django.conf import settings

from quicksand.settings import USERNAME_MAX_LENGTH, PASSWORD_MAX_LENGTH, PASSWORD_MIN_LENGTH, PROFILE_NAME_MAX_LENGTH, \
    PROFILE_AVATAR_MAX_SIZE

from quicksand_auth.validators import username_characters_validator, \
    username_not_taken_validator, email_not_taken_validator, user_email_exists
from django.contrib.auth.password_validation import validate_password

from quicksand_common.serializers_fields.request import RestrictedImageFileSizeField
from quicksand_common.validators import name_characters_validator


class RegisterSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH,
                                     validators=[validate_password])
    is_of_legal_age = serializers.BooleanField()
    are_guidelines_accepted = serializers.BooleanField()
    name = serializers.CharField(max_length=PROFILE_NAME_MAX_LENGTH,
                                 allow_blank=False, validators=[name_characters_validator])
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH,
                                     required=False,
                                     allow_blank=True,
                                     validators=[username_characters_validator, username_not_taken_validator])
    avatar = RestrictedImageFileSizeField(allow_empty_file=True, required=False,
                                          max_upload_size=PROFILE_AVATAR_MAX_SIZE)
    email = serializers.EmailField(validators=[email_not_taken_validator])
    token = serializers.CharField()


class RegisterTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class UsernameCheckSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH,
                                     allow_blank=False,
                                     validators=[username_characters_validator, username_not_taken_validator])


class EmailCheckSerializer(serializers.Serializer):
    email = serializers.EmailField(validators=[email_not_taken_validator])


class EmailVerifySerializer(serializers.Serializer):
    token = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH,
                                     allow_blank=False,
                                     validators=[username_characters_validator])
    password = serializers.CharField(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, validators=[user_email_exists])


class VerifyPasswordResetSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH,
                                         validators=[validate_password])
