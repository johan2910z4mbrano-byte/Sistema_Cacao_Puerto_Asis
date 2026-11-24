from django.contrib import admin
from .models import Finca, DelimitacionFinca


@admin.register(Finca)
class FincaAdmin(admin.ModelAdmin):

    list_display = (
        "codigo",
        "nombre",
        "productor",
        "municipio",
        "vereda",
        "area_hectareas",
        "activa",
    )

    search_fields = (
        "codigo",
        "nombre",
        "productor__codigo",
        "productor__nombres",
        "productor__apellidos",
        "vereda",
    )

    list_filter = (
        "activa",
        "municipio",
        "departamento",
    )

    readonly_fields = (
        "fecha_registro",
        "fecha_actualizacion",
    )

    list_select_related = ("productor",)


@admin.register(DelimitacionFinca)
class DelimitacionFincaAdmin(admin.ModelAdmin):

    list_display = (
        "finca",
        "precision_metros",
        "fecha_registro",
    )

    search_fields = (
        "finca__codigo",
        "finca__nombre",
        "finca__productor__nombres",
        "finca__productor__apellidos",
    )

    readonly_fields = ("fecha_registro",)

    list_select_related = ("finca",)