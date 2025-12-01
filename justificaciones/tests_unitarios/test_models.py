import pytest
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from justificaciones.models import Justificacion, Documento, Notificacion


@pytest.mark.django_db
def test_model_justificacion_str(usuario_estudiante):
    j = Justificacion.objects.create(
        estudiante=usuario_estudiante,
        fecha_inicio="2025-01-01",
        motivo="Enfermedad"
    )
    assert str(j) == f"Justificación #{j.pk} - {usuario_estudiante} - {j.estado}"


@pytest.mark.django_db
def test_documento_validar_legibilidad(usuario_estudiante):
    justi = Justificacion.objects.create(
        estudiante=usuario_estudiante,
        fecha_inicio="2025-01-01",
        motivo="Enfermedad"
    )
    archivo = SimpleUploadedFile("doc.pdf", b"contenido")

    doc = Documento.objects.create(justificacion=justi, archivo=archivo)

    doc.validar_legibilidad()
    doc.refresh_from_db()

    assert doc.legible is True
    assert isinstance(doc.validado_en, timezone.datetime)


@pytest.mark.django_db
def test_notificacion_str(usuario_estudiante):
    notif = Notificacion.objects.create(
        destinatario=usuario_estudiante,
        mensaje="Mensaje de prueba"
    )
    assert "Notificación a" in str(notif)
