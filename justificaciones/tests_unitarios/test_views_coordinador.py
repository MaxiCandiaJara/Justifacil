import pytest
from unittest.mock import patch
from django.urls import reverse
from justificaciones.models import Justificacion, Notificacion


@pytest.mark.django_db
def test_coordinador_aprueba(cliente_coordinador, usuario_estudiante):
    j = Justificacion.objects.create(
        estudiante=usuario_estudiante,
        fecha_inicio="2025-01-01",
        motivo="X"
    )

    url = reverse("coordinador_aprobar", args=[j.pk])

    with patch("justificaciones.views.send_mail") as mock_mail:
        resp = cliente_coordinador.post(url, {"comentarios_coordinador": "OK"})

    assert resp.status_code == 302

    j.refresh_from_db()
    assert j.estado == "APROBADA"
    assert j.comentarios_coordinador == "OK"

    # se creó la notificación
    assert Notificacion.objects.filter(destinatario=usuario_estudiante).exists()

    mock_mail.assert_called_once()


@pytest.mark.django_db
def test_coordinador_rechaza(cliente_coordinador, usuario_estudiante):
    j = Justificacion.objects.create(
        estudiante=usuario_estudiante,
        fecha_inicio="2025-01-01",
        motivo="X"
    )

    url = reverse("coordinador_rechazar", args=[j.pk])
    resp = cliente_coordinador.post(url, {"comentarios_coordinador": "NO"})

    j.refresh_from_db()
    assert j.estado == "RECHAZADA"
