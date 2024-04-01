import uuid
import re
import secrets

import jwt
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill, ResizeToFit

from quicksand.settings import USERNAME_MAX_LENGTH, PROFILE_NAME_MAX_LENGTH, AUTH_USER_MODEL, JWT_ALGORITHM, SECRET_KEY
from quicksand_auth.checkers import check_password_matches
from quicksand_common.model_loaders import get_user_invite_model
from quicksand_common.validators import name_characters_validator
from quicksand_auth.helpers import upload_to_user_cover_directory, upload_to_user_avatar_directory


class User(AbstractUser):
    """"
    Custom user model to change behaviour of the default user model
    such as validation and required fields.
    """

    first_name = None
    last_name = None
    email = models.EmailField(_('email address'), unique=True, null=False, blank=False)
    username_validator = UnicodeUsernameValidator()
    is_email_verified = models.BooleanField(default=False)
    are_guidelines_accepted = models.BooleanField(default=False)
    # Nothing is ever deleted 😉
    is_deleted = models.BooleanField(
        _('is deleted'),
        default=False,
    )
    username = models.CharField(
        _('username'),
        blank=False,
        null=False,
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text=_('Required. %(username_max_length)d characters or fewer. Letters, digits and _ only.' % {
            'username_max_length': USERNAME_MAX_LENGTH}),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    JWT_TOKEN_TYPE_CHANGE_EMAIL = 'CE'
    JWT_TOKEN_TYPE_PASSWORD_RESET = 'PR'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @classmethod
    def create_user(cls, username, email=None, password=None, name=None, avatar=None, is_of_legal_age=None,
                    are_guidelines_accepted=None):

        if not is_of_legal_age:
            raise ValidationError(
                _('You must confirm you are over 16 years old to make an account'),
            )

        if not are_guidelines_accepted:
            raise ValidationError(
                _('You must accept the guidelines to make an account'),
            )

        new_user = cls.objects.create_user(username, email=email, password=password,
                                           are_guidelines_accepted=are_guidelines_accepted)
        user_profile = bootstrap_user_profile(name=name, user=new_user, avatar=avatar,
                                              is_of_legal_age=is_of_legal_age)

        return new_user

    @classmethod
    def is_username_taken(cls, username):
        UserInvite = get_user_invite_model()
        user_invites = UserInvite.objects.filter(username=username, created_user=None)
        users = cls.objects.filter(username=username)
        if not user_invites.exists() and not users.exists():
            return False
        return True

    @classmethod
    def is_email_taken(cls, email):
        try:
            cls.objects.get(email=email)
            return True
        except User.DoesNotExist:
            return False

    @classmethod
    def get_user_with_email(cls, user_email):
        return cls.objects.get(email=user_email)

    @classmethod
    def user_with_username_exists(cls, username):
        return User.objects.filter(username=username, is_deleted=False).exists()

    @classmethod
    def sanitise_username(cls, username):
        chars = '[@#!±$%^&*()=|/><?,:;\~`{}]'
        return re.sub(chars, '', username).lower().replace(' ', '_').replace('+', '_').replace('-', '_')

    @classmethod
    def get_temporary_username(cls, email):
        username = email.split('@')[0]
        temp_username = cls.sanitise_username(username)
        while cls.is_username_taken(temp_username):
            temp_username = username + str(secrets.randbelow(9999))

        return temp_username

    @classmethod
    def get_user_for_password_reset_token(cls, password_verification_token):
        try:
            token_contents = jwt.decode(password_verification_token, SECRET_KEY,
                                        algorithm=JWT_ALGORITHM)

            token_user_id = token_contents['user_id']
            token_type = token_contents['type']

            if token_type != cls.JWT_TOKEN_TYPE_PASSWORD_RESET:
                raise ValidationError(
                    _('Token type does not match')
                )
            user = User.objects.get(pk=token_user_id)

            return user
        except jwt.InvalidSignatureError:
            raise ValidationError(
                _('Invalid token signature')
            )
        except jwt.ExpiredSignatureError:
            raise ValidationError(
                _('Token expired')
            )
        except jwt.DecodeError:
            raise ValidationError(
                _('Failed to decode token')
            )
        except User.DoesNotExist:
            raise ValidationError(
                _('No user found for token')
            )
        except KeyError:
            raise ValidationError(
                _('Invalid token')
            )

    def save(self, *args, **kwargs):
        self.full_clean(exclude=['invite_count'])
        return super(User, self).save(*args, **kwargs)

    def delete_with_password(self, password):
        check_password_matches(user=self, password=password)
        self.delete()


def bootstrap_user_profile(user, name, is_of_legal_age, avatar=None):
    return UserProfile.objects.create(name=name, user=user, avatar=avatar, is_of_legal_age=is_of_legal_age)


class UserProfile(models.Model):
    name = models.CharField(_('name'), max_length=PROFILE_NAME_MAX_LENGTH, blank=False, null=False,
                            db_index=True,
                            validators=[name_characters_validator])
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    is_of_legal_age = models.BooleanField(default=False)
    avatar = ProcessedImageField(verbose_name=_('avatar'), blank=False, null=True, format='JPEG',
                                 options={'quality': 90}, processors=[ResizeToFill(500, 500)],
                                 upload_to=upload_to_user_avatar_directory)
    cover = ProcessedImageField(verbose_name=_('cover'), blank=False, null=True, format='JPEG', options={'quality': 90},
                                upload_to=upload_to_user_cover_directory,
                                processors=[ResizeToFit(width=1024, upscale=False)])

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('users profiles')

        index_together = [
            ('id', 'user'),
        ]

    def __repr__(self):
        return '<UserProfile %s>' % self.user.username

    def __str__(self):
        return self.user.username
