from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from productores.models import Productor


class PerfilUsuario(models.Model):

    class TipoUsuario(models.TextChoices):
        PRODUCTOR = "productor", "Productor"
        ASOCIACION = "asociacion", "Representante de asociación"

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil",
        verbose_name="Cuenta de usuario"
    )

    tipo_usuario = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        verbose_name="Tipo de usuario"
    )

    productor = models.OneToOneField(
        Productor,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="perfil_usuario",
        verbose_name="Productor relacionado"
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
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def clean(self):
        super().clean()

        if (
            self.tipo_usuario == self.TipoUsuario.PRODUCTOR
            and not self.productor_id
        ):
            raise ValidationError({
                "productor": "Un perfil de productor debe estar relacionado "
                             "con un registro de productor."
            })

        if (
            self.tipo_usuario == self.TipoUsuario.ASOCIACION
            and self.productor_id
        ):
            raise ValidationError({
                "productor": "Un representante de asociación no debe "
                             "estar vinculado como productor."
            })

    def __str__(self):
        return (
            f"{self.usuario.username} - "
            f"{self.get_tipo_usuario_display()}"
        )
