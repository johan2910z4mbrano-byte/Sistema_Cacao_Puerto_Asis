from django.urls import path
from . import views

app_name = "produccion"

urlpatterns = [
    # Cosechas
    path("cosechas/", views.lista_cosechas, name="cosechas_lista"),
    path("cosechas/nueva/", views.crear_cosecha, name="cosechas_crear"),
    path(
        "cosechas/<int:pk>/editar/",
        views.editar_cosecha,
        name="cosechas_editar",
    ),

    # Lotes
    path("lotes/", views.lista_lotes, name="lotes_lista"),
    path("lotes/nuevo/", views.crear_lote, name="lotes_crear"),
    path(
        "lotes/<int:pk>/editar/",
        views.editar_lote,
        name="lotes_editar",
    ),

    # Poscosecha
    path("poscosecha/", views.lista_procesos, name="procesos_lista"),
    path(
        "poscosecha/nuevo/",
        views.crear_proceso,
        name="procesos_crear",
    ),
    path(
        "poscosecha/<int:pk>/editar/",
        views.editar_proceso,
        name="procesos_editar",
    ),
]