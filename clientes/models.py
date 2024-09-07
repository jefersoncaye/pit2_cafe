from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Clientes(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    endereco = models.TextField()

    class Meta:
        db_table = 'clientes'

    def __str__(self):
        return self.user.username