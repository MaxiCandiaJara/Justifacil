# JustiFácil

Aplicación Django para el registro y validación de inasistencias académicas. Permite:

- Gestión de roles: Estudiante, Profesor y Coordinador.
- Envío y almacenamiento de documentos de respaldo (PDF/PNG).
- Validación básica de documentos y notificaciones internas.

## Requisitos

- Python 3.8+ (ya instalado en el sistema).
- Las dependencias del proyecto están en `requirements.txt` (opcional si no necesita instalar extras).

Nota: No es necesario crear un entorno virtual para ejecutar la aplicación si solo quieres probarla localmente. Con tener Python instalado, `python manage.py runserver` funciona. Usar un entorno virtual sigue siendo buena práctica para desarrollo y despliegue, pero no es obligatorio.

## Inicio rápido

1. (Opcional) Instalar dependencias si las necesitas:
```
pip install -r requirements.txt
```

2. Aplicar migraciones:
```
python manage.py migrate
```

3. (Opcional) Crear superusuario para acceder al admin:
```
python manage.py createsuperuser
```

4. Ejecutar el servidor de desarrollo:
```
python manage.py runserver
``` 

Después de esto la app estará disponible en http://127.0.0.1:8000/ y el panel de admin en http://127.0.0.1:8000/admin/ (si creaste un superusuario).

## Test unitarios

Para realizar los test se deben instalar dependencias
```
pip install pytest pytest-django pytest-cov
```

## Notas

- Seguridad: si vas a desplegar en producción, NO uses el servidor de desarrollo. Configura un servidor WSGI/ASGI apropiado y revisa settings de seguridad.
- Validación de archivos: el sistema solo acepta por defecto archivos con extensión PDF o PNG. Si necesitas admitir más formatos, actualiza la lista de extensiones en `justificaciones/models.py` y `justificaciones/forms.py`.

