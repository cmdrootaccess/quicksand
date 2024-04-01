from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _

def check_password_matches(user, password):
    if not user.check_password(password):
        raise AuthenticationFailed(
            _('Wrong password.'),
        )
