from django.db import models
from django.contrib.auth.models import AbstractUser
from PIL import Image

class Usuario(AbstractUser):
    foto_perfil = models.ImageField(upload_to='perfiles/', blank=True, null=True)
    favoritos = models.ManyToManyField('aplicacion.Restaurant', blank=True, related_name='usuarios_favoritos')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.foto_perfil:
            path = self.foto_perfil.path
            img = Image.open(path)

            # Tamaño máximo
            max_size = (300, 300)

            # Redimensiona manteniendo proporción
            img.thumbnail(max_size)
            img.save(path)