from __future__ import annotations
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator


class Justificacion(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        APROBADA = "APROBADA", "Aprobada"
        RECHAZADA = "RECHAZADA", "Rechazada"

    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="justificaciones")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    motivo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    comentarios_coordinador = models.TextField(blank=True)
    fuente = models.CharField(max_length=30, default="app")  # app | whatsapp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Justificación #{self.pk} - {self.estudiante} - {self.estado}"


class Documento(models.Model):
    justificacion = models.ForeignKey(Justificacion, on_delete=models.CASCADE, related_name="documentos")
    archivo = models.FileField(upload_to="documentos/", validators=[FileExtensionValidator(allowed_extensions=['pdf', 'png'])])
    legible = models.BooleanField(default=False)
    validado_en = models.DateTimeField(blank=True, null=True)

    def validar_legibilidad(self) -> None:
        # Validación básica como stub: si el tamaño > 0 lo consideramos legible
        if self.archivo and self.archivo.size >= 1:
            self.legible = True
            self.validado_en = timezone.now()
        else:
            self.legible = False
            self.validado_en = timezone.now()
        self.save(update_fields=["legible", "validado_en"])

    def __str__(self) -> str:
        return f"Documento #{self.pk} de Justificación #{self.justificacion_id}"


class Notificacion(models.Model):
    destinatario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mensaje = models.TextField()
    canal = models.CharField(max_length=20, default="email")  # email | app | sms
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Notificación a {self.destinatario} por {self.canal}"
