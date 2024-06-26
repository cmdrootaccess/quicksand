from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
import jwt
from quicksand.settings import USERNAME_MAX_LENGTH, PROFILE_NAME_MAX_LENGTH, SECRET_KEY, JWT_ALGORITHM, EMAIL_HOST
from quicksand_common.model_loaders import get_user_invite_model
from rest_framework.exceptions import ValidationError


class UserInvite(models.Model):
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invited_users',
                                   null=True, blank=True)
    created = models.DateTimeField(_('invited datetime'), null=False, blank=False)
    created_user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=PROFILE_NAME_MAX_LENGTH, null=True, blank=True)
    nickname = models.CharField(max_length=PROFILE_NAME_MAX_LENGTH, null=True, blank=True)
    email = models.EmailField(_('email address'), null=True, blank=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        blank=True,
        null=True,
        max_length=USERNAME_MAX_LENGTH,
        unique=True,
        help_text=_('Required. %(username_max_length)d characters or fewer. Letters, digits and _ only.' % {
            'username_max_length': USERNAME_MAX_LENGTH}),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )

    token = models.CharField(max_length=255, unique=True)
    is_invite_email_sent = models.BooleanField(default=False)

    class Meta:
        unique_together = (('invited_by', 'email'), ('invited_by', 'nickname'),)

    def __str__(self):
        return 'UserInvite'

    @classmethod
    def is_token_valid(cls, token):
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        except jwt.InvalidTokenError:
            return False
        return True

    @classmethod
    def create_invite(cls, email=None, name=None, username=None, nickname=None, invited_by=None):
        UserInvite = get_user_invite_model()
        invite = UserInvite.objects.create(nickname=nickname, name=name, email=email, username=username,
                                           invited_by=invited_by)
        invite.token = invite.generate_token()
        invite.save()
        return invite

    @classmethod
    def get_invite_for_token(cls, token):
        cls._check_token_is_valid(token=token)
        user_invite = UserInvite.objects.get(token=token, created_user=None)
        return user_invite

    @classmethod
    def check_token_is_valid(cls, token):
        cls._check_token_is_valid(token=token)

    @classmethod
    def _check_token_is_valid(cls, token):
        if not UserInvite.is_token_valid(token=token):
            raise ValidationError(
                _('The token is invalid.')
            )

        if not UserInvite.objects.filter(token=token).exists():
            raise ValidationError(
                _('No invite exists for given token.')
            )

        if UserInvite.objects.filter(token=token, created_user__isnull=False).exists():
            raise ValidationError(
                _('This invite has already been used.')
            )

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(UserInvite, self).save(*args, **kwargs)

    def send_invite_email(self):
        if self.invited_by:
            mail_subject = _('You\'ve been invited to join Quicksand')
            text_message_content = render_to_string('quicksand_invitations/email/user_invite.txt', {
                'name': self.name,
                'invited_by_name': self.invited_by.profile.name,
                'invite_link': self._generate_one_time_link()
            })
            html_message_content = render_to_string('quicksand_invitations/email/user_invite.html', {
                'name': self.name,
                'invited_by_name': self.invited_by.profile.name,
                'invite_link': self._generate_one_time_link()
            })
        else:
            raise ValidationError(
                _('You can be invited')
            )

        email = EmailMultiAlternatives(mail_subject, text_message_content, to=[self.email],
                                       from_email=settings.SERVICE_EMAIL_ADDRESS)
        email.attach_alternative(html_message_content, 'text/html')
        email.send()
        self.is_invite_email_sent = True
        self.save()

    def generate_token(self):
        token_bytes = jwt.encode({'id': self.id}, SECRET_KEY, algorithm=JWT_ALGORITHM)
        return token_bytes

    def _generate_one_time_link(self):
        return '{0}/api/auth/invite?token={1}'.format(EMAIL_HOST, self.token)
