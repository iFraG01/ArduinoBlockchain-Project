from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

# 1️⃣ SUPERUSER (Amministratore con accesso alla dashboard)
class Administrator(AbstractUser):  
    groups = models.ManyToManyField(Group, related_name="administrator_groups")
    user_permissions = models.ManyToManyField(Permission, related_name="administrator_permissions")

    def __str__(self):
        return self.username  # Identifica l'amministratore con il nome utente


# 2️⃣ UTENTI NORMALI (Solo nome, cognome e codice, senza accesso)
class User(models.Model):
    first_name = models.CharField(max_length=255, verbose_name="Nome")
    last_name = models.CharField(max_length=255, verbose_name="Cognome")
    unlock_code = models.CharField(max_length=6, unique=True, verbose_name="Codice di Sblocco")

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Codice: {self.unlock_code}"
