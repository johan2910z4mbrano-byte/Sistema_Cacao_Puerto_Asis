from django.contrib import admin

from .models import (
    Cosecha,
    LoteProduccion,
    ProcesoPoscosecha
)


@admin.register(Cosecha)
class CosechaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "cultivo",
        "fecha_cosecha",
        "cantidad_kg",
    )
    search_fields = (
        "codigo",
        "cultivo__codigo",
    )
    list_filter = ("fecha_cosecha",)


@admin.register(LoteProduccion)
class LoteProduccionAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "cosecha",
        "cantidad_inicial_kg",
        "estado",
    )
    search_fields = (
        "codigo",
        "cosecha__codigo",
    )
    list_filter = ("estado",)


@admin.register(ProcesoPoscosecha)
class ProcesoPoscosechaAdmin(admin.ModelAdmin):
    list_display = (
        "lote",
        "etapa",
        "fecha_inicio",
        "fecha_fin",
        "cantidad_entrada_kg",
        "cantidad_salida_kg",
    )
    search_fields = (
        "lote__codigo",
    )
    list_filter = (
        "etapa",
        "fecha_inicio",
    )