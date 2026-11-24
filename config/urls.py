
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Autenticación de usuarios
    path("accounts/", include("django.contrib.auth.urls")),

    # Aplicaciones del sistema
    path("", include("asociaciones.urls")),
    path("", include("productores.urls")),
    path("", include("cultivos.urls")),
    path("", include("fincas.urls")),
    path("", include("produccion.urls")),
    path("", include("economia.urls")),
]
