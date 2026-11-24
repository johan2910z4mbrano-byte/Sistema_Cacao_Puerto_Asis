
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from productores.models import Productor
from asociaciones.models import (
    Asociacion,
    Membresia,
    ResponsableAsociacion,
)
from fincas.models import Finca
from cultivos.models import Cultivo, ActividadAgricola
from produccion.models import (
    Cosecha,
    LoteProduccion,
    ProcesoPoscosecha,
)
from economia.models import MovimientoEconomico


# =====================================================
# IDENTIFICACIÓN DEL USUARIO
# =====================================================

def es_administrador(usuario):
    return (
        usuario.is_authenticated
        and (usuario.is_superuser or usuario.is_staff)
    )


def obtener_perfil(usuario):

    if not usuario.is_authenticated:
        return None

    try:
        return usuario.perfil
    except ObjectDoesNotExist:
        return None


def es_productor(usuario):

    perfil = obtener_perfil(usuario)

    return (
        perfil is not None
        and perfil.tipo_usuario == "productor"
        and perfil.productor_id is not None
    )


def es_representante_asociacion(usuario):

    perfil = obtener_perfil(usuario)

    return (
        perfil is not None
        and perfil.tipo_usuario == "asociacion"
        and ResponsableAsociacion.objects.filter(
            perfil=perfil,
            activo=True,
            asociacion__activo=True,
        ).exists()
    )


# =====================================================
# ASOCIACIONES Y AUTORIZACIONES
# =====================================================

def asociaciones_del_usuario(usuario):

    perfil = obtener_perfil(usuario)

    if perfil is None:
        return Asociacion.objects.none()

    return Asociacion.objects.filter(
        responsables__perfil=perfil,
        responsables__activo=True,
        activo=True,
    ).distinct()


def productores_autorizados(usuario):

    if es_administrador(usuario):
        return Productor.objects.all()

    asociaciones = asociaciones_del_usuario(usuario)

    return Productor.objects.filter(
        membresias__asociacion__in=asociaciones,
        membresias__estado=Membresia.Estado.ACTIVA,
        membresias__autorizacion_compartir=True,
    ).distinct()


# =====================================================
# FINCAS VISIBLES
# =====================================================

def fincas_visibles(usuario):

    if es_administrador(usuario):
        return Finca.objects.all()

    perfil = obtener_perfil(usuario)

    if perfil is None:
        return Finca.objects.none()

    if es_productor(usuario):
        return Finca.objects.filter(
            productor_id=perfil.productor_id
        )

    if es_representante_asociacion(usuario):
        return Finca.objects.filter(
            productor__in=productores_autorizados(usuario)
        )

    return Finca.objects.none()


# =====================================================
# FINCAS CON INFORMACIÓN ECONÓMICA VISIBLE
# =====================================================

def fincas_economicas_visibles(usuario):

    if es_administrador(usuario):
        return Finca.objects.all()

    perfil = obtener_perfil(usuario)

    if perfil is None:
        return Finca.objects.none()

    if es_productor(usuario):
        return Finca.objects.filter(
            productor_id=perfil.productor_id
        )

    # Las asociaciones no reciben información financiera
    # hasta disponer de consentimiento económico específico.
    return Finca.objects.none()


# =====================================================
# CULTIVOS Y ACTIVIDADES
# =====================================================

def cultivos_visibles(usuario):

    return Cultivo.objects.filter(
        finca__in=fincas_visibles(usuario)
    )


def actividades_visibles(usuario):

    return ActividadAgricola.objects.filter(
        cultivo__finca__in=fincas_visibles(usuario)
    )


# =====================================================
# COSECHAS, LOTES Y POSCOSECHA
# =====================================================

def cosechas_visibles(usuario):

    return Cosecha.objects.filter(
        cultivo__finca__in=fincas_visibles(usuario)
    )


def lotes_visibles(usuario):

    return LoteProduccion.objects.filter(
        cosecha__cultivo__finca__in=fincas_visibles(usuario)
    )


def procesos_visibles(usuario):

    return ProcesoPoscosecha.objects.filter(
        lote__cosecha__cultivo__finca__in=fincas_visibles(usuario)
    )


# =====================================================
# MOVIMIENTOS ECONÓMICOS
# =====================================================

def movimientos_visibles(usuario):

    return MovimientoEconomico.objects.filter(
        finca__in=fincas_economicas_visibles(usuario)
    )


# =====================================================
# PERMISOS DE EDICIÓN
# =====================================================

def puede_editar_finca(usuario, finca):

    if es_administrador(usuario):
        return True

    perfil = obtener_perfil(usuario)

    return (
        perfil is not None
        and es_productor(usuario)
        and finca.productor_id == perfil.productor_id
    )


def puede_editar_cultivo(usuario, cultivo):

    return (
        es_administrador(usuario)
        or (
            es_productor(usuario)
            and puede_editar_finca(usuario, cultivo.finca)
        )
    )


def puede_editar_movimiento(usuario, movimiento):

    return (
        es_administrador(usuario)
        or (
            es_productor(usuario)
            and puede_editar_finca(usuario, movimiento.finca)
        )
    )


# =====================================================
# VALIDACIÓN GENERAL DE PERFIL
# =====================================================

def requiere_perfil(view_func):

    @login_required
    @wraps(view_func)
    def vista_protegida(request, *args, **kwargs):

        if (
            not es_administrador(request.user)
            and obtener_perfil(request.user) is None
        ):
            raise PermissionDenied(
                "La cuenta no tiene un perfil de acceso configurado."
            )

        return view_func(request, *args, **kwargs)

    return vista_protegida
