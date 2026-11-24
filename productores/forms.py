from django import forms
from .models import Productor


class ProductorForm(forms.ModelForm):
    class Meta:
        model = Productor
        fields = [
            "codigo",
            "nombres",
            "apellidos",
            "telefono",
            "correo",
            "vereda",
        ]
        labels = {
            "codigo": "Código del productor",
            "nombres": "Nombres",
            "apellidos": "Apellidos",
            "telefono": "Teléfono de contacto",
            "correo": "Correo electrónico",
            "vereda": "Vereda o sector",
        }
        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. CAC-001",
                "autocomplete": "off",
            }),
            "nombres": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombres del productor",
                "autocomplete": "given-name",
            }),
            "apellidos": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Apellidos del productor",
                "autocomplete": "family-name",
            }),
            "telefono": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Número de contacto",
                "autocomplete": "tel",
                "inputmode": "tel",
            }),
            "correo": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "Correo electrónico de contacto",
                "autocomplete": "email",
                "inputmode": "email",
            }),
            "vereda": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre de la vereda",
            }),
        }

    def clean_telefono(self):
        telefono = (self.cleaned_data.get("telefono") or "").strip()
        return telefono

    def clean_correo(self):
        correo = (self.cleaned_data.get("correo") or "").strip()
        return correo.lower()