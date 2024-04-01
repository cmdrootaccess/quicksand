from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Language(models.Model):
    code = models.CharField(_('code'), max_length=12, blank=False, null=False)
    name = models.CharField(_('name'), max_length=64, blank=False, null=False)
    created = models.DateTimeField(editable=False)

    def __str__(self):
        return 'Language: ' + self.code

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        return super(Language, self).save(*args, **kwargs)
