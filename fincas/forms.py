from django import forms
from django.db.models import Q

from .models import Finca
from productores.models import Productor


class FincaForm(forms.ModelForm):

    geojson = forms.JSONField(
        required=False,
        widget=forms.HiddenInput()
    )

    precision_metros = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Finca

        fields = [
            "codigo",
            "nombre",
            "productor",
            "municipio",
            "departamento",
            "vereda",
            "area_hectareas",
            "latitud",
            "longitud",
        ]

        labels = {
            "codigo": "Código de la finca",
            "nombre": "Nombre del predio",
            "productor": "Productor responsable",
            "municipio": "Municipio",
            "departamento": "Departamento",
            "vereda": "Vereda o sector",
            "area_hectareas": "Área en hectáreas",
            "latitud": "Latitud GPS",
            "longitud": "Longitud GPS",
        }

        help_texts = {
            "area_hectareas": (
                "Superficie aproximada del predio en hectáreas."
            ),
            "latitud": "Coordenada GPS obtenida mediante el mapa.",
            "longitud": "Coordenada GPS obtenida mediante el mapa.",
        }

        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. FIN-001"
            }),
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre de la finca"
            }),
            "productor": forms.Select(attrs={
                "class": "form-control"
            }),
            "municipio": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "departamento": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "vereda": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Vereda donde está ubicada"
            }),
            "area_hectareas": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. 2.0000",
                "step": "0.0001",
                "min": "0.0001"
            }),
            "latitud": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Se obtiene mediante GPS",
                "step": "any"
            }),
            "longitud": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Se obtiene mediante GPS",
                "step": "any"
            }),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        if usuario is None:
            if self.instance.pk:
                self.fields["productor"].queryset = (
                    Productor.objects.all()
                )
            else:
                self.fields["productor"].queryset = (
                    Productor.objects.filter(activo=True)
                    .order_by("apellidos", "nombres")
                )

            return

        es_admin = usuario.is_superuser or usuario.is_staff

        if es_admin:
            self.fields["productor"].queryset = (
                Productor.objects.all()
                if self.instance.pk
                else Productor.objects.filter(activo=True)
            )
            return

        try:
            perfil = usuario.perfil
        except Exception:
            perfil = None

        if (
            perfil
            and perfil.tipo_usuario == "productor"
            and perfil.productor_id
        ):
            productor = Productor.objects.filter(
                pk=perfil.productor_id
            )

            self.fields["productor"].queryset = productor
            self.fields["productor"].initial = productor.first()
            self.fields["productor"].disabled = True

        else:
            self.fields["productor"].queryset = (
                Productor.objects.none()
            )