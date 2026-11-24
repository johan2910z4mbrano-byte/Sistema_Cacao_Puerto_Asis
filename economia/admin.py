from django.contrib import admin

from .models import MovimientoEconomico


@admin.register(MovimientoEconomico)
class MovimientoEconomicoAdmin(admin.ModelAdmin):

    list_display = (
        "fecha",
        "finca",
        "tipo",
        "categoria",
        "valor",
    )

    list_filter = (
        "tipo",
        "categoria",
        "fecha",
    )

    search_fields = (
        "finca__nombre",
        "descripcion",
    )

    date_hierarchy = "fecha"