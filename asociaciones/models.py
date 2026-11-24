from django.db import models
from django.core.validators import MinLengthValidator

from productores.models import Productor

from django.core.exceptions import ValidationError

class Asociacion(models.Model):

    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre de la asociación"
    )

    sigla = models.CharField(
        max_length=30,
        blank=True,
        verbose_name="Sigla"
    )

    descripcion = models.TextField(
        blank=True,
        verbose_name="Descripción"
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
        blank=True,
        verbose_name="Vereda o sector"
    )

    telefono_contacto = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono institucional"
    )

    correo_contacto = models.EmailField(
        blank=True,
        verbose_name="Correo institucional"
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Estado de la asociación"
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
        verbose_name = "Asociación"
        verbose_name_plural = "Asociaciones"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Membresia(models.Model):

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        ACTIVA = "activa", "Activa"
        INACTIVA = "inactiva", "Inactiva"

    productor = models.ForeignKey(
        Productor,
        on_delete=models.PROTECT,
        related_name="membresias",
        verbose_name="Productor"
    )

    asociacion = models.ForeignKey(
        Asociacion,
        on_delete=models.PROTECT,
        related_name="membresias",
        verbose_name="Asociación"
    )

    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        verbose_name="Estado de la membresía"
    )

    fecha_vinculacion = models.DateField(
        null=True,
        blank=True,
        verbose_name="Fecha de vinculación"
    )

    autorizacion_compartir = models.BooleanField(
        default=False,
        verbose_name="Autorización para consultar información"
    )

    fecha_autorizacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de autorización"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )

    class Meta:
        verbose_name = "Membresía"
        verbose_name_plural = "Membresías"
        ordering = ["productor__apellidos", "productor__nombres"]

        constraints = [
            models.UniqueConstraint(
                fields=["productor", "asociacion"],
                name="unica_membresia_productor_asociacion"
            )
        ]

    def __str__(self):
        return (
            f"{self.productor} - {self.asociacion}"
        )

class ResponsableAsociacion(models.Model):

    perfil = models.ForeignKey(
        "cuentas.PerfilUsuario",
        on_delete=models.PROTECT,
        related_name="responsabilidades_asociacion",
        verbose_name="Perfil del representante"
    )

    asociacion = models.ForeignKey(
        Asociacion,
        on_delete=models.PROTECT,
        related_name="responsables",
        verbose_name="Asociación"
    )

    cargo = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Cargo en la asociación"
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Responsabilidad activa"
    )

    fecha_asignacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de asignación"
    )

    class Meta:
        verbose_name = "Responsable de asociación"
        verbose_name_plural = "Responsables de asociaciones"

        constraints = [
            models.UniqueConstraint(
                fields=["perfil", "asociacion"],
                name="unico_responsable_por_asociacion"
            )
        ]

    def clean(self):
        super().clean()

        if (
            self.perfil_id
            and self.perfil.tipo_usuario != "asociacion"
        ):
            raise ValidationError({
                "perfil": (
                    "El usuario debe tener un perfil de representante "
                    "de asociación."
                )
            })

    def __str__(self):
        return f"{self.perfil.usuario.username} - {self.asociacion.nombre}"