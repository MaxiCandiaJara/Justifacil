from django.urls import path
from . import views

urlpatterns = [
    # Estudiante
    path("", views.estudiante_dashboard, name="estudiante_dashboard"),
    path("mis/", views.justificacion_list, name="justificacion_list"),
    path("nueva/", views.justificacion_create, name="justificacion_create"),
    path("detalle/<int:pk>/", views.justificacion_detail, name="justificacion_detail"),

    # Coordinador
    path("coordinador/", views.coordinador_dashboard, name="coordinador_dashboard"),
    path("coordinador/revisar/<int:pk>/aprobar/", views.coordinador_aprobar, name="coordinador_aprobar"),
    path("coordinador/revisar/<int:pk>/rechazar/", views.coordinador_rechazar, name="coordinador_rechazar"),

    # Profesor
    path("profesor/", views.profesor_dashboard, name="profesor_dashboard"),

    # WhatsApp stub
    path("whatsapp/recepcion/", views.whatsapp_recepcion, name="whatsapp_recepcion"),
]
