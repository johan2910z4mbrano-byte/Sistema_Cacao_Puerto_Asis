
from django.db import models
from django.core.validators import MinValueValidator

from fincas.models import Finca


class Cultivo(models.Model):

    class TipoCultivo(models.TextChoices):
        CACAO = "cacao", "Cacao"
        PLATANO = "platano", "Plátano"
        YUCA = "yuca", "Yuca"
        ARROZ = "arroz", "Arroz"
        OTRO = "otro", "Otro"

    class EstadoCultivo(models.TextChoices):
        ESTABLECIMIENTO = "establecimiento", "Establecimiento"
        DESARROLLO = "desarrollo", "Desarrollo"
        PRODUCTIVO = "productivo", "Productivo"
        RENOVACION = "renovacion", "Renovación"
        INACTIVO = "inactivo", "Inactivo"

    codigo = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Código del cultivo"
    )

    finca = models.ForeignKey(
        Finca,
        on_delete=models.PROTECT,
        related_name="cultivos",
        verbose_name="Finca"
    )

    tipo_cultivo = models.CharField(
        max_length=20,
        choices=TipoCultivo.choices,
        default=TipoCultivo.CACAO,
        verbose_name="Tipo de cultivo"
    )

    variedad = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Variedad"
    )

    area_hectareas = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        validators=[MinValueValidator(0.0001)],
        verbose_name="Área cultivada en hectáreas"
    )

    cantidad_plantulas = models.PositiveIntegerField(
        default=0,
        verbose_name="Cantidad de plántulas"
    )

    fecha_siembra = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de establecimiento"
    )

    estado = models.CharField(
        max_length=20,
        choices=EstadoCultivo.choices,
        default=EstadoCultivo.ESTABLECIMIENTO,
        verbose_name="Estado del cultivo"
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
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
        verbose_name = "Cultivo"
        verbose_name_plural = "Cultivos"
        ordering = ["finca__nombre", "codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.get_tipo_cultivo_display()}"


class ActividadAgricola(models.Model):

    class TipoActividad(models.TextChoices):
        LIMPIEZA = "limpieza", "Limpieza"
        PODA = "poda", "Poda"
        FERTILIZACION = "fertilizacion", "Fertilización"
        FUMIGACION = "fumigacion", "Fumigación"
        CONTROL_PLAGAS = "control_plagas", "Control de plagas"
        RIEGO = "riego", "Riego"
        RESIEMBRA = "resiembra", "Resiembra"
        OTRO = "otro", "Otra actividad"

    cultivo = models.ForeignKey(
        Cultivo,
        on_delete=models.PROTECT,
        related_name="actividades",
        verbose_name="Cultivo"
    )

    tipo_actividad = models.CharField(
        max_length=25,
        choices=TipoActividad.choices,
        verbose_name="Tipo de actividad"
    )

    fecha = models.DateField(
        verbose_name="Fecha de realización"
    )

    descripcion = models.TextField(
        verbose_name="Descripción de la actividad"
    )

    insumos_utilizados = models.TextField(
        blank=True,
        verbose_name="Insumos utilizados"
    )

    costo_estimado = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Costo de la actividad"
    )

    responsable = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Responsable"
    )

    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )

    class Meta:
        verbose_name = "Actividad agrícola"
        verbose_name_plural = "Actividades agrícolas"
        ordering = ["-fecha"]

    def __str__(self):
        return (
            f"{self.get_tipo_actividad_display()} - "
            f"{self.cultivo.codigo} - {self.fecha}"
        )
