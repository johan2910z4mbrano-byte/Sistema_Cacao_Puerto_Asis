from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from fincas.models import Finca
from produccion.models import Cosecha


class MovimientoEconomico(models.Model):

    class TipoMovimiento(models.TextChoices):
        INGRESO = "ingreso", "Ingreso"
        GASTO = "gasto", "Gasto"

    class Categoria(models.TextChoices):
        # Ingresos
        VENTA_CACAO = "venta_cacao", "Venta de cacao"
        VENTA_OTROS = "venta_otros", "Venta de otros productos"
        SUBSIDIO = "subsidio", "Subsidio o apoyo económico"
        OTRO_INGRESO = "otro_ingreso", "Otro ingreso"

        # Gastos
        INSUMOS = "insumos", "Insumos agrícolas"
        FERTILIZANTES = "fertilizantes", "Fertilizantes"
        MANO_OBRA = "mano_obra", "Mano de obra"
        TRANSPORTE = "transporte", "Transporte"
        HERRAMIENTAS = "herramientas", "Herramientas y equipos"
        MANTENIMIENTO = "mantenimiento", "Mantenimiento"
        OTRO_GASTO = "otro_gasto", "Otro gasto"

    finca = models.ForeignKey(
        Finca,
        on_delete=models.PROTECT,
        related_name="movimientos_economicos",
        verbose_name="Finca"
    )

    cosecha = models.ForeignKey(
        Cosecha,
        on_delete=models.PROTECT,
        related_name="movimientos_economicos",
        null=True,
        blank=True,
        verbose_name="Cosecha relacionada"
    )

    tipo = models.CharField(
        max_length=10,
        choices=TipoMovimiento.choices,
        verbose_name="Tipo de movimiento"
    )

    categoria = models.CharField(
        max_length=30,
        choices=Categoria.choices,
        verbose_name="Categoría"
    )

    fecha = models.DateField(
        verbose_name="Fecha del movimiento"
    )

    valor = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name="Valor en pesos colombianos (COP)"
    )

    descripcion = models.TextField(
        verbose_name="Descripción del movimiento"
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
        verbose_name = "Movimiento económico"
        verbose_name_plural = "Movimientos económicos"
        ordering = ["-fecha", "-fecha_registro"]

    def clean(self):
        super().clean()

        if self.cosecha_id and self.finca_id:
            finca_cosecha = self.cosecha.cultivo.finca_id

            if finca_cosecha != self.finca_id:
                raise ValidationError({
                    "cosecha": (
                        "La cosecha seleccionada no pertenece "
                        "a la finca indicada."
                    )
                })

        if self.tipo == self.TipoMovimiento.INGRESO:
            categorias_validas = {
                self.Categoria.VENTA_CACAO,
                self.Categoria.VENTA_OTROS,
                self.Categoria.SUBSIDIO,
                self.Categoria.OTRO_INGRESO,
            }

        elif self.tipo == self.TipoMovimiento.GASTO:
            categorias_validas = {
                self.Categoria.INSUMOS,
                self.Categoria.FERTILIZANTES,
                self.Categoria.MANO_OBRA,
                self.Categoria.TRANSPORTE,
                self.Categoria.HERRAMIENTAS,
                self.Categoria.MANTENIMIENTO,
                self.Categoria.OTRO_GASTO,
            }

        else:
            categorias_validas = set()

        if self.categoria and self.categoria not in categorias_validas:
            raise ValidationError({
                "categoria": (
                    "La categoría no corresponde al tipo de movimiento."
                )
            })

    def __str__(self):
        return (
            f"{self.get_tipo_display()} - "
            f"{self.finca.nombre} - "
            f"${self.valor}"
        )