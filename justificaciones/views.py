from __future__ import annotations
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import Usuario
from .forms import JustificacionForm, DocumentoForm
from .models import Justificacion, Documento, Notificacion


def require_role(*roles: str):
    def decorator(view_func):
        def _wrapped(request: HttpRequest, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if roles and getattr(request.user, "rol", None) not in roles:
                messages.error(request, "No tienes permisos para acceder a esta sección.")
                return redirect("home")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


@login_required
@require_role("ESTUDIANTE", "ADMINISTRATIVO")
def estudiante_dashboard(request: HttpRequest) -> HttpResponse:
    justificaciones = Justificacion.objects.filter(estudiante=request.user).order_by("-created_at")
    return render(request, "justificaciones/estudiante_dashboard.html", {"justificaciones": justificaciones})


@login_required
def justificacion_list(request: HttpRequest) -> HttpResponse:
    if request.user.is_coordinador() or request.user.is_profesor():
        qs = Justificacion.objects.all().order_by("-created_at")
    else:
        qs = Justificacion.objects.filter(estudiante=request.user).order_by("-created_at")
    return render(request, "justificaciones/justificacion_list.html", {"justificaciones": qs})


@login_required
@require_role("ESTUDIANTE", "ADMINISTRATIVO")
def justificacion_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = JustificacionForm(request.POST)
        doc_form = DocumentoForm(request.POST, request.FILES)
        if form.is_valid() and doc_form.is_valid():
            justi: Justificacion = form.save(commit=False)
            justi.estudiante = request.user
            justi.fuente = "app"
            justi.save()
            if doc_form.cleaned_data.get("archivo"):
                documento: Documento = doc_form.save(commit=False)
                documento.justificacion = justi
                documento.save()
                documento.validar_legibilidad()
            messages.success(request, "Justificación enviada correctamente.")
            return redirect("justificacion_detail", pk=justi.pk)
    else:
        form = JustificacionForm()
        doc_form = DocumentoForm()
    return render(request, "justificaciones/justificacion_form.html", {"form": form, "doc_form": doc_form})


@login_required
def justificacion_detail(request: HttpRequest, pk: int) -> HttpResponse:
    justi = get_object_or_404(Justificacion, pk=pk)
    if not (request.user.is_superuser or request.user.is_coordinador() or request.user.is_profesor() or justi.estudiante_id == request.user.id):
        messages.error(request, "No tienes permisos para ver esta justificación.")
        return redirect("home")
    return render(request, "justificaciones/justificacion_detail.html", {"justificacion": justi})


@login_required
@require_role("COORDINADOR")
def coordinador_dashboard(request: HttpRequest) -> HttpResponse:
    pendientes = Justificacion.objects.filter(estado=Justificacion.Estado.PENDIENTE).order_by("created_at")
    return render(request, "justificaciones/coordinador_dashboard.html", {"pendientes": pendientes})


@login_required
@require_role("COORDINADOR")
@require_http_methods(["POST"]) 
def coordinador_aprobar(request: HttpRequest, pk: int) -> HttpResponse:
    justi = get_object_or_404(Justificacion, pk=pk)
    comentario = request.POST.get("comentarios_coordinador", "")
    justi.estado = Justificacion.Estado.APROBADA
    justi.comentarios_coordinador = comentario
    justi.save(update_fields=["estado", "comentarios_coordinador", "updated_at"])
    _notificar_cambio_estado(justi)
    messages.success(request, "Justificación aprobada y notificación enviada.")
    return redirect("coordinador_dashboard")


@login_required
@require_role("COORDINADOR")
@require_http_methods(["POST"]) 
def coordinador_rechazar(request: HttpRequest, pk: int) -> HttpResponse:
    justi = get_object_or_404(Justificacion, pk=pk)
    comentario = request.POST.get("comentarios_coordinador", "")
    justi.estado = Justificacion.Estado.RECHAZADA
    justi.comentarios_coordinador = comentario
    justi.save(update_fields=["estado", "comentarios_coordinador", "updated_at"])
    _notificar_cambio_estado(justi)
    messages.info(request, "Justificación rechazada y notificación enviada.")
    return redirect("coordinador_dashboard")


@login_required
@require_role("PROFESOR")
def profesor_dashboard(request: HttpRequest) -> HttpResponse:
    # Simplificado: listado general; se puede filtrar por alumno.
    q = request.GET.get("q", "").strip()
    qs = Justificacion.objects.all().select_related("estudiante").order_by("-created_at")
    if q:
        qs = qs.filter(estudiante__username__icontains=q)
    return render(request, "justificaciones/profesor_dashboard.html", {"justificaciones": qs, "q": q})


@require_http_methods(["POST"]) 
def whatsapp_recepcion(request: HttpRequest) -> HttpResponse:
    # Stub: recibe JSON simple con {username, motivo, descripcion, fecha}
    try:
        import json
        payload = json.loads(request.body.decode("utf-8"))
        username = payload.get("username")
        motivo = payload.get("motivo") or "Inasistencia reportada por WhatsApp"
        descripcion = payload.get("descripcion", "")
        fecha = payload.get("fecha")  # "YYYY-MM-DD"
        user = Usuario.objects.get(username=username)
        justi = Justificacion.objects.create(
            estudiante=user,
            fecha_inicio=fecha,
            motivo=motivo,
            descripcion=descripcion,
            fuente="whatsapp",
        )
        return JsonResponse({"ok": True, "id": justi.id})
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


def _notificar_cambio_estado(justi: Justificacion) -> None:
    asunto = f"Tu justificación #{justi.pk} fue {justi.estado.lower()}"
    cuerpo = (
        f"Hola {justi.estudiante.get_full_name() or justi.estudiante.username},\n\n"
        f"Estado: {justi.get_estado_display()}\n"
        f"Comentario: {justi.comentarios_coordinador or 'Sin comentarios'}\n\n"
        f"Saludos,\nEquipo JustiFácil"
    )
    send_mail(asunto, cuerpo, None, [justi.estudiante.email or "devnull@example.com"], fail_silently=True)
    Notificacion.objects.create(destinatario=justi.estudiante, mensaje=cuerpo, canal="email")
