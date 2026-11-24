from django.contrib import admin
from .models import Cultivo, ActividadAgricola


@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):

    list_display = (
        "codigo",
        "finca",
        "tipo_cultivo",
        "variedad",
        "area_hectareas",
        "cantidad_plantulas",
        "estado",
        "fecha_siembra",
    )

    search_fields = (
        "codigo",
        "finca__codigo",
        "finca__nombre",
        "finca__productor__nombres",
        "finca__productor__apellidos",
        "variedad",
    )

    list_filter = (
        "tipo_cultivo",
        "estado",
        "fecha_siembra",
    )

    readonly_fields = (
        "fecha_registro",
        "fecha_actualizacion",
    )

    list_select_related = (
        "finca",
        "finca__productor",
    )


@admin.register(ActividadAgricola)
class ActividadAgricolaAdmin(admin.ModelAdmin):

    list_display = (
        "cultivo",
        "tipo_actividad",
        "fecha",
        "responsable",
        "costo_estimado",
    )

    search_fields = (
        "cultivo__codigo",
        "cultivo__finca__nombre",
        "descripcion",
        "responsable",
    )

    list_filter = (
        "tipo_actividad",
        "fecha",
    )

    readonly_fields = (
        "fecha_registro",
    )

    list_select_related = (
        "cultivo",
        "cultivo__finca",
    )

    date_hierarchy = "fecha"