import pytest
from django.urls import reverse
from justificaciones.models import Justificacion


@pytest.mark.django_db
def test_whatsapp_recepcion(usuario_estudiante, client):
    payload = {
        "username": usuario_estudiante.username,
        "motivo": "Dolor",
        "descripcion": "No puedo asistir",
        "fecha": "2025-01-10"
    }

    resp = client.post(
        reverse("whatsapp_recepcion"),
        data=payload,
        content_type="application/json"
    )

    assert resp.status_code == 200
    assert Justificacion.objects.count() == 1
    assert Justificacion.objects.first().fuente == "whatsapp"
