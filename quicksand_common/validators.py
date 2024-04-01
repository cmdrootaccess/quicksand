from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from quicksand_common.model_loaders import get_language_model


def name_characters_validator(name):
    if '>' in name or '<' in name:
        raise ValidationError(
            _('Names can\'t contain < or >.'),
        )


def language_id_exists(language_id):
    Language = get_language_model()
    if not Language.objects.filter(pk=language_id).exists():
        raise ValidationError(
            _('No supported language with the provided id exists.'),
        )


def language_code_exists(language_code):
    Language = get_language_model()
    if not Language.objects.filter(code=language_code).exists():
        raise ValidationError(
            _('No supported language with the provided code exists.'),
        )
