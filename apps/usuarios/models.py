"""
Model ORM do Usuário — camada de infraestrutura/Django.
Estende AbstractBaseUser para ter controle total sobre os campos,
incluindo o perfil ADMIN/FUNCIONARIO exigido pelo projeto.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("O username é obrigatório.")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('perfil', 'ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Entidade Usuario — armazena credenciais e perfil de acesso.
    A senha é sempre armazenada com hash (Django cuida disso via set_password).
    """
    PERFIL_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('FUNCIONARIO', 'Funcionário'),
    ]

    username = models.CharField(max_length=50, unique=True)
    email    = models.EmailField(max_length=100, blank=True, null=True)
    perfil   = models.CharField(max_length=15, choices=PERFIL_CHOICES, default='FUNCIONARIO')
    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return f"{self.username} ({self.perfil})"

    @property
    def is_admin(self):
        return self.perfil == 'ADMIN'
