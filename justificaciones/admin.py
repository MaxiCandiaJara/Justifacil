from django.contrib import admin
from .models import Justificacion, Documento, Notificacion


@admin.register(Justificacion)
class JustificacionAdmin(admin.ModelAdmin):
    list_display = ("id", "estudiante", "fecha_inicio", "fecha_fin", "estado", "fuente", "created_at")
    list_filter = ("estado", "fuente", "created_at")
    search_fields = ("estudiante__username", "motivo", "descripcion")


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ("id", "justificacion", "legible", "validado_en")


@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("id", "destinatario", "canal", "created_at")
