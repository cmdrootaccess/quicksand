from django.contrib.humanize.templatetags.humanize import naturaltime
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _


class IsNotSuspended(BasePermission):
    """
    Dont allow access to suspended users
    """

    def has_permission(self, request, view):
        user = request.user
        return check_user_is_not_suspended(user=user)


def check_user_is_not_suspended(user):
    #TODO: -|.|-
    return False
