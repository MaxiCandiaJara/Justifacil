import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_profesor_dashboard_filtra_por_nombre(cliente_profesor, usuario_estudiante):
    url = reverse("profesor_dashboard")
    resp = cliente_profesor.get(url + "?q=alum")

    assert resp.status_code == 200
    assert b"alum" in resp.content
