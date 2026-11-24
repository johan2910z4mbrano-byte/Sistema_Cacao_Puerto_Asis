
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from .models import Cosecha, LoteProduccion, ProcesoPoscosecha

from .forms import (
    CosechaForm,
    LoteProduccionForm,
    ProcesoPoscosechaForm,
)

from cuentas.permisos import (
    es_administrador,
    es_productor,
    puede_editar_finca,
    cosechas_visibles,
    lotes_visibles,
    procesos_visibles,
)


def puede_modificar_produccion(usuario):
    return es_administrador(usuario) or es_productor(usuario)


def puede_editar_cosecha(usuario, cosecha):
    return (
        es_administrador(usuario)
        or (
            es_productor(usuario)
            and puede_editar_finca(
                usuario,
                cosecha.cultivo.finca,
            )
        )
    )


def puede_editar_lote(usuario, lote):
    return (
        es_administrador(usuario)
        or (
            es_productor(usuario)
            and puede_editar_finca(
                usuario,
                lote.cosecha.cultivo.finca,
            )
        )
    )


def puede_editar_proceso(usuario, proceso):
    return (
        es_administrador(usuario)
        or (
            es_productor(usuario)
            and puede_editar_finca(
                usuario,
                proceso.lote.cosecha.cultivo.finca,
            )
        )
    )


# =====================================================
# COSECHAS
# =====================================================

@login_required
def lista_cosechas(request):

    busqueda = request.GET.get("q", "").strip()

    cosechas = cosechas_visibles(
        request.user
    ).select_related(
        "cultivo",
        "cultivo__finca",
        "cultivo__finca__productor",
    )

    if busqueda:
        cosechas = cosechas.filter(
            Q(codigo__icontains=busqueda)
            | Q(cultivo__codigo__icontains=busqueda)
            | Q(cultivo__finca__nombre__icontains=busqueda)
            | Q(cultivo__finca__productor__nombres__icontains=busqueda)
            | Q(cultivo__finca__productor__apellidos__icontains=busqueda)
        )

    return render(
        request,
        "produccion/cosechas_lista.html",
        {
            "cosechas": cosechas,
            "busqueda": busqueda,
            "puede_modificar": puede_modificar_produccion(
                request.user
            ),
        }
    )


@login_required
def crear_cosecha(request):

    if not puede_modificar_produccion(request.user):
        raise PermissionDenied(
            "Tu perfil no tiene autorización para registrar cosechas."
        )

    if request.method == "POST":
        form = CosechaForm(
            request.POST,
            usuario=request.user,
        )

        if form.is_valid():
            cosecha = form.save()

            messages.success(
                request,
                f"La cosecha {cosecha.codigo} fue registrada correctamente."
            )

            return redirect("produccion:cosechas_lista")

    else:
        form = CosechaForm(usuario=request.user)

    return render(
        request,
        "produccion/cosecha_formulario.html",
        {
            "form": form,
            "titulo": "Registrar cosecha",
        }
    )


@login_required
def editar_cosecha(request, pk):

    cosecha = get_object_or_404(
        cosechas_visibles(request.user).select_related(
            "cultivo",
            "cultivo__finca",
        ),
        pk=pk,
    )

    if not puede_editar_cosecha(request.user, cosecha):
        raise PermissionDenied(
            "No tienes autorización para modificar esta cosecha."
        )

    if request.method == "POST":
        form = CosechaForm(
            request.POST,
            instance=cosecha,
            usuario=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "La información de la cosecha fue actualizada."
            )

            return redirect("produccion:cosechas_lista")

    else:
        form = CosechaForm(
            instance=cosecha,
            usuario=request.user,
        )

    return render(
        request,
        "produccion/cosecha_formulario.html",
        {
            "form": form,
            "titulo": "Editar cosecha",
        }
    )


# =====================================================
# LOTES DE PRODUCCIÓN
# =====================================================

@login_required
def lista_lotes(request):

    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "todos")

    lotes = lotes_visibles(
        request.user
    ).select_related(
        "cosecha",
        "cosecha__cultivo",
        "cosecha__cultivo__finca",
        "cosecha__cultivo__finca__productor",
    )

    if estado != "todos":
        lotes = lotes.filter(estado=estado)

    if busqueda:
        lotes = lotes.filter(
            Q(codigo__icontains=busqueda)
            | Q(cosecha__codigo__icontains=busqueda)
            | Q(cosecha__cultivo__codigo__icontains=busqueda)
            | Q(cosecha__cultivo__finca__nombre__icontains=busqueda)
        )

    return render(
        request,
        "produccion/lotes_lista.html",
        {
            "lotes": lotes,
            "busqueda": busqueda,
            "estado": estado,
            "estados": LoteProduccion.EstadoLote.choices,
            "puede_modificar": puede_modificar_produccion(
                request.user
            ),
        }
    )


@login_required
def crear_lote(request):

    if not puede_modificar_produccion(request.user):
        raise PermissionDenied(
            "Tu perfil no tiene autorización para registrar lotes."
        )

    if request.method == "POST":
        form = LoteProduccionForm(
            request.POST,
            usuario=request.user,
        )

        if form.is_valid():
            lote = form.save()

            messages.success(
                request,
                f"El lote {lote.codigo} fue registrado correctamente."
            )

            return redirect("produccion:lotes_lista")

    else:
        form = LoteProduccionForm(usuario=request.user)

    return render(
        request,
        "produccion/lote_formulario.html",
        {
            "form": form,
            "titulo": "Registrar lote de producción",
        }
    )


@login_required
def editar_lote(request, pk):

    lote = get_object_or_404(
        lotes_visibles(request.user).select_related(
            "cosecha",
            "cosecha__cultivo",
            "cosecha__cultivo__finca",
        ),
        pk=pk,
    )

    if not puede_editar_lote(request.user, lote):
        raise PermissionDenied(
            "No tienes autorización para modificar este lote."
        )

    if request.method == "POST":
        form = LoteProduccionForm(
            request.POST,
            instance=lote,
            usuario=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "La información del lote fue actualizada."
            )

            return redirect("produccion:lotes_lista")

    else:
        form = LoteProduccionForm(
            instance=lote,
            usuario=request.user,
        )

    return render(
        request,
        "produccion/lote_formulario.html",
        {
            "form": form,
            "titulo": "Editar lote de producción",
        }
    )


# =====================================================
# POSCOSECHA
# =====================================================

@login_required
def lista_procesos(request):

    busqueda = request.GET.get("q", "").strip()
    etapa = request.GET.get("etapa", "todas")

    procesos = procesos_visibles(
        request.user
    ).select_related(
        "lote",
        "lote__cosecha",
        "lote__cosecha__cultivo",
        "lote__cosecha__cultivo__finca",
    )

    if etapa != "todas":
        procesos = procesos.filter(etapa=etapa)

    if busqueda:
        procesos = procesos.filter(
            Q(lote__codigo__icontains=busqueda)
            | Q(lote__cosecha__codigo__icontains=busqueda)
            | Q(responsable__icontains=busqueda)
            | Q(observaciones__icontains=busqueda)
        )

    return render(
        request,
        "produccion/procesos_lista.html",
        {
            "procesos": procesos,
            "busqueda": busqueda,
            "etapa": etapa,
            "etapas": ProcesoPoscosecha.Etapa.choices,
            "puede_modificar": puede_modificar_produccion(
                request.user
            ),
        }
    )


@login_required
def crear_proceso(request):

    if not puede_modificar_produccion(request.user):
        raise PermissionDenied(
            "Tu perfil no tiene autorización para registrar procesos."
        )

    if request.method == "POST":
        form = ProcesoPoscosechaForm(
            request.POST,
            usuario=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "El proceso de poscosecha fue registrado correctamente."
            )

            return redirect("produccion:procesos_lista")

    else:
        form = ProcesoPoscosechaForm(usuario=request.user)

    return render(
        request,
        "produccion/proceso_formulario.html",
        {
            "form": form,
            "titulo": "Registrar proceso de poscosecha",
        }
    )


@login_required
def editar_proceso(request, pk):

    proceso = get_object_or_404(
        procesos_visibles(request.user).select_related(
            "lote",
            "lote__cosecha",
            "lote__cosecha__cultivo",
            "lote__cosecha__cultivo__finca",
        ),
        pk=pk,
    )

    if not puede_editar_proceso(request.user, proceso):
        raise PermissionDenied(
            "No tienes autorización para modificar este proceso."
        )

    if request.method == "POST":
        form = ProcesoPoscosechaForm(
            request.POST,
            instance=proceso,
            usuario=request.user,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "El proceso de poscosecha fue actualizado."
            )

            return redirect("produccion:procesos_lista")

    else:
        form = ProcesoPoscosechaForm(
            instance=proceso,
            usuario=request.user,
        )

    return render(
        request,
        "produccion/proceso_formulario.html",
        {
            "form": form,
            "titulo": "Editar proceso de poscosecha",
        }
    )
