from django.contrib import admin
from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):

    list_display = (
        "usuario",
        "tipo_usuario",
        "fecha_creacion",
        "fecha_actualizacion",
    )

    list_filter = (
        "tipo_usuario",
        "fecha_creacion",
    )

    search_fields = (
        "usuario__username",
        "usuario__first_name",
        "usuario__last_name",
        "usuario__email",
    )

    readonly_fields = (
        "fecha_creacion",
        "fecha_actualizacion",
    )