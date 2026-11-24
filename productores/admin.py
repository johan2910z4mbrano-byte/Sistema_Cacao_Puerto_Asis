from django.contrib import admin
from .models import Productor


@admin.register(Productor)
class ProductorAdmin(admin.ModelAdmin):

    list_display = (
        "codigo",
        "nombres",
        "apellidos",
        "telefono",
        "vereda",
        "activo",
        "fecha_registro",
    )

    search_fields = (
        "codigo",
        "nombres",
        "apellidos",
        "vereda",
    )

    list_filter = (
        "activo",
        "fecha_registro",
    )

    ordering = ("apellidos", "nombres")

    readonly_fields = (
        "fecha_registro",
        "fecha_actualizacion",
    )

# Register your models here.
