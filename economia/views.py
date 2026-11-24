
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum, DecimalField, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date

from openpyxl import Workbook
from openpyxl.styles import (
    Font,
    PatternFill,
    Alignment,
    Border,
    Side,
)

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from xml.sax.saxutils import escape

from .models import MovimientoEconomico
from .forms import MovimientoEconomicoForm

from cuentas.permisos import (
    es_administrador,
    es_productor,
    fincas_economicas_visibles as fincas_visibles,
    movimientos_visibles,
    puede_editar_movimiento,
)


# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

def puede_modificar_economia(usuario):
    return es_administrador(usuario) or es_productor(usuario)


def obtener_fechas(parametros):

    fecha_desde = parse_date(
        parametros.get("desde", "")
    )

    fecha_hasta = parse_date(
        parametros.get("hasta", "")
    )

    return fecha_desde, fecha_hasta


# =====================================================
# LISTADO DE MOVIMIENTOS ECONÓMICOS
# =====================================================

@login_required
def lista_movimientos(request):

    busqueda = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "todos")
    finca_id = request.GET.get("finca", "todos")

    fecha_desde, fecha_hasta = obtener_fechas(request.GET)

    movimientos = movimientos_visibles(
        request.user
    ).select_related(
        "finca",
        "finca__productor",
        "cosecha",
    )

    if tipo in (
        MovimientoEconomico.TipoMovimiento.INGRESO,
        MovimientoEconomico.TipoMovimiento.GASTO,
    ):
        movimientos = movimientos.filter(tipo=tipo)

    if finca_id.isdigit():
        movimientos = movimientos.filter(
            finca_id=int(finca_id)
        )

    if fecha_desde:
        movimientos = movimientos.filter(
            fecha__gte=fecha_desde
        )

    if fecha_hasta:
        movimientos = movimientos.filter(
            fecha__lte=fecha_hasta
        )

    if busqueda:
        movimientos = movimientos.filter(
            Q(finca__nombre__icontains=busqueda)
            | Q(finca__productor__nombres__icontains=busqueda)
            | Q(finca__productor__apellidos__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
            | Q(cosecha__codigo__icontains=busqueda)
        )

    resumen = movimientos.aggregate(
        ingresos=Sum(
            "valor",
            filter=Q(
                tipo=MovimientoEconomico.TipoMovimiento.INGRESO
            ),
        ),
        gastos=Sum(
            "valor",
            filter=Q(
                tipo=MovimientoEconomico.TipoMovimiento.GASTO
            ),
        ),
    )

    ingresos = resumen["ingresos"] or Decimal("0.00")
    gastos = resumen["gastos"] or Decimal("0.00")

    return render(
        request,
        "economia/movimientos_lista.html",
        {
            "movimientos": movimientos,
            "busqueda": busqueda,
            "tipo": tipo,
            "finca_id": finca_id,
            "fincas": fincas_visibles(
                request.user
            ).order_by("nombre"),
            "fecha_desde": request.GET.get("desde", ""),
            "fecha_hasta": request.GET.get("hasta", ""),
            "ingresos": ingresos,
            "gastos": gastos,
            "balance": ingresos - gastos,
            "puede_modificar": puede_modificar_economia(
                request.user
            ),
        },
    )


# =====================================================
# CREAR MOVIMIENTO ECONÓMICO
# =====================================================

@login_required
def crear_movimiento(request):

    if not puede_modificar_economia(request.user):
        raise PermissionDenied(
            "Tu perfil no tiene autorización para registrar movimientos económicos."
        )

    if request.method == "POST":

        form = MovimientoEconomicoForm(
            request.POST,
            usuario=request.user,
        )

        if form.is_valid():

            movimiento = form.save()

            messages.success(
                request,
                "El movimiento económico fue registrado correctamente.",
            )

            return redirect("economia:movimientos_lista")

    else:
        form = MovimientoEconomicoForm(
            usuario=request.user
        )

    return render(
        request,
        "economia/movimiento_formulario.html",
        {
            "form": form,
            "titulo": "Registrar movimiento económico",
        },
    )


# =====================================================
# EDITAR MOVIMIENTO ECONÓMICO
# =====================================================

@login_required
def editar_movimiento(request, pk):

    movimiento = get_object_or_404(
        movimientos_visibles(request.user),
        pk=pk,
    )

    if not puede_editar_movimiento(
        request.user,
        movimiento,
    ):
        raise PermissionDenied(
            "No tienes autorización para modificar este movimiento económico."
        )

    if request.method == "POST":

        form = MovimientoEconomicoForm(
            request.POST,
            instance=movimiento,
            usuario=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "El movimiento económico fue actualizado correctamente.",
            )

            return redirect("economia:movimientos_lista")

    else:
        form = MovimientoEconomicoForm(
            instance=movimiento,
            usuario=request.user,
        )

    return render(
        request,
        "economia/movimiento_formulario.html",
        {
            "form": form,
            "titulo": "Editar movimiento económico",
        },
    )


# =====================================================
# OBTENER BALANCE POR FINCA
# =====================================================

def obtener_datos_balance(usuario, parametros):

    fecha_desde, fecha_hasta = obtener_fechas(parametros)

    filtro_ingreso = Q(
        movimientos_economicos__tipo=
        MovimientoEconomico.TipoMovimiento.INGRESO
    )

    filtro_gasto = Q(
        movimientos_economicos__tipo=
        MovimientoEconomico.TipoMovimiento.GASTO
    )

    if fecha_desde:

        filtro_ingreso &= Q(
            movimientos_economicos__fecha__gte=fecha_desde
        )

        filtro_gasto &= Q(
            movimientos_economicos__fecha__gte=fecha_desde
        )

    if fecha_hasta:

        filtro_ingreso &= Q(
            movimientos_economicos__fecha__lte=fecha_hasta
        )

        filtro_gasto &= Q(
            movimientos_economicos__fecha__lte=fecha_hasta
        )

    campo_moneda = DecimalField(
        max_digits=16,
        decimal_places=2,
    )

    fincas = list(
        fincas_visibles(usuario).annotate(

            ingresos=Coalesce(
                Sum(
                    "movimientos_economicos__valor",
                    filter=filtro_ingreso,
                ),
                Value(Decimal("0.00")),
                output_field=campo_moneda,
            ),

            gastos=Coalesce(
                Sum(
                    "movimientos_economicos__valor",
                    filter=filtro_gasto,
                ),
                Value(Decimal("0.00")),
                output_field=campo_moneda,
            ),

        ).select_related(
            "productor"
        ).order_by("nombre")
    )

    for finca in fincas:
        finca.balance = finca.ingresos - finca.gastos

    total_ingresos = sum(
        (finca.ingresos for finca in fincas),
        Decimal("0.00"),
    )

    total_gastos = sum(
        (finca.gastos for finca in fincas),
        Decimal("0.00"),
    )

    return {
        "fincas": fincas,
        "total_ingresos": total_ingresos,
        "total_gastos": total_gastos,
        "balance_general": total_ingresos - total_gastos,
        "fecha_desde": fecha_desde,
        "fecha_hasta": fecha_hasta,
    }


# =====================================================
# BALANCE ECONÓMICO
# =====================================================

@login_required
def balance_economico(request):

    # Obtener los datos económicos permitidos para el usuario
    datos = obtener_datos_balance(
        request.user,
        request.GET,
    )

    # Construir el contexto que recibirá la plantilla
    contexto = {
        **datos,
        "fecha_desde": request.GET.get("desde", ""),
        "fecha_hasta": request.GET.get("hasta", ""),
        "puede_modificar": puede_modificar_economia(request.user),
    }

    return render(
        request,
        "economia/balance.html",
        contexto,
    )

# =====================================================
# FORMATO MONETARIO
# =====================================================

def formato_cop(valor):

    return (
        "$"
        + f"{valor:,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


# =====================================================
# EXPORTAR BALANCE A EXCEL
# =====================================================

@login_required
def exportar_balance_excel(request):

    datos = obtener_datos_balance(
        request.user,
        request.GET,
    )

    libro = Workbook()
    hoja = libro.active
    hoja.title = "Balance económico"

    hoja.merge_cells("A1:E1")

    hoja["A1"] = "CACAO GESTIÓN - BALANCE ECONÓMICO"

    hoja["A1"].font = Font(
        name="Arial",
        size=16,
        bold=True,
        color="FFFFFF",
    )

    hoja["A1"].fill = PatternFill(
        "solid",
        fgColor="1F6B50",
    )

    hoja["A1"].alignment = Alignment(
        horizontal="center"
    )

    hoja.merge_cells("A2:E2")

    hoja["A2"] = (
        f"Período: {datos['fecha_desde'] or 'Sin fecha inicial'} "
        f"hasta {datos['fecha_hasta'] or 'Sin fecha final'}"
    )

    hoja.merge_cells("A3:E3")

    hoja["A3"] = (
        "Generado: "
        + timezone.localtime().strftime("%d/%m/%Y %H:%M")
    )

    encabezados = [
        "Finca",
        "Productor",
        "Ingresos (COP)",
        "Gastos (COP)",
        "Balance (COP)",
    ]

    fila_encabezado = 5

    for columna, texto in enumerate(
        encabezados,
        start=1,
    ):

        celda = hoja.cell(
            row=fila_encabezado,
            column=columna,
            value=texto,
        )

        celda.font = Font(
            bold=True,
            color="FFFFFF",
        )

        celda.fill = PatternFill(
            "solid",
            fgColor="267653",
        )

        celda.alignment = Alignment(
            horizontal="center"
        )

    fila = 6

    for finca in datos["fincas"]:

        productor = (
            f"{finca.productor.nombres} "
            f"{finca.productor.apellidos}"
        )

        hoja.cell(fila, 1, finca.nombre)
        hoja.cell(fila, 2, productor)
        hoja.cell(fila, 3, finca.ingresos)
        hoja.cell(fila, 4, finca.gastos)
        hoja.cell(fila, 5, finca.balance)

        for columna in range(3, 6):
            hoja.cell(
                fila,
                columna,
            ).number_format = '"$" #,##0.00'

        fila += 1

    if not datos["fincas"]:
        hoja.cell(
            fila,
            1,
            "No hay fincas disponibles para este usuario.",
        )

    fila_total = fila + 1

    hoja.cell(fila_total, 1, "TOTAL GENERAL")
    hoja.cell(fila_total, 3, datos["total_ingresos"])
    hoja.cell(fila_total, 4, datos["total_gastos"])
    hoja.cell(fila_total, 5, datos["balance_general"])

    for columna in range(1, 6):

        celda = hoja.cell(
            fila_total,
            columna,
        )

        celda.font = Font(bold=True)

        celda.fill = PatternFill(
            "solid",
            fgColor="DCEDE4",
        )

    for columna in range(3, 6):
        hoja.cell(
            fila_total,
            columna,
        ).number_format = '"$" #,##0.00'

    anchos = {
        "A": 30,
        "B": 32,
        "C": 20,
        "D": 20,
        "E": 20,
    }

    for columna, ancho in anchos.items():
        hoja.column_dimensions[columna].width = ancho

    hoja.freeze_panes = "A6"

    hoja.auto_filter.ref = (
        f"A5:E{max(fila - 1, 5)}"
    )

    borde = Border(
        bottom=Side(
            style="thin",
            color="D9E2DC",
        )
    )

    for fila_celdas in hoja.iter_rows(
        min_row=5,
        max_row=fila_total,
        min_col=1,
        max_col=5,
    ):

        for celda in fila_celdas:
            celda.border = borde

    response = HttpResponse(
        content_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )

    response["Content-Disposition"] = (
        'attachment; filename="balance_economico.xlsx"'
    )

    libro.save(response)

    return response


# =====================================================
# EXPORTAR BALANCE A PDF
# =====================================================

@login_required
def exportar_balance_pdf(request):

    datos = obtener_datos_balance(
        request.user,
        request.GET,
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        'attachment; filename="balance_economico.pdf"'
    )

    documento = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    estilos = getSampleStyleSheet()

    contenido = []

    contenido.append(
        Paragraph(
            "CACAO GESTIÓN - BALANCE ECONÓMICO",
            estilos["Title"],
        )
    )

    contenido.append(
        Spacer(1, 8)
    )

    periodo = (
        f"Período: {datos['fecha_desde'] or 'Sin fecha inicial'} "
        f"hasta {datos['fecha_hasta'] or 'Sin fecha final'}"
    )

    contenido.append(
        Paragraph(
            escape(periodo),
            estilos["Normal"],
        )
    )

    generado = (
        "Generado: "
        + timezone.localtime().strftime("%d/%m/%Y %H:%M")
    )

    contenido.append(
        Paragraph(
            escape(generado),
            estilos["Normal"],
        )
    )

    contenido.append(
        Spacer(1, 12)
    )

    resumen = [
        [
            "INGRESOS GENERALES",
            "GASTOS GENERALES",
            "BALANCE GENERAL",
        ],
        [
            formato_cop(datos["total_ingresos"]),
            formato_cop(datos["total_gastos"]),
            formato_cop(datos["balance_general"]),
        ],
    ]

    tabla_resumen = Table(
        resumen,
        colWidths=[
            75 * mm,
            75 * mm,
            75 * mm,
        ],
    )

    tabla_resumen.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1F6B50"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "FONTNAME",
                (0, 1),
                (-1, 1),
                "Helvetica-Bold",
            ),
            (
                "ALIGN",
                (0, 0),
                (-1, -1),
                "CENTER",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.lightgrey,
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                8,
            ),
        ])
    )

    contenido.append(tabla_resumen)
    contenido.append(Spacer(1, 18))

    encabezados = [
        "Finca",
        "Productor",
        "Ingresos (COP)",
        "Gastos (COP)",
        "Balance (COP)",
    ]

    filas = [encabezados]

    for finca in datos["fincas"]:

        productor = (
            f"{finca.productor.nombres} "
            f"{finca.productor.apellidos}"
        )

        filas.append([
            Paragraph(
                escape(finca.nombre),
                estilos["BodyText"],
            ),
            Paragraph(
                escape(productor),
                estilos["BodyText"],
            ),
            formato_cop(finca.ingresos),
            formato_cop(finca.gastos),
            formato_cop(finca.balance),
        ])

    if not datos["fincas"]:
        filas.append([
            "No hay fincas disponibles para este usuario.",
            "",
            "",
            "",
            "",
        ])

    tabla = Table(
        filas,
        repeatRows=1,
        colWidths=[
            45 * mm,
            55 * mm,
            35 * mm,
            35 * mm,
            35 * mm,
        ],
    )

    tabla.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#267653"),
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.white,
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold",
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8,
            ),
            (
                "ALIGN",
                (2, 1),
                (-1, -1),
                "RIGHT",
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.lightgrey,
            ),
            (
                "ROWBACKGROUNDS",
                (0, 1),
                (-1, -1),
                [
                    colors.white,
                    colors.HexColor("#F1F6F3"),
                ],
            ),
            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
        ])
    )

    contenido.append(tabla)

    documento.build(contenido)

    return response
