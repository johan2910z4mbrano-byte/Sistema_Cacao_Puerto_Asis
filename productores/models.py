from django.db import models


class Productor(models.Model):

    codigo = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Código del productor"
    )

    nombres = models.CharField(
        max_length=100,
        verbose_name="Nombres"
    )

    apellidos = models.CharField(
        max_length=100,
        verbose_name="Apellidos"
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono"
    )

    correo = models.EmailField(
    max_length=254,
    blank=True,
    verbose_name="Correo electrónico"
)

    vereda = models.CharField(
        max_length=120,
        blank=True,
        verbose_name="Vereda"
    )

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de registro"
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )

    activo = models.BooleanField(
        default=True,
        verbose_name="Estado del productor"
    )

    class Meta:
        verbose_name = "Productor"
        verbose_name_plural = "Productores"
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.codigo} - {self.nombres} {self.apellidos}"