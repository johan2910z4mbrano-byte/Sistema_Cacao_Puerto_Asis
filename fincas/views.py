import math
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Finca, DelimitacionFinca
from .forms import FincaForm

from cuentas.permisos import (
    es_administrador,
    es_productor,
    obtener_perfil,
    fincas_visibles,
    puede_editar_finca,
)


# =====================================================
# GUARDAR FINCA Y DELIMITACIÓN
# =====================================================

def guardar_finca_con_delimitacion(form, productor_forzado=None):

    with transaction.atomic():

        finca = form.save(commit=False)

        # Impedir que un productor asigne la finca a otra persona.
        if productor_forzado is not None:
            finca.productor = productor_forzado

        geojson = form.cleaned_data.get("geojson")
        delimitacion = None

        if geojson:

            delimitacion = DelimitacionFinca(
                finca=finca,
                geojson=geojson,
                precision_metros=form.cleaned_data.get(
                    "precision_metros"
                ),
                observaciones=(
                    "Delimitación capturada desde el mapa "
                    "de Cacao Gestión."
                ),
            )

            delimitacion.full_clean(exclude=["finca"])

            anillo = geojson["coordinates"][0]
            radio_tierra = 6378137.0

            suma = 0.0

            for i in range(len(anillo) - 1):

                lon1, lat1 = anillo[i]
                lon2, lat2 = anillo[i + 1]

                suma += (
                    math.radians(lon2 - lon1)
                    * (
                        2
                        + math.sin(math.radians(lat1))
                        + math.sin(math.radians(lat2))
                    )
                )

            area_metros = abs(suma) * radio_tierra ** 2 / 2

            area_hectareas = Decimal(
                str(area_metros / 10000)
            ).quantize(Decimal("0.0001"))

            if area_hectareas <= 0:
                raise ValidationError(
                    "El área del polígono debe ser mayor que cero."
                )

            finca.area_hectareas = area_hectareas

            longitudes = [float(p[0]) for p in anillo[:-1]]
            latitudes = [float(p[1]) for p in anillo[:-1]]

            finca.longitud = Decimal(
                str((min(longitudes) + max(longitudes)) / 2)
            ).quantize(Decimal("0.0000001"))

            finca.latitud = Decimal(
                str((min(latitudes) + max(latitudes)) / 2)
            ).quantize(Decimal("0.0000001"))

        finca.save()

        if delimitacion:
            delimitacion.finca = finca
            delimitacion.save()

    return finca


# =====================================================
# LISTADO DE FINCAS
# =====================================================

@login_required
def lista_fincas(request):

    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "activas")

    fincas = fincas_visibles(
        request.user
    ).select_related("productor")

    if estado == "activas":
        fincas = fincas.filter(activa=True)

    elif estado == "inactivas":
        fincas = fincas.filter(activa=False)

    if busqueda:
        fincas = fincas.filter(
            Q(codigo__icontains=busqueda)
            | Q(nombre__icontains=busqueda)
            | Q(vereda__icontains=busqueda)
            | Q(productor__nombres__icontains=busqueda)
            | Q(productor__apellidos__icontains=busqueda)
        )

    return render(
        request,
        "fincas/lista.html",
        {
            "fincas": fincas,
            "busqueda": busqueda,
            "estado": estado,
            "puede_crear": (
                es_administrador(request.user)
                or es_productor(request.user)
            ),
        },
    )


# =====================================================
# CREAR FINCA
# =====================================================

@login_required
def crear_finca(request):

    administrador = es_administrador(request.user)

    productor_forzado = None

    if not administrador:

        perfil = obtener_perfil(request.user)

        if not es_productor(request.user):
            raise PermissionDenied(
                "Los representantes de asociaciones no pueden "
                "registrar fincas en nombre de sus asociados."
            )

        productor_forzado = perfil.productor

    if request.method == "POST":
        form = FincaForm(
            request.POST,
            usuario=request.user,
        )

        if form.is_valid():

            try:
                finca = guardar_finca_con_delimitacion(
                    form,
                    productor_forzado=productor_forzado,
                )

            except ValidationError as error:
                form.add_error(None, error)

            else:
                messages.success(
                    request,
                    f"La finca {finca.nombre} "
                    "fue registrada correctamente.",
                )

                return redirect("fincas:lista")

    else:
        form = FincaForm(usuario=request.user)

    return render(
        request,
        "fincas/formulario.html",
        {
            "form": form,
            "titulo": "Registrar finca",
        },
    )


# =====================================================
# EDITAR FINCA
# =====================================================

@login_required
def editar_finca(request, pk):

    finca = get_object_or_404(
        fincas_visibles(request.user),
        pk=pk,
    )

    if not puede_editar_finca(request.user, finca):
        raise PermissionDenied(
            "No tienes autorización para modificar esta finca."
        )

    perfil = obtener_perfil(request.user)

    productor_forzado = (
        perfil.productor
        if es_productor(request.user)
        else None
    )

    delimitacion_actual = (
        finca.delimitaciones
        .order_by("-fecha_registro")
        .first()
    )

    datos_iniciales = {}

    if delimitacion_actual:
        datos_iniciales["geojson"] = delimitacion_actual.geojson
        datos_iniciales["precision_metros"] = (
            delimitacion_actual.precision_metros
        )

    if request.method == "POST":

        form = FincaForm(
            request.POST,
            instance=finca,
            usuario=request.user,
        )

        if form.is_valid():

            try:
                finca = guardar_finca_con_delimitacion(
                    form,
                    productor_forzado=productor_forzado,
                )

            except ValidationError as error:
                form.add_error(None, error)

            else:
                messages.success(
                    request,
                    "La información de la finca "
                    "fue actualizada correctamente.",
                )

                return redirect("fincas:lista")

    else:
        form = FincaForm(
            instance=finca,
            initial=datos_iniciales,
            usuario=request.user,
        )

    return render(
        request,
        "fincas/formulario.html",
        {
            "form": form,
            "titulo": "Editar finca",
        },
    )


# =====================================================
# CAMBIAR ESTADO DE FINCA
# =====================================================

@login_required
@require_POST
def cambiar_estado_finca(request, pk):

    finca = get_object_or_404(
        fincas_visibles(request.user),
        pk=pk,
    )

    if not puede_editar_finca(request.user, finca):
        raise PermissionDenied(
            "No tienes autorización para cambiar el estado de esta finca."
        )

    finca.activa = not finca.activa

    finca.save(
        update_fields=["activa", "fecha_actualizacion"]
    )

    messages.success(
        request,
        f"El estado de la finca {finca.nombre} "
        "fue actualizado correctamente.",
    )

    return redirect("fincas:lista")