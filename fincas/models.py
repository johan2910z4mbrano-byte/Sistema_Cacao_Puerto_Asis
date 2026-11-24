
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from productores.models import Productor


class Finca(models.Model):

    codigo = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Código de la finca"
    )

    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre del predio"
    )

    productor = models.ForeignKey(
        Productor,
        on_delete=models.PROTECT,
        related_name="fincas",
        verbose_name="Productor responsable"
    )

    municipio = models.CharField(
        max_length=100,
        default="Puerto Asís",
        verbose_name="Municipio"
    )

    departamento = models.CharField(
        max_length=100,
        default="Putumayo",
        verbose_name="Departamento"
    )

    vereda = models.CharField(
        max_length=120,
        verbose_name="Vereda o sector"
    )

    area_hectareas = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0001)],
        verbose_name="Área en hectáreas"
    )

    latitud = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ],
        verbose_name="Latitud"
    )

    longitud = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ],
        verbose_name="Longitud"
    )

    activa = models.BooleanField(
        default=True,
        verbose_name="Finca activa"
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )

    class Meta:
        verbose_name = "Finca"
        verbose_name_plural = "Fincas"
        ordering = ["nombre"]

    def clean(self):
        super().clean()

        if bool(self.latitud is None) != bool(self.longitud is None):
            raise ValidationError(
                "Debes registrar conjuntamente la latitud y la longitud."
            )

    def __str__(self):
        return f"{self.nombre} - {self.productor}"


class DelimitacionFinca(models.Model):

    finca = models.ForeignKey(
        Finca,
        on_delete=models.PROTECT,
        related_name="delimitaciones",
        verbose_name="Finca"
    )

    geojson = models.JSONField(
        verbose_name="Delimitación geográfica"
    )

    precision_metros = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Precisión GPS en metros"
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de delimitación"
    )

    class Meta:
        verbose_name = "Delimitación de finca"
        verbose_name_plural = "Delimitaciones de fincas"
        ordering = ["-fecha_registro"]

    def clean(self):
        super().clean()

        if not isinstance(self.geojson, dict):
            raise ValidationError({
                "geojson": "La delimitación debe tener formato GeoJSON."
            })

        if self.geojson.get("type") != "Polygon":
            raise ValidationError({
                "geojson": "La geometría debe ser de tipo Polygon."
            })

        coordinates = self.geojson.get("coordinates")

        if not isinstance(coordinates, list) or not coordinates:
            raise ValidationError({
                "geojson": "El polígono no contiene coordenadas."
            })

        ring = coordinates[0]

        if not isinstance(ring, list) or len(ring) < 4:
            raise ValidationError({
                "geojson": "El polígono necesita al menos tres vértices "
                           "y el punto de cierre."
            })

        for punto in ring:
            if (
                not isinstance(punto, (list, tuple))
                or len(punto) != 2
            ):
                raise ValidationError({
                    "geojson": "Cada punto debe contener longitud y latitud."
                })

            try:
                longitud, latitud = map(float, punto)
            except (TypeError, ValueError):
                raise ValidationError({
                    "geojson": "Las coordenadas deben ser valores numéricos."
                })

            if not (-180 <= longitud <= 180):
                raise ValidationError({
                    "geojson": "La longitud debe estar entre -180 y 180."
                })

            if not (-90 <= latitud <= 90):
                raise ValidationError({
                    "geojson": "La latitud debe estar entre -90 y 90."
                })

        if ring[0] != ring[-1]:
            raise ValidationError({
                "geojson": "El polígono debe cerrar repitiendo el primer punto."
            })

    def __str__(self):
        return f"Delimitación de {self.finca.nombre}"
