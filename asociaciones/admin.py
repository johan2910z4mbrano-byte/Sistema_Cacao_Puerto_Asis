from django.contrib import admin
from .models import Asociacion, Membresia, ResponsableAsociacion


@admin.register(Asociacion)
class AsociacionAdmin(admin.ModelAdmin):

    list_display = (
        "nombre",
        "sigla",
        "municipio",
        "vereda",
        "activo",
        "fecha_registro",
    )

    search_fields = (
        "nombre",
        "sigla",
        "municipio",
        "vereda",
    )

    list_filter = (
        "activo",
        "municipio",
        "fecha_registro",
    )

    readonly_fields = (
        "fecha_registro",
        "fecha_actualizacion",
    )


@admin.register(Membresia)
class MembresiaAdmin(admin.ModelAdmin):

    list_display = (
        "productor",
        "asociacion",
        "estado",
        "autorizacion_compartir",
        "fecha_vinculacion",
    )

    search_fields = (
        "productor__codigo",
        "productor__nombres",
        "productor__apellidos",
        "asociacion__nombre",
    )

    list_filter = (
        "estado",
        "autorizacion_compartir",
        "asociacion",
    )

    readonly_fields = (
        "fecha_creacion",
        "fecha_actualizacion",
    )

    list_select_related = (
        "productor",
        "asociacion",
    )

@admin.register(ResponsableAsociacion)
class ResponsableAsociacionAdmin(admin.ModelAdmin):

    list_display = (
        "perfil",
        "asociacion",
        "cargo",
        "activo",
        "fecha_asignacion",
    )

    search_fields = (
        "perfil__usuario__username",
        "perfil__usuario__first_name",
        "perfil__usuario__last_name",
        "asociacion__nombre",
        "cargo",
    )

    list_filter = (
        "activo",
        "asociacion",
        "fecha_asignacion",
    )

    readonly_fields = (
        "fecha_asignacion",
    )

    list_select_related = (
        "perfil",
        "asociacion",
        "perfil__usuario",
    )