# JustiFácil

Aplicación Django para registro y validación de inasistencias con roles (Estudiante, Profesor, Coordinador), subida de documentos y notificaciones.

## Desarrollo rápido

1. Crear entorno e instalar dependencias
```
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
2. Migraciones y superusuario
```
python manage.py migrate
python manage.py createsuperuser
```
3. Ejecutar
```
python manage.py runserver
```
