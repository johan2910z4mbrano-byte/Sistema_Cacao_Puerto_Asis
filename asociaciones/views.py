
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Asociacion, Membresia
from .forms import AsociacionForm, MembresiaForm


# =====================================================
# GESTIÓN DE ASOCIACIONES
# =====================================================

@staff_member_required
def lista_asociaciones(request):

    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "activas")

    asociaciones = Asociacion.objects.all()

    if estado == "activas":
        asociaciones = asociaciones.filter(activo=True)
    elif estado == "inactivas":
        asociaciones = asociaciones.filter(activo=False)

    if busqueda:
        asociaciones = asociaciones.filter(
            Q(nombre__icontains=busqueda)
            | Q(sigla__icontains=busqueda)
            | Q(municipio__icontains=busqueda)
            | Q(vereda__icontains=busqueda)
        )

    contexto = {
        "asociaciones": asociaciones,
        "busqueda": busqueda,
        "estado": estado,
    }

    return render(
        request,
        "asociaciones/lista.html",
        contexto
    )


@staff_member_required
def crear_asociacion(request):

    if request.method == "POST":
        form = AsociacionForm(request.POST)

        if form.is_valid():
            asociacion = form.save()

            messages.success(
                request,
                f"La asociación {asociacion.nombre} "
                "fue registrada correctamente."
            )

            return redirect("asociaciones:lista")

    else:
        form = AsociacionForm()

    return render(
        request,
        "asociaciones/formulario.html",
        {
            "form": form,
            "titulo": "Registrar asociación",
        }
    )


@staff_member_required
def editar_asociacion(request, pk):

    asociacion = get_object_or_404(
        Asociacion,
        pk=pk
    )

    if request.method == "POST":
        form = AsociacionForm(
            request.POST,
            instance=asociacion
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "La información de la asociación "
                "fue actualizada correctamente."
            )

            return redirect("asociaciones:lista")

    else:
        form = AsociacionForm(instance=asociacion)

    return render(
        request,
        "asociaciones/formulario.html",
        {
            "form": form,
            "titulo": "Editar asociación",
        }
    )


@staff_member_required
@require_POST
def cambiar_estado(request, pk):

    asociacion = get_object_or_404(
        Asociacion,
        pk=pk
    )

    asociacion.activo = not asociacion.activo

    asociacion.save(
        update_fields=["activo", "fecha_actualizacion"]
    )

    messages.success(
        request,
        f"El estado de {asociacion.nombre} "
        "fue actualizado correctamente."
    )

    return redirect("asociaciones:lista")


# =====================================================
# GESTIÓN DE MEMBRESÍAS
# =====================================================

@staff_member_required
def lista_membresias(request):

    busqueda = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "todas")
    autorizacion = request.GET.get("autorizacion", "todas")

    membresias = Membresia.objects.select_related(
        "productor",
        "asociacion"
    ).all()

    if estado != "todas":
        membresias = membresias.filter(estado=estado)

    if autorizacion == "si":
        membresias = membresias.filter(
            autorizacion_compartir=True
        )
    elif autorizacion == "no":
        membresias = membresias.filter(
            autorizacion_compartir=False
        )

    if busqueda:
        membresias = membresias.filter(
            Q(productor__codigo__icontains=busqueda)
            | Q(productor__nombres__icontains=busqueda)
            | Q(productor__apellidos__icontains=busqueda)
            | Q(asociacion__nombre__icontains=busqueda)
        )

    return render(
        request,
        "asociaciones/membresias_lista.html",
        {
            "membresias": membresias,
            "busqueda": busqueda,
            "estado": estado,
            "autorizacion": autorizacion,
        }
    )


@staff_member_required
def crear_membresia(request):

    if request.method == "POST":
        form = MembresiaForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "La membresía fue registrada correctamente."
            )

            return redirect("asociaciones:membresias_lista")

    else:
        form = MembresiaForm()

    return render(
        request,
        "asociaciones/membresia_formulario.html",
        {
            "form": form,
            "titulo": "Registrar membresía",
        }
    )


@staff_member_required
def editar_membresia(request, pk):

    membresia = get_object_or_404(
        Membresia,
        pk=pk
    )

    if request.method == "POST":
        form = MembresiaForm(
            request.POST,
            instance=membresia
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "La membresía fue actualizada correctamente."
            )

            return redirect("asociaciones:membresias_lista")

    else:
        form = MembresiaForm(instance=membresia)

    return render(
        request,
        "asociaciones/membresia_formulario.html",
        {
            "form": form,
            "titulo": "Editar membresía",
        }
    )


@staff_member_required
@require_POST
def cambiar_estado_membresia(request, pk):

    membresia = get_object_or_404(
        Membresia,
        pk=pk
    )

    if membresia.estado == Membresia.Estado.PENDIENTE:

        messages.warning(
            request,
            "La membresía está pendiente. "
            "Debes revisar y actualizar su estado."
        )

    elif membresia.estado == Membresia.Estado.ACTIVA:

        membresia.estado = Membresia.Estado.INACTIVA

        membresia.save(
            update_fields=["estado", "fecha_actualizacion"]
        )

        messages.success(
            request,
            "La membresía fue desactivada."
        )

    else:

        membresia.estado = Membresia.Estado.ACTIVA

        membresia.save(
            update_fields=["estado", "fecha_actualizacion"]
        )

        messages.success(
            request,
            "La membresía fue activada."
        )

    return redirect("asociaciones:membresias_lista")
