from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Cultivo, ActividadAgricola
from .forms import CultivoForm, ActividadAgricolaForm

from cuentas.permisos import (
    es_administrador,
    es_productor,
    cultivos_visibles,
    actividades_visibles,
    puede_editar_finca,
    puede_editar_cultivo,
)


# =====================================================
# PERMISOS DE MODIFICACIÓN
# =====================================================

def puede_modificar_registros(usuario):
    return es_administrador(usuario) or es_productor(usuario)


# =====================================================
# LISTADO DE CULTIVOS
# =====================================================

@login_required
def lista_cultivos(request):

    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "todos")
    tipo = request.GET.get("tipo", "todos")

    cultivos = cultivos_visibles(
        request.user
    ).select_related(
        "finca",
        "finca__productor",
    )

    if estado != "todos":
        cultivos = cultivos.filter(estado=estado)

    if tipo != "todos":
        cultivos = cultivos.filter(tipo_cultivo=tipo)

    if busqueda:
        cultivos = cultivos.filter(
            Q(codigo__icontains=busqueda)
            | Q(variedad__icontains=busqueda)
            | Q(finca__nombre__icontains=busqueda)
            | Q(finca__productor__nombres__icontains=busqueda)
            | Q(finca__productor__apellidos__icontains=busqueda)
        )

    return render(
        request,
        "cultivos/lista.html",
        {
            "cultivos": cultivos,
            "busqueda": busqueda,
            "estado": estado,
            "tipo": tipo,
            "estados": Cultivo.EstadoCultivo.choices,
            "tipos": Cultivo.TipoCultivo.choices,
            "puede_modificar": puede_modificar_registros(
                request.user
            ),
        }
    )


# =====================================================
# CREAR CULTIVO
# =====================================================

@login_required
def crear_cultivo(request):

    if not puede_modificar_registros(request.user):
        raise PermissionDenied(
            "Tu perfil no tiene autorización para registrar cultivos."
        )

    if request.method == "POST":

        form = CultivoForm(
            request.POST,
            usuario=request.user,
        )

        if form.is_valid():

            cultivo = form.save()

            messages.success(
                request,
                f"El cultivo {cultivo.codigo} "
                "fue registrado correctamente."
            )

            return redirect("cultivos:lista")

    else:
        form = CultivoForm(usuario=request.user)

    return render(
        request,
        "cultivos/formulario.html",
        {
            "form": form,
            "titulo": "Registrar cultivo",
        }
    )


# =====================================================
# EDITAR CULTIVO
# =====================================================

@login_required
def editar_cultivo(request, pk):

    cultivo = get_object_or_404(
        cultivos_visibles(request.user).select_related("finca"),
        pk=pk,
    )

    if not puede_editar_cultivo(request.user, cultivo):
        raise PermissionDenied(
            "No tienes autorización para modificar este cultivo."
        )

    if request.method == "POST":

        form = CultivoForm(
            request.POST,
            instance=cultivo,
            usuario=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La información del cultivo "
                "fue actualizada correctamente."
            )

            return redirect("cultivos:lista")

    else:
        form = CultivoForm(
            instance=cultivo,
            usuario=request.user,
        )

    return render(
        request,
        "cultivos/formulario.html",
        {
            "form": form,
            "titulo": "Editar cultivo",
        }
    )


# =====================================================
# LISTADO DE ACTIVIDADES AGRÍCOLAS
# =====================================================

@login_required
def lista_actividades(request):

    busqueda = request.GET.get("q", "").strip()
    tipo = request.GET.get("tipo", "todos")

    actividades = actividades_visibles(
        request.user
    ).select_related(
        "cultivo",
        "cultivo__finca",
        "cultivo__finca__productor",
    )

    if tipo != "todos":
        actividades = actividades.filter(
            tipo_actividad=tipo
        )

    if busqueda:
        actividades = actividades.filter(
            Q(cultivo__codigo__icontains=busqueda)
            | Q(cultivo__finca__nombre__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
            | Q(responsable__icontains=busqueda)
        )

    return render(
        request,
        "cultivos/actividades_lista.html",
        {
            "actividades": actividades,
            "busqueda": busqueda,
            "tipo": tipo,
            "tipos": ActividadAgricola.TipoActividad.choices,
            "puede_modificar": puede_modificar_registros(
                request.user
            ),
        }
    )


# =====================================================
# CREAR ACTIVIDAD AGRÍCOLA
# =====================================================

@login_required
def crear_actividad(request):

    if not puede_modificar_registros(request.user):
        raise PermissionDenied(
            "Tu perfil no tiene autorización para registrar actividades."
        )

    if request.method == "POST":

        form = ActividadAgricolaForm(
            request.POST,
            usuario=request.user,
        )

        if form.is_valid():

            actividad = form.save()

            messages.success(
                request,
                "La actividad agrícola fue registrada correctamente."
            )

            return redirect("cultivos:actividades_lista")

    else:
        form = ActividadAgricolaForm(usuario=request.user)

    return render(
        request,
        "cultivos/actividad_formulario.html",
        {
            "form": form,
            "titulo": "Registrar actividad agrícola",
        }
    )


# =====================================================
# EDITAR ACTIVIDAD AGRÍCOLA
# =====================================================

@login_required
def editar_actividad(request, pk):

    actividad = get_object_or_404(
        actividades_visibles(request.user).select_related(
            "cultivo",
            "cultivo__finca",
        ),
        pk=pk,
    )

    if not (
        es_administrador(request.user)
        or (
            es_productor(request.user)
            and puede_editar_finca(
                request.user,
                actividad.cultivo.finca,
            )
        )
    ):
        raise PermissionDenied(
            "No tienes autorización para modificar esta actividad."
        )

    if request.method == "POST":

        form = ActividadAgricolaForm(
            request.POST,
            instance=actividad,
            usuario=request.user,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "La actividad agrícola fue actualizada correctamente."
            )

            return redirect("cultivos:actividades_lista")

    else:
        form = ActividadAgricolaForm(
            instance=actividad,
            usuario=request.user,
        )

    return render(
        request,
        "cultivos/actividad_formulario.html",
        {
            "form": form,
            "titulo": "Editar actividad agrícola",
        }
    )