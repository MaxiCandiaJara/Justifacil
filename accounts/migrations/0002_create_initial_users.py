from django.db import migrations
from django.contrib.auth.hashers import make_password


def create_initial_users(apps, schema_editor):
    Usuario = apps.get_model('accounts', 'Usuario')

    users = [
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'first_name': 'Admin',
            'rol': 'ADMINISTRATIVO',
            'is_staff': True,
            'is_superuser': True,
            'password': 'adminpass123',
        },
        {
            'username': 'coordinador',
            'email': 'coord@example.com',
            'first_name': 'Coord',
            'rol': 'COORDINADOR',
            'is_staff': True,
            'is_superuser': False,
            'password': 'coordpass123',
        },
        {
            'username': 'profesor1',
            'email': 'prof1@example.com',
            'first_name': 'Profesor',
            'rol': 'PROFESOR',
            'is_staff': False,
            'is_superuser': False,
            'password': 'profpass123',
        },
        {
            'username': 'estudiante1',
            'email': 'est1@example.com',
            'first_name': 'Estudiante',
            'rol': 'ESTUDIANTE',
            'is_staff': False,
            'is_superuser': False,
            'password': 'estpass123',
        },
    ]

    for u in users:
        if not Usuario.objects.filter(username=u['username']).exists():
            user = Usuario(
                username=u['username'],
                email=u['email'],
                first_name=u.get('first_name', ''),
                rol=u.get('rol', 'ESTUDIANTE'),
                is_staff=u.get('is_staff', False),
                is_superuser=u.get('is_superuser', False),
            )
            # Historical models in migrations may not have set_password; hash manually
            user.password = make_password(u['password'])
            user.save()


def delete_initial_users(apps, schema_editor):
    Usuario = apps.get_model('accounts', 'Usuario')
    usernames = ['admin', 'coordinador', 'profesor1', 'estudiante1']
    Usuario.objects.filter(username__in=usernames).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_users, reverse_code=delete_initial_users),
    ]
