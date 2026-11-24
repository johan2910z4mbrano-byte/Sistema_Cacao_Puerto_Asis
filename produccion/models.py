from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Sum

from cultivos.models import Cultivo


class Cosecha(models.Model):

    codigo = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Código de cosecha"
    )

    cultivo = models.ForeignKey(
        Cultivo,
        on_delete=models.PROTECT,
        related_name="cosechas",
        verbose_name="Cultivo"
    )

    fecha_cosecha = models.DateField(
        verbose_name="Fecha de cosecha"
    )

    cantidad_kg = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name="Cantidad recolectada (kg)"
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
        verbose_name = "Cosecha"
        verbose_name_plural = "Cosechas"
        ordering = ["-fecha_cosecha"]

    def __str__(self):
        return f"{self.codigo} - {self.cultivo.codigo}"


class LoteProduccion(models.Model):

    class EstadoLote(models.TextChoices):
        RECOLECTADO = "recolectado", "Recolectado"
        FERMENTACION = "fermentacion", "En fermentación"
        SECADO = "secado", "En secado"
        ALMACENADO = "almacenado", "Almacenado"
        VENDIDO = "vendido", "Vendido"
        DESCARTADO = "descartado", "Descartado"

    codigo = models.CharField(
        max_length=40,
        unique=True,
        verbose_name="Código del lote"
    )

    cosecha = models.ForeignKey(
        Cosecha,
        on_delete=models.PROTECT,
        related_name="lotes",
        verbose_name="Cosecha de origen"
    )

    cantidad_inicial_kg = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name="Cantidad inicial del lote (kg)"
    )

    estado = models.CharField(
        max_length=20,
        choices=EstadoLote.choices,
        default=EstadoLote.RECOLECTADO,
        verbose_name="Estado del lote"
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
        verbose_name = "Lote de producción"
        verbose_name_plural = "Lotes de producción"
        ordering = ["-fecha_registro"]

    def clean(self):
        super().clean()

        if (
            self.cosecha_id
            and self.cantidad_inicial_kg is not None
        ):
            otros_lotes = LoteProduccion.objects.filter(
                cosecha_id=self.cosecha_id
            )

            if self.pk:
                otros_lotes = otros_lotes.exclude(pk=self.pk)

            total = otros_lotes.aggregate(
                total=Sum("cantidad_inicial_kg")
            )["total"] or Decimal("0")

            if total + self.cantidad_inicial_kg > self.cosecha.cantidad_kg:
                raise ValidationError({
                    "cantidad_inicial_kg": (
                        "La cantidad de los lotes supera "
                        "los kilogramos registrados en la cosecha."
                    )
                })

    def __str__(self):
        return self.codigo


class ProcesoPoscosecha(models.Model):

    class Etapa(models.TextChoices):
        FERMENTACION = "fermentacion", "Fermentación"
        SECADO = "secado", "Secado"

    lote = models.ForeignKey(
        LoteProduccion,
        on_delete=models.PROTECT,
        related_name="procesos_poscosecha",
        verbose_name="Lote de producción"
    )

    etapa = models.CharField(
        max_length=20,
        choices=Etapa.choices,
        verbose_name="Etapa de poscosecha"
    )

    fecha_inicio = models.DateField(
        verbose_name="Fecha de inicio"
    )

    fecha_fin = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de finalización"
    )

    cantidad_entrada_kg = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name="Peso de entrada (kg)"
    )

    cantidad_salida_kg = models.DecimalField(
        max_digits=12,
        decimal_places=3,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.001"))],
        verbose_name="Peso de salida (kg)"
    )

    responsable = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Responsable del proceso"
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
        verbose_name = "Proceso de poscosecha"
        verbose_name_plural = "Procesos de poscosecha"
        ordering = ["-fecha_inicio"]

    def clean(self):
        super().clean()

        if (
            self.fecha_inicio
            and self.fecha_fin
            and self.fecha_fin < self.fecha_inicio
        ):
            raise ValidationError({
                "fecha_fin": (
                    "La fecha de finalización no puede "
                    "ser anterior a la fecha de inicio."
                )
            })

    @property
    def duracion_dias(self):
        if self.fecha_inicio and self.fecha_fin:
            return (self.fecha_fin - self.fecha_inicio).days

            return (

            f"{self.get_etapa_display()} - "
            f"{self.lote.codigo}"
        )
