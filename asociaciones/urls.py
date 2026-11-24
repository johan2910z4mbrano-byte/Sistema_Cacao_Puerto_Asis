from django.urls import path
from . import views

app_name = "asociaciones"

urlpatterns = [

    # Gestión de asociaciones
    path(
        "asociaciones/",
        views.lista_asociaciones,
        name="lista"
    ),

    path(
        "asociaciones/nueva/",
        views.crear_asociacion,
        name="crear"
    ),

    path(
        "asociaciones/<int:pk>/editar/",
        views.editar_asociacion,
        name="editar"
    ),

    path(
        "asociaciones/<int:pk>/estado/",
        views.cambiar_estado,
        name="cambiar_estado"
    ),

    # Gestión de membresías
    path(
        "membresias/",
        views.lista_membresias,
        name="membresias_lista"
    ),

    path(
        "membresias/nueva/",
        views.crear_membresia,
        name="membresias_crear"
    ),

    path(
        "membresias/<int:pk>/editar/",
        views.editar_membresia,
        name="membresias_editar"
    ),

    path(
        "membresias/<int:pk>/estado/",
        views.cambiar_estado_membresia,
        name="membresias_cambiar_estado"
    ),
]