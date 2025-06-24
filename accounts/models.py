from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class UserType(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        MANAGER = 'MANAGER', 'Gestor'
        COMMON = 'COMMON', 'Usuário Comum'

    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.COMMON
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Adicionando related_name para resolver conflitos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    def is_admin(self):
        return self.user_type == self.UserType.ADMIN

    def is_manager(self):
        return self.user_type == self.UserType.MANAGER

    def is_common_user(self):
        return self.user_type == self.UserType.COMMON

    def __str__(self):
        return self.username

class Platform(models.Model):
    name = models.CharField(max_length=100, unique=True)
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['name']
        db_table = 'plataforma'

    def __str__(self):
        return self.name

class Norm(models.Model):
    name = models.CharField(max_length=100, unique=True)
    link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['name']
        db_table = 'norma'

    def __str__(self):
        return self.name