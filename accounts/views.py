from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import logout


@login_required
def home(request: HttpRequest) -> HttpResponse:
    user = request.user
    if getattr(user, "rol", None) == "COORDINADOR":
        return redirect("coordinador_dashboard")
    if getattr(user, "rol", None) == "PROFESOR":
        return redirect("profesor_dashboard")
    # Default: estudiante
    return redirect("estudiante_dashboard")


def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    messages.success(request, "Has cerrado sesión correctamente.")
    return redirect("login")
