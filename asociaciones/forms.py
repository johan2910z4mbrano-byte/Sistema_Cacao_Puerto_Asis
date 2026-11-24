from django import forms
from .models import Asociacion


class AsociacionForm(forms.ModelForm):

    class Meta:
        model = Asociacion

        fields = [
            "nombre",
            "sigla",
            "descripcion",
            "municipio",
            "departamento",
            "vereda",
            "telefono_contacto",
            "correo_contacto",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre de la asociación"
            }),

            "sigla": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Sigla de la organización"
            }),

            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descripción de la asociación"
            }),

            "municipio": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "departamento": forms.TextInput(attrs={
                "class": "form-control"
            }),

            "vereda": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Vereda o sector"
            }),

            "telefono_contacto": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono institucional"
            }),

            "correo_contacto": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Correo institucional"
            }),
        }

from django import forms
from django.utils import timezone

from .models import Asociacion, Membresia
from productores.models import Productor


class AsociacionForm(forms.ModelForm):

    class Meta:
        model = Asociacion

        fields = [
            "nombre",
            "sigla",
            "descripcion",
            "municipio",
            "departamento",
            "vereda",
            "telefono_contacto",
            "correo_contacto",
        ]

        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre de la asociación"
            }),
            "sigla": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Sigla de la organización"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descripción de la asociación"
            }),
            "municipio": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "departamento": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "vereda": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Vereda o sector"
            }),
            "telefono_contacto": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Teléfono institucional"
            }),
            "correo_contacto": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Correo institucional"
            }),
        }


class MembresiaForm(forms.ModelForm):

    class Meta:
        model = Membresia

        fields = [
            "productor",
            "asociacion",
            "estado",
            "fecha_vinculacion",
            "autorizacion_compartir",
        ]

        labels = {
            "productor": "Productor",
            "asociacion": "Asociación",
            "estado": "Estado de la membresía",
            "fecha_vinculacion": "Fecha de vinculación",
            "autorizacion_compartir": (
                "El productor autorizó compartir su información"
            ),
        }

        help_texts = {
            "autorizacion_compartir": (
                "Marca esta opción únicamente cuando exista "
                "autorización expresa y verificable del productor."
            ),
        }

        widgets = {
            "productor": forms.Select(attrs={
                "class": "form-control"
            }),
            "asociacion": forms.Select(attrs={
                "class": "form-control"
            }),
            "estado": forms.Select(attrs={
                "class": "form-control"
            }),
            "fecha_vinculacion": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "autorizacion_compartir": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            self.fields["productor"].queryset = (
                Productor.objects.filter(
                    activo=True
                ).order_by("apellidos", "nombres")
            )

            self.fields["asociacion"].queryset = (
                Asociacion.objects.filter(
                    activo=True
                ).order_by("nombre")
            )

    def save(self, commit=True):
        membresia = super().save(commit=False)

        if membresia.autorizacion_compartir:
            if not membresia.fecha_autorizacion:
                membresia.fecha_autorizacion = timezone.now()
        else:
            membresia.fecha_autorizacion = None

        if commit:
            membresia.save()

        return membresia