from django.urls import path
from . import views

app_name = "economia"

urlpatterns = [
    # Movimientos económicos
    path(
        "economia/",
        views.lista_movimientos,
        name="movimientos_lista",
    ),
    path(
        "economia/nuevo/",
        views.crear_movimiento,
        name="movimientos_crear",
    ),
    path(
        "economia/<int:pk>/editar/",
        views.editar_movimiento,
        name="movimientos_editar",
    ),

    # Balance económico
    path(
        "economia/balance/",
        views.balance_economico,
        name="balance",
    ),

    # Exportaciones
    path(
        "economia/balance/exportar/excel/",
        views.exportar_balance_excel,
        name="balance_excel",
    ),
    path(
        "economia/balance/exportar/pdf/",
        views.exportar_balance_pdf,
        name="balance_pdf",
    ),
]