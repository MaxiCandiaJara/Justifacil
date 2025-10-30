from django.urls import path
from django.contrib.auth import views as auth_views
from .views import home, logout_view

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", logout_view, name="logout"),
    path("home/", home, name="home"),
]
