from django.urls import path
from . import views

app_name = "productores"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path(
        "productores/",
        views.lista_productores,
        name="lista"
    ),

    path(
        "productores/nuevo/",
        views.crear_productor,
        name="crear"
    ),

    path(
        "productores/<int:pk>/editar/",
        views.editar_productor,
        name="editar"
    ),

    path(
        "productores/<int:pk>/estado/",
        views.cambiar_estado,
        name="cambiar_estado"
    ),
]