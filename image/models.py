from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db.models import signals
from django.dispatch import receiver


# Create your manager here

class AvailableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(archive=False)


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Image(models.Model):
    # validators
    image_validator = FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg'])

    photographer = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, 'images')
    image = models.ImageField(upload_to='images/%Y/%m/%d', validators=[image_validator])
    short_description = models.CharField(max_length=255)
    categories = models.ManyToManyField(Category, related_name='image_categories')
    # optional fields
    description = models.TextField(blank=True)
    location = models.CharField(max_length=150, blank=True)
    collection = models.ManyToManyField('Collection', 'collections', blank=True)
    # likes
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='likes')
    number_of_likes = models.PositiveIntegerField(default=0)

    archive = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()
    available_images = AvailableManager()

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['short_description']),
            models.Index(fields=['-created'])
        ]

    def __str__(self):
        return self.short_description


class Collection(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE, 'collections')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['-created']),
            models.Index(fields=['name'])
        ]

    def __str__(self):
        return f"{self.name} collection"


# signals
@receiver(signal=signals.m2m_changed, sender=Image.like.through)
def count_number_of_like(sender, **kwargs):
    action = kwargs.get('action')
    image: Image = kwargs.get('instance')
    if action == "post_add" or action == 'post_remove':
        image.number_of_likes = image.like.count()
        image.save()
