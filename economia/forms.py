
from django import forms
from django.db.models import Q

from .models import MovimientoEconomico
from produccion.models import Cosecha
from fincas.models import Finca

from cuentas.permisos import (
    es_administrador,
    fincas_economicas_visibles,
)


class MovimientoEconomicoForm(forms.ModelForm):

    class Meta:
        model = MovimientoEconomico

        fields = [
            "finca",
            "cosecha",
            "tipo",
            "categoria",
            "fecha",
            "valor",
            "descripcion",
            "observaciones",
        ]

        widgets = {
            "finca": forms.Select(attrs={
                "class": "form-control",
            }),
            "cosecha": forms.Select(attrs={
                "class": "form-control",
            }),
            "tipo": forms.Select(attrs={
                "class": "form-control",
            }),
            "categoria": forms.Select(attrs={
                "class": "form-control",
            }),
            "fecha": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "valor": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0.01",
                "step": "0.01",
                "placeholder": "Valor en pesos colombianos",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Describe el ingreso o gasto realizado",
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
            }),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        if usuario is None:
            fincas = Finca.objects.all()
        elif es_administrador(usuario):
            fincas = Finca.objects.all()
        else:
            fincas = fincas_economicas_visibles(usuario)

        if self.instance.pk:
            fincas = fincas.filter(
                Q(activa=True) | Q(pk=self.instance.finca_id)
            )
        else:
            fincas = fincas.filter(activa=True)

        self.fields["finca"].queryset = fincas.order_by("nombre")

        cosechas = Cosecha.objects.select_related(
            "cultivo",
            "cultivo__finca",
        )

        cosechas = cosechas.filter(
            cultivo__finca__in=fincas
        )

        finca_id = (
            self.data.get(self.add_prefix("finca"))
            or getattr(self.instance, "finca_id", None)
        )

        if finca_id and str(finca_id).isdigit():
            cosechas = cosechas.filter(
                cultivo__finca_id=int(finca_id)
            )

        if self.instance.pk and self.instance.cosecha_id:
            cosechas = (
                cosechas
                | Cosecha.objects.filter(
                    pk=self.instance.cosecha_id
                )
            )

        self.fields["cosecha"].queryset = (
            cosechas.distinct().order_by("-fecha_cosecha")
        )

        self.fields["cosecha"].required = False

        tipo = (
            self.data.get(self.add_prefix("tipo"))
            or getattr(self.instance, "tipo", "")
        )

        if tipo == MovimientoEconomico.TipoMovimiento.INGRESO:

            categorias = {
                MovimientoEconomico.Categoria.VENTA_CACAO,
                MovimientoEconomico.Categoria.VENTA_OTROS,
                MovimientoEconomico.Categoria.SUBSIDIO,
                MovimientoEconomico.Categoria.OTRO_INGRESO,
            }

        elif tipo == MovimientoEconomico.TipoMovimiento.GASTO:

            categorias = {
                MovimientoEconomico.Categoria.INSUMOS,
                MovimientoEconomico.Categoria.FERTILIZANTES,
                MovimientoEconomico.Categoria.MANO_OBRA,
                MovimientoEconomico.Categoria.TRANSPORTE,
                MovimientoEconomico.Categoria.HERRAMIENTAS,
                MovimientoEconomico.Categoria.MANTENIMIENTO,
                MovimientoEconomico.Categoria.OTRO_GASTO,
            }

        else:
            categorias = None

        if categorias is not None:
            self.fields["categoria"].choices = [
                ("", "---------"),
                *[
                    (valor, nombre)
                    for valor, nombre
                    in MovimientoEconomico.Categoria.choices
                    if valor in categorias
                ],
            ]

    def clean(self):

        cleaned_data = super().clean()

        finca = cleaned_data.get("finca")
        cosecha = cleaned_data.get("cosecha")

        if finca and cosecha:
            if cosecha.cultivo.finca_id != finca.pk:
                self.add_error(
                    "cosecha",
                    "La cosecha seleccionada no pertenece a la finca indicada."
                )

        return cleaned_data
