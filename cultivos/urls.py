from django.urls import path
from . import views

app_name = "cultivos"

urlpatterns = [
    # Gestión de cultivos
    path("cultivos/", views.lista_cultivos, name="lista"),
    path("cultivos/nuevo/", views.crear_cultivo, name="crear"),
    path("cultivos/<int:pk>/editar/", views.editar_cultivo, name="editar"),

    # Gestión de actividades agrícolas
    path("actividades/", views.lista_actividades, name="actividades_lista"),
    path("actividades/nueva/", views.crear_actividad, name="actividades_crear"),
    path(
        "actividades/<int:pk>/editar/",
        views.editar_actividad,
        name="actividades_editar",
    ),
]