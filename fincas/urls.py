from django.urls import path
from . import views

app_name = "fincas"

urlpatterns = [

    path(
        "fincas/",
        views.lista_fincas,
        name="lista"
    ),

    path(
        "fincas/nueva/",
        views.crear_finca,
        name="crear"
    ),

    path(
        "fincas/<int:pk>/editar/",
        views.editar_finca,
        name="editar"
    ),

    path(
        "fincas/<int:pk>/estado/",
        views.cambiar_estado_finca,
        name="cambiar_estado"
    ),
]