from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    favoritos = models.ManyToManyField('aplicacion.Restaurant', blank=True, related_name='usuarios_favoritos')

    def __str__(self):
        return self.username
