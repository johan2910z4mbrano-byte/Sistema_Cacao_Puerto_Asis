
from django import forms

from cultivos.models import Cultivo
from .models import Cosecha, LoteProduccion, ProcesoPoscosecha

from cuentas.permisos import (
    es_administrador,
    cosechas_visibles,
    lotes_visibles,
)


class CosechaForm(forms.ModelForm):

    class Meta:
        model = Cosecha

        fields = [
            "codigo",
            "cultivo",
            "fecha_cosecha",
            "cantidad_kg",
            "observaciones",
        ]

        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. COS-001",
            }),
            "cultivo": forms.Select(attrs={
                "class": "form-control",
            }),
            "fecha_cosecha": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "cantidad_kg": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0.001",
                "step": "0.001",
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        if usuario is None or es_administrador(usuario):
            cultivos = Cultivo.objects.exclude(
                estado=Cultivo.EstadoCultivo.INACTIVO
            ).select_related("finca")

        else:
            cultivos = cosechas_visibles(usuario).none()

            # Obtener cultivos que pertenecen a fincas visibles.
            from cuentas.permisos import fincas_visibles

            cultivos = Cultivo.objects.filter(
                finca__in=fincas_visibles(usuario)
            ).exclude(
                estado=Cultivo.EstadoCultivo.INACTIVO
            ).select_related("finca")

        # Permitir conservar la relación actual al editar.
        if self.instance.pk:
            cultivos = (
                cultivos
                | Cultivo.objects.filter(
                    pk=self.instance.cultivo_id
                )
            )

        self.fields["cultivo"].queryset = (
            cultivos.distinct().order_by("codigo")
        )


class LoteProduccionForm(forms.ModelForm):

    class Meta:
        model = LoteProduccion

        fields = [
            "codigo",
            "cosecha",
            "cantidad_inicial_kg",
            "estado",
            "observaciones",
        ]

        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. LOT-001",
            }),
            "cosecha": forms.Select(attrs={
                "class": "form-control",
            }),
            "cantidad_inicial_kg": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0.001",
                "step": "0.001",
            }),
            "estado": forms.Select(attrs={
                "class": "form-control",
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        if usuario is None or es_administrador(usuario):
            cosechas = Cosecha.objects.all()
        else:
            cosechas = cosechas_visibles(usuario)

        # Conservar la cosecha del lote cuando se está editando.
        if self.instance.pk:
            cosechas = (
                cosechas
                | Cosecha.objects.filter(
                    pk=self.instance.cosecha_id
                )
            )

        self.fields["cosecha"].queryset = (
            cosechas.select_related(
                "cultivo",
                "cultivo__finca",
            ).distinct().order_by("-fecha_cosecha")
        )


class ProcesoPoscosechaForm(forms.ModelForm):

    class Meta:
        model = ProcesoPoscosecha

        fields = [
            "lote",
            "etapa",
            "fecha_inicio",
            "fecha_fin",
            "cantidad_entrada_kg",
            "cantidad_salida_kg",
            "responsable",
            "observaciones",
        ]

        widgets = {
            "lote": forms.Select(attrs={
                "class": "form-control",
            }),
            "etapa": forms.Select(attrs={
                "class": "form-control",
            }),
            "fecha_inicio": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "fecha_fin": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "cantidad_entrada_kg": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0.001",
                "step": "0.001",
            }),
            "cantidad_salida_kg": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0.001",
                "step": "0.001",
            }),
            "responsable": forms.TextInput(attrs={
                "class": "form-control",
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
            }),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        if usuario is None or es_administrador(usuario):
            lotes = LoteProduccion.objects.all()
        else:
            lotes = lotes_visibles(usuario)

        # Conservar el lote del proceso cuando se está editando.
        if self.instance.pk:
            lotes = (
                lotes
                | LoteProduccion.objects.filter(
                    pk=self.instance.lote_id
                )
            )

        self.fields["lote"].queryset = (
            lotes.select_related(
                "cosecha",
                "cosecha__cultivo",
                "cosecha__cultivo__finca",
            ).distinct().order_by("codigo")
        )
