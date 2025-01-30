from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# Modello per gli Amministratori
class Administrator(AbstractUser):
    first_name = models.CharField(max_length=255, verbose_name="Nome")
    last_name = models.CharField(max_length=255, verbose_name="Cognome")
    email = models.EmailField(unique=True, verbose_name="Email")
    password = models.CharField(max_length=255, verbose_name="Password")

    groups = models.ManyToManyField(Group, related_name='admin_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='admin_permissions')
    
    def __str__(self):
        return self.email

# Modello per gli Utenti (User)
class User(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255, verbose_name="Nome")
    last_name = models.CharField(max_length=255, verbose_name="Cognome")
    unlock_code = models.CharField(max_length=6, verbose_name="Codice di sblocco")

    groups = models.ManyToManyField(Group, related_name='user_groups')
    user_permissions = models.ManyToManyField(Permission, related_name='user_permissions')
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (Codice: {self.unlock_code})"
