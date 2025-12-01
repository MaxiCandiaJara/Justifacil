import pytest
from django.urls import reverse
from justificaciones.models import Justificacion


@pytest.mark.django_db
def test_estudiante_dashboard(cliente_estudiante, usuario_estudiante):
    Justificacion.objects.create(
        estudiante=usuario_estudiante,
        fecha_inicio="2025-01-01",
        motivo="Prueba"
    )
    url = reverse("estudiante_dashboard")
    resp = cliente_estudiante.get(url)

    assert resp.status_code == 200
    assert b"Prueba" in resp.content
