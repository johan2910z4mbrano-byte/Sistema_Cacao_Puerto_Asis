from django import forms
from django.db.models import Sum, Q

from .models import Cultivo, ActividadAgricola
from fincas.models import Finca


def obtener_perfil(usuario):

    if usuario is None:
        return None

    try:
        return usuario.perfil
    except Exception:
        return None


def es_administrador(usuario):
    return (
        usuario is not None
        and (usuario.is_superuser or usuario.is_staff)
    )


class CultivoForm(forms.ModelForm):

    class Meta:
        model = Cultivo

        fields = [
            "codigo",
            "finca",
            "tipo_cultivo",
            "variedad",
            "area_hectareas",
            "cantidad_plantulas",
            "fecha_siembra",
            "estado",
            "observaciones",
        ]

        widgets = {
            "codigo": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. CUL-001"
            }),
            "finca": forms.Select(attrs={
                "class": "form-control"
            }),
            "tipo_cultivo": forms.Select(attrs={
                "class": "form-control"
            }),
            "variedad": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ej. CCN-51, Criollo, etc."
            }),
            "area_hectareas": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.0001",
                "min": "0.0001"
            }),
            "cantidad_plantulas": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0"
            }),
            "fecha_siembra": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "estado": forms.Select(attrs={
                "class": "form-control"
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        if usuario is None or es_administrador(usuario):
            fincas = Finca.objects.filter(activa=True)

            if self.instance.pk:
                fincas = Finca.objects.filter(
                    Q(activa=True) | Q(pk=self.instance.finca_id)
                )

            self.fields["finca"].queryset = fincas.order_by("nombre")
            return

        perfil = obtener_perfil(usuario)

        if perfil and perfil.tipo_usuario == "productor":
            fincas = Finca.objects.filter(
                productor_id=perfil.productor_id
            )

            if self.instance.pk:
                fincas = fincas.filter(
                    Q(activa=True) | Q(pk=self.instance.finca_id)
                )
            else:
                fincas = fincas.filter(activa=True)

            self.fields["finca"].queryset = fincas.order_by("nombre")

        else:
            self.fields["finca"].queryset = Finca.objects.none()

    def clean(self):
        cleaned_data = super().clean()

        finca = cleaned_data.get("finca")
        area = cleaned_data.get("area_hectareas")

        if finca and area is not None and finca.area_hectareas is not None:

            otras_areas = finca.cultivos.exclude(
                pk=self.instance.pk
            ).aggregate(
                total=Sum("area_hectareas")
            )["total"] or 0

            if otras_areas + area > finca.area_hectareas:
                self.add_error(
                    "area_hectareas",
                    "El área cultivada supera el área disponible de la finca."
                )

        return cleaned_data


class ActividadAgricolaForm(forms.ModelForm):

    class Meta:
        model = ActividadAgricola

        fields = [
            "cultivo",
            "tipo_actividad",
            "fecha",
            "descripcion",
            "insumos_utilizados",
            "costo_estimado",
            "responsable",
            "observaciones",
        ]

        widgets = {
            "cultivo": forms.Select(attrs={
                "class": "form-control"
            }),
            "tipo_actividad": forms.Select(attrs={
                "class": "form-control"
            }),
            "fecha": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3
            }),
            "insumos_utilizados": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2
            }),
            "costo_estimado": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "step": "0.01"
            }),
            "responsable": forms.TextInput(attrs={
                "class": "form-control"
            }),
            "observaciones": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2
            }),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        cultivos = Cultivo.objects.exclude(
            estado=Cultivo.EstadoCultivo.INACTIVO
        ).select_related("finca")

        if usuario is None or es_administrador(usuario):
            if self.instance.pk:
                cultivos = Cultivo.objects.filter(
                    Q(
                        estado__in=[
                            Cultivo.EstadoCultivo.ESTABLECIMIENTO,
                            Cultivo.EstadoCultivo.DESARROLLO,
                            Cultivo.EstadoCultivo.PRODUCTIVO,
                            Cultivo.EstadoCultivo.RENOVACION,
                        ]
                    )
                    | Q(pk=self.instance.cultivo_id)
                ).select_related("finca")

        else:
            perfil = obtener_perfil(usuario)

            if perfil and perfil.tipo_usuario == "productor":
                cultivos = cultivos.filter(
                    finca__productor_id=perfil.productor_id
                )

                if self.instance.pk:
                    cultivos = Cultivo.objects.filter(
                        Q(
                            finca__productor_id=perfil.productor_id,
                            estado__in=[
                                Cultivo.EstadoCultivo.ESTABLECIMIENTO,
                                Cultivo.EstadoCultivo.DESARROLLO,
                                Cultivo.EstadoCultivo.PRODUCTIVO,
                                Cultivo.EstadoCultivo.RENOVACION,
                            ]
                        )
                        | Q(pk=self.instance.cultivo_id)
                    ).select_related("finca")
            else:
                cultivos = Cultivo.objects.none()

        self.fields["cultivo"].queryset = cultivos.order_by("codigo")