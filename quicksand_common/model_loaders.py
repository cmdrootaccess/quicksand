from django.apps import apps


def get_user_invite_model():
    return apps.get_model('quicksand_invitations.UserInvite')


def get_language_model():
    return apps.get_model('quicksand_common.Language')
