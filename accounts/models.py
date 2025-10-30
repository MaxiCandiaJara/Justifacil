from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import UserManager as DjangoUserManager


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ESTUDIANTE = "ESTUDIANTE", "Estudiante"
        PROFESOR = "PROFESOR", "Profesor"
        COORDINADOR = "COORDINADOR", "Coordinador"
        ADMINISTRATIVO = "ADMINISTRATIVO", "Administrativo"

    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.ESTUDIANTE)

    def is_estudiante(self) -> bool:
        return self.rol == self.Rol.ESTUDIANTE

    def is_profesor(self) -> bool:
        return self.rol == self.Rol.PROFESOR

    def is_coordinador(self) -> bool:
        return self.rol == self.Rol.COORDINADOR


class EstudianteManager(DjangoUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(rol=Usuario.Rol.ESTUDIANTE)


class ProfesorManager(DjangoUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(rol=Usuario.Rol.PROFESOR)


class CoordinadorManager(DjangoUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(rol=Usuario.Rol.COORDINADOR)


class Estudiante(Usuario):
    objects = EstudianteManager()

    class Meta:
        proxy = True
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"


class Profesor(Usuario):
    objects = ProfesorManager()

    class Meta:
        proxy = True
        verbose_name = "Profesor"
        verbose_name_plural = "Profesores"


class Coordinador(Usuario):
    objects = CoordinadorManager()

    class Meta:
        proxy = True
        verbose_name = "Coordinador"
        verbose_name_plural = "Coordinadores"
