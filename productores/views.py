from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Productor
from .forms import ProductorForm

from asociaciones.models import Asociacion
from cultivos.models import Cultivo
from produccion.models import (
    Cosecha,
    LoteProduccion,
    ProcesoPoscosecha,
)
from economia.models import MovimientoEconomico

from cuentas.permisos import (
    es_administrador,
    es_productor,
    es_representante_asociacion,
    obtener_perfil,
    asociaciones_del_usuario,
    productores_autorizados,
    fincas_visibles,
    cultivos_visibles,
    cosechas_visibles,
    lotes_visibles,
    procesos_visibles,
    movimientos_visibles,
)


def exigir_administrador(usuario):
    """
    Restringe las operaciones administrativas
    de productores a usuarios administradores.
    """
    if not es_administrador(usuario):
        raise PermissionDenied(
            "No tienes autorización para realizar esta operación."
        )


@login_required
def dashboard(request):

    usuario = request.user

    # ==========================================
    # IDENTIFICAR ROL Y ALCANCE DE INFORMACIÓN
    # ==========================================

    administrador = es_administrador(usuario)
    productor = es_productor(usuario)
    representante = es_representante_asociacion(usuario)

    if administrador:
        productores = Productor.objects.all()
        asociaciones = Asociacion.objects.all()

    elif productor:
        perfil = obtener_perfil(usuario)

        if not perfil or not perfil.productor_id:
            raise PermissionDenied(
                "La cuenta no tiene un productor asociado."
            )

        productores = Productor.objects.filter(
            pk=perfil.productor_id
        )

        asociaciones = Asociacion.objects.none()

    elif representante:
        productores = productores_autorizados(usuario)
        asociaciones = asociaciones_del_usuario(usuario)

    else:
        raise PermissionDenied(
            "Tu cuenta no tiene un perfil autorizado para acceder al panel."
        )

    # Consultas limitadas según los permisos del usuario.
    fincas = fincas_visibles(usuario)
    cultivos = cultivos_visibles(usuario)
    cosechas = cosechas_visibles(usuario)
    lotes = lotes_visibles(usuario)
    procesos = procesos_visibles(usuario)
    movimientos = movimientos_visibles(usuario)

    # ==========================================
    # PRODUCTORES AUTORIZADOS
    # ==========================================

    total = productores.count()
    activos = productores.filter(activo=True).count()
    inactivos = productores.filter(activo=False).count()

    recientes = productores.order_by(
        "-fecha_registro"
    )[:5]

    # ==========================================
    # ASOCIACIONES AUTORIZADAS
    # ==========================================

    total_asociaciones = asociaciones.count()

    asociaciones_activas = asociaciones.filter(
        activo=True
    ).count()

    # ==========================================
    # FINCAS VISIBLES
    # ==========================================

    total_fincas = fincas.count()

    fincas_activas = fincas.filter(
        activa=True
    ).count()

    # ==========================================
    # CULTIVOS VISIBLES
    # ==========================================

    total_cultivos = cultivos.count()

    cultivos_activos = cultivos.exclude(
        estado=Cultivo.EstadoCultivo.INACTIVO
    ).count()

    # ==========================================
    # COSECHAS Y PRODUCCIÓN
    # ==========================================

    total_cosechas = cosechas.count()

    produccion_total = cosechas.aggregate(
        total=Sum("cantidad_kg")
    )["total"] or Decimal("0.000")

    cosechas_recientes = (
        cosechas.select_related(
            "cultivo",
            "cultivo__finca",
        ).order_by("-fecha_cosecha")[:5]
    )

    produccion_por_tipo = list(
        cosechas.values(
            "cultivo__tipo_cultivo"
        ).annotate(
            total_kg=Sum("cantidad_kg")
        ).order_by("-total_kg")
    )

    etiquetas_tipos = dict(Cultivo.TipoCultivo.choices)

    maximo_produccion = max(
        (
            item["total_kg"] or Decimal("0")
            for item in produccion_por_tipo
        ),
        default=Decimal("0"),
    )

    for item in produccion_por_tipo:

        tipo = item["cultivo__tipo_cultivo"]

        item["nombre"] = etiquetas_tipos.get(
            tipo,
            tipo,
        )

        item["porcentaje"] = (
            float(item["total_kg"] / maximo_produccion * 100)
            if maximo_produccion > 0
            else 0
        )

    # ==========================================
    # LOTES Y POSCOSECHA
    # ==========================================

    total_lotes = lotes.count()

    lotes_en_proceso = lotes.filter(
        estado__in=["fermentacion", "secado"]
    ).count()

    procesos_en_curso = procesos.filter(
        fecha_fin__isnull=True
    ).count()

    # ==========================================
    # INFORMACIÓN ECONÓMICA AUTORIZADA
    # ==========================================

    puede_ver_economia = administrador or productor

    resumen_economico = movimientos.aggregate(
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

    ingresos = resumen_economico["ingresos"] or Decimal("0.00")
    gastos = resumen_economico["gastos"] or Decimal("0.00")

    balance = ingresos - gastos

    movimientos_recientes = (
        movimientos.select_related(
            "finca",
            "finca__productor",
        ).order_by("-fecha", "-fecha_registro")[:5]
    )

    # ==========================================
    # CONTEXTO DEL PANEL
    # ==========================================

    contexto = {
        "total": total,
        "activos": activos,
        "inactivos": inactivos,
        "recientes": recientes,

        "total_asociaciones": total_asociaciones,
        "asociaciones_activas": asociaciones_activas,

        "total_fincas": total_fincas,
        "fincas_activas": fincas_activas,

        "total_cultivos": total_cultivos,
        "cultivos_activos": cultivos_activos,

        "total_cosechas": total_cosechas,
        "produccion_total": produccion_total,
        "cosechas_recientes": cosechas_recientes,
        "produccion_por_tipo": produccion_por_tipo,

        "total_lotes": total_lotes,
        "lotes_en_proceso": lotes_en_proceso,
        "procesos_en_curso": procesos_en_curso,

        "ingresos": ingresos,
        "gastos": gastos,
        "balance": balance,
        "movimientos_recientes": movimientos_recientes,

        "puede_ver_economia": puede_ver_economia,
        "puede_modificar_productores": administrador,
        "es_representante": representante,
        "es_productor": productor,
    }

    return render(
        request,
        "productores/dashboard.html",
        contexto,
    )


@login_required
def lista_productores(request):

    usuario = request.user

    if es_administrador(usuario):
        productores = Productor.objects.all()

    elif es_representante_asociacion(usuario):
        productores = productores_autorizados(usuario)

    elif es_productor(usuario):
        perfil = obtener_perfil(usuario)

        if not perfil or not perfil.productor_id:
            raise PermissionDenied(
                "La cuenta no tiene un productor asociado."
            )

        productores = Productor.objects.filter(
            pk=perfil.productor_id
        )

    else:
        raise PermissionDenied(
            "No tienes autorización para consultar productores."
        )

    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "activos")

    if estado == "activos":
        productores = productores.filter(activo=True)

    elif estado == "inactivos":
        productores = productores.filter(activo=False)

    if busqueda:
        productores = productores.filter(
            Q(codigo__icontains=busqueda)
            | Q(nombres__icontains=busqueda)
            | Q(apellidos__icontains=busqueda)
            | Q(vereda__icontains=busqueda)
        )

    contexto = {
        "productores": productores,
        "busqueda": busqueda,
        "estado": estado,
        "puede_modificar": es_administrador(usuario),
    }

    return render(
        request,
        "productores/lista.html",
        contexto,
    )


@login_required
def crear_productor(request):

    exigir_administrador(request.user)

    if request.method == "POST":
        form = ProductorForm(request.POST)

        if form.is_valid():
            productor = form.save()

            messages.success(
                request,
                f"Productor {productor.codigo} registrado correctamente."
            )

            return redirect("productores:lista")

    else:
        form = ProductorForm()

    return render(
        request,
        "productores/formulario.html",
        {
            "form": form,
            "titulo": "Registrar productor",
        }
    )


@login_required
def editar_productor(request, pk):

    exigir_administrador(request.user)

    productor = get_object_or_404(
        Productor,
        pk=pk,
    )

    if request.method == "POST":
        form = ProductorForm(
            request.POST,
            instance=productor,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Información del productor actualizada correctamente."
            )

            return redirect("productores:lista")

    else:
        form = ProductorForm(instance=productor)

    return render(
        request,
        "productores/formulario.html",
        {
            "form": form,
            "titulo": "Editar productor",
        }
    )


@login_required
@require_POST
def cambiar_estado(request, pk):

    exigir_administrador(request.user)

    productor = get_object_or_404(
        Productor,
        pk=pk,
    )

    productor.activo = not productor.activo

    productor.save(
        update_fields=[
            "activo",
            "fecha_actualizacion",
        ]
    )

    messages.success(
        request,
        f"Estado del productor {productor.codigo} actualizado."
    )

    return redirect("productores:lista")