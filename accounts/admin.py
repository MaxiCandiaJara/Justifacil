from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario, Estudiante, Profesor, Coordinador


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Rol", {"fields": ("rol",)}),)
    list_display = ("username", "email", "first_name", "last_name", "rol", "is_active")
    list_filter = ("rol", "is_active", "is_staff", "is_superuser")


@admin.register(Estudiante)
class EstudianteProxyAdmin(UserAdmin):
    def get_queryset(self, request):
        return Estudiante.objects.all()


@admin.register(Profesor)
class ProfesorProxyAdmin(UserAdmin):
    def get_queryset(self, request):
        return Profesor.objects.all()


@admin.register(Coordinador)
class CoordinadorProxyAdmin(UserAdmin):
    def get_queryset(self, request):
        return Coordinador.objects.all()
