# Cacao Gestión — Sistema de información para productores de cacao de Puerto Asís

Prototipo académico desarrollado con Django y PostgreSQL para apoyar el registro y la consulta de información de pequeños productores agropecuarios de Puerto Asís, Putumayo, con énfasis en la actividad cacaotera.

## Funcionalidades del prototipo

- Registro y consulta de productores.
- Gestión de asociaciones y membresías.
- Registro de fincas y visualización de su ubicación/delimitación en mapa.
- Gestión de cultivos y actividades agrícolas.
- Registro de cosechas, lotes y procesos de poscosecha.
- Registro y consulta de movimientos económicos.
- Control de acceso según el perfil de usuario.

> El alcance y los datos disponibles corresponden a un prototipo académico. Los registros de prueba son demostrativos y no deben presentarse como resultados de campo verificados.

## Tecnologías

- Python 3.15.2 (entorno de desarrollo utilizado).
- Django 6.1.3.
- PostgreSQL.
- psycopg 3.3.8.
- HTML, CSS y JavaScript.
- python-dotenv para leer la configuración local desde `.env`.

Las dependencias de Python están registradas en `requirements.txt`.

## Requisitos previos

1. Python instalado.
2. PostgreSQL instalado y en ejecución.
3. Git (opcional para clonar el repositorio).

## Instalación local en Windows (PowerShell)

### 1. Obtener el código

Clonar el repositorio o descargarlo y abrir PowerShell en la carpeta raíz, donde se encuentra `manage.py`.

```powershell
git clone <URL_DEL_REPOSITORIO>
cd <CARPETA_DEL_PROYECTO>
```

Si ya se descargó el código ZIP, basta con abrir PowerShell en la carpeta extraída.

### 2. Crear y activar el entorno virtual

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si la política de ejecución de PowerShell impide activar el entorno, también puede invocarse directamente el intérprete de `.venv` sin activarlo:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 3. Instalar dependencias

Con el entorno activado:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar la plantilla y crear el archivo local `.env`:

```powershell
Copy-Item .env.example .env
notepad .env
```

Completar `.env` con los datos de la instalación local. `DJANGO_SECRET_KEY` debe ser una clave secreta nueva y privada. No compartir ni publicar `.env`.

### 5. Preparar PostgreSQL

Crear en PostgreSQL una base de datos y un usuario con permisos sobre ella. Los nombres y credenciales deben coincidir con las variables configuradas en `.env` (`DB_NAME`, `DB_USER` y `DB_PASSWORD`).

### 6. Aplicar migraciones y comprobar el proyecto

```powershell
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py check
```

### 7. Crear un usuario administrador

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Seguir las instrucciones de Django para establecer usuario y contraseña. No reutilizar contraseñas de demostración en una instalación compartida.

### 8. Ejecutar el servidor de desarrollo

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Abrir en el navegador:

- Aplicación: http://127.0.0.1:8000/
- Inicio de sesión: http://127.0.0.1:8000/accounts/login/

El servidor se detiene con `Ctrl+C` en la ventana de PowerShell.

## Estructura general

```text
Sistema_Cacao_Puerto_Asis/
├── asociaciones/
├── config/
├── cuentas/
├── cultivos/
├── economia/
├── fincas/
├── produccion/
├── productores/
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## Seguridad y manejo de datos

- `.env` contiene secretos y credenciales locales; no debe subirse al repositorio.
- No publicar copias de seguridad, archivos de importación con teléfonos/correos ni datos personales de productores.
- El archivo `.gitignore` excluye estos elementos del control de versiones.
- Para una instalación compartida, deben revisarse `DEBUG`, `ALLOWED_HOSTS`, HTTPS, cookies seguras, política de contraseñas y demás ajustes de despliegue antes de exponer la aplicación a Internet.
- Los datos demostrativos deben identificarse como tales y mantenerse separados de los datos reales autorizados.

## Estado del proyecto

Prototipo funcional para evaluación académica. La ejecución descrita corresponde a un entorno local de desarrollo; este repositorio no representa por sí solo un despliegue de producción.
