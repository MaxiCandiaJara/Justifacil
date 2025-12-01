import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def usuario_estudiante(db):
    return User.objects.create_user(username="alumno", password="1234", rol="ESTUDIANTE")


@pytest.fixture
def usuario_coordinador(db):
    return User.objects.create_user(username="coord", password="1234", rol="COORDINADOR")


@pytest.fixture
def usuario_profesor(db):
    return User.objects.create_user(username="profe", password="1234", rol="PROFESOR")


@pytest.fixture
def cliente_estudiante(client, usuario_estudiante):
    client.force_login(usuario_estudiante)
    return client


@pytest.fixture
def cliente_coordinador(client, usuario_coordinador):
    client.force_login(usuario_coordinador)
    return client


@pytest.fixture
def cliente_profesor(client, usuario_profesor):
    client.force_login(usuario_profesor)
    return client
