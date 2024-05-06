import os
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.dispatch import receiver

from diploma.settings import MEDIA_USER_FOLDER, MEDIA_DELETE_FOLDER


class UUIDFileStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        _, ext = os.path.splitext(name)
        return MEDIA_USER_FOLDER + str(uuid4()) + ext


class File(models.Model):
    title = models.CharField(null=False, max_length=100)
    filename = models.CharField(default='', max_length=255)
    extension = models.CharField(default='')
    size = models.BigIntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    handle = models.FileField(storage=UUIDFileStorage() , null=True, blank=True, max_length=255)
    url = models.CharField(unique=True, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, to_field='id', related_name='file')
    download_count = models.IntegerField(default=0)
    download_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'File'
        verbose_name_plural = 'Files'

    def __str__(self):
        return self.title


@receiver(models.signals.post_delete, sender=File)
def delete_file(sender, instance, *args, **kwargs):
    if not instance.handle:
        return
    path = instance.handle.path
    if not os.path.exists(MEDIA_DELETE_FOLDER):
        os.makedirs(MEDIA_DELETE_FOLDER)

    os.replace(path, os.path.join(MEDIA_DELETE_FOLDER, os.path.basename(path)))


class UserSettings(models.Model):
    class ColorThemes(models.TextChoices):
        DARK = 'dark', 'DARK'
        LIGHT = 'light', 'LIGHT'

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key = True, to_field='id', related_name='settings')
    color_theme = models.CharField(choices=ColorThemes.choices, default=ColorThemes.DARK)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User settings'
        verbose_name_plural = 'User setings'

    def __str__(self):
        return self.color_theme


@receiver(models.signals.post_save, sender=User)
def create_user(sender, instance, created, **kwargs):
    if created:
        UserSettings.objects.create(user_id=instance.id)
