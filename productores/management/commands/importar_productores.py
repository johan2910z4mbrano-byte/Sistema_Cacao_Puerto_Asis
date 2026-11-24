"""Importa contactos de productores desde un CSV usando el modelo Productor.

Uso desde la raíz del proyecto Django:
    python manage.py importar_productores ruta/al/archivo.csv
    python manage.py importar_productores ruta/al/archivo.csv --confirmar

Sin --confirmar solo muestra una vista previa y NO modifica la base de datos.
"""

import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import Q

from productores.models import Productor


class Command(BaseCommand):
    help = "Importa productores desde CSV; por defecto ejecuta solo una vista previa."

    def add_arguments(self, parser):
        parser.add_argument("archivo", type=str, help="Ruta del archivo CSV")
        parser.add_argument(
            "--confirmar",
            action="store_true",
            help="Guarda los registros. Sin esta opción solo muestra una vista previa.",
        )

    def handle(self, *args, **options):
        ruta = Path(options["archivo"]).expanduser()
        confirmar = options["confirmar"]

        if not ruta.is_file():
            raise CommandError(f"No se encontró el archivo: {ruta}")

        try:
            with ruta.open("r", encoding="utf-8-sig", newline="") as archivo:
                lector = csv.DictReader(archivo)
                columnas = {c.strip().lower() for c in (lector.fieldnames or [])}
                requeridas = {"nombres", "apellidos", "telefono", "correo"}
                faltantes = requeridas - columnas
                if faltantes:
                    raise CommandError(
                        "Faltan columnas en el CSV: " + ", ".join(sorted(faltantes))
                    )
                filas = list(lector)
        except UnicodeDecodeError as exc:
            raise CommandError("El CSV debe estar guardado en UTF-8.") from exc

        preparados = []
        errores = []
        telefonos_archivo = set()
        correos_archivo = set()

        for numero, fila in enumerate(filas, start=2):
            fila = {
                str(k).strip().lower(): (v or "").strip()
                for k, v in fila.items()
                if k
            }
            nombres = fila.get("nombres", "").strip()
            apellidos = fila.get("apellidos", "").strip()
            telefono = fila.get("telefono", "").strip()
            correo = fila.get("correo", "").strip().lower()

            if not nombres or not apellidos:
                errores.append(f"Fila {numero}: nombres y apellidos son obligatorios.")
                continue
            if not telefono and not correo:
                errores.append(
                    f"Fila {numero}: debe tener teléfono o correo para identificarlo."
                )
                continue
            if correo and ("@" not in correo or "." not in correo.rsplit("@", 1)[-1]):
                errores.append(f"Fila {numero}: correo no parece válido ({correo}).")
                continue

            # Evita duplicados dentro del mismo CSV durante vista previa e importación.
            if telefono and telefono in telefonos_archivo:
                errores.append(
                    f"Fila {numero}: teléfono repetido dentro del CSV ({telefono})."
                )
                continue
            if correo and correo in correos_archivo:
                errores.append(
                    f"Fila {numero}: correo repetido dentro del CSV ({correo})."
                )
                continue
            if telefono:
                telefonos_archivo.add(telefono)
            if correo:
                correos_archivo.add(correo)

            preparados.append({
                "fila": numero,
                "nombres": nombres,
                "apellidos": apellidos,
                "telefono": telefono,
                "correo": correo,
            })

        if errores:
            for error in errores:
                self.stderr.write(self.style.ERROR(error))
            raise CommandError("Corrige las filas indicadas antes de importar.")

        self.stdout.write(self.style.MIGRATE_HEADING("Vista previa de importación de productores"))
        creados = 0
        existentes = 0

        # Reserva en memoria los códigos ya existentes y los propuestos. Así la
        # vista previa muestra códigos distintos, aunque todavía no guarde nada.
        codigos_reservados = set(Productor.objects.values_list("codigo", flat=True))
        siguiente_consecutivo = 1

        contexto = transaction.atomic() if confirmar else _SinTransaccion()
        with contexto:
            for registro in preparados:
                filtros = Q()
                tiene_filtro = False
                if registro["telefono"]:
                    filtros |= Q(telefono=registro["telefono"])
                    tiene_filtro = True
                if registro["correo"]:
                    filtros |= Q(correo__iexact=registro["correo"])
                    tiene_filtro = True

                existente = Productor.objects.filter(filtros).first() if tiene_filtro else None
                if existente:
                    existentes += 1
                    self.stdout.write(self.style.WARNING(
                        f"OMITIR (ya existe, ID {existente.pk}): "
                        f"{registro['nombres']} {registro['apellidos']}"
                    ))
                    continue

                while True:
                    codigo = f"CAC-I{siguiente_consecutivo:05d}"
                    siguiente_consecutivo += 1
                    if codigo not in codigos_reservados:
                        codigos_reservados.add(codigo)
                        break

                datos = {
                    "codigo": codigo,
                    "nombres": registro["nombres"],
                    "apellidos": registro["apellidos"],
                    "telefono": registro["telefono"],
                    "correo": registro["correo"],
                }
                if confirmar:
                    Productor.objects.create(**datos)
                    creados += 1
                    self.stdout.write(self.style.SUCCESS(
                        f"CREADO {codigo}: {registro['nombres']} {registro['apellidos']}"
                    ))
                else:
                    creados += 1
                    self.stdout.write(
                        f"PREVISTO {codigo}: {registro['nombres']} {registro['apellidos']}"
                    )

        self.stdout.write("")
        if confirmar:
            self.stdout.write(self.style.SUCCESS(
                f"Importación finalizada. Creados: {creados}; ya existentes: {existentes}."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Vista previa terminada. Se crearían: {creados}; ya existentes: {existentes}."
            ))
            self.stdout.write(
                "No se guardó ningún registro. Usa --confirmar solo después de revisar el resultado."
            )


class _SinTransaccion:
    """Context manager sin efectos para reutilizar el mismo bloque en modo vista previa."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False
