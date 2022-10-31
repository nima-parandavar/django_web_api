from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings

# Create your models here.


class Action(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, 'actions')
    verb = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)

    target_ct = models.ForeignKey(ContentType, models.CASCADE)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_ct', 'target_id')

    class Meta:
        indexes = [
            models.Index(fields=['target_ct', 'target_id']),
            models.Index(fields=['-created'])
        ]
        ordering = ['-created']

