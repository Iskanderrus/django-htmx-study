from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Film(models.Model):
    title = models.CharField(max_length=200, unique=True)
    users = models.ManyToManyField(User, related_name='films')

    class Meta:
        ordering = ['title']


