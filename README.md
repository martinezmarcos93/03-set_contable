# Set Contable — Software de Gestión para Estudios Contables

Herramienta de escritorio en Python/PyQt6 para la gestión de clientes, honorarios y liquidación de sueldos en estudios contables argentinos.

---

## Características

- **Panel de Monotributistas** — ABM completo con búsqueda, filtros por condición, marcas de revisión y cuenta corriente por cliente.
- **Panel de Responsables Inscriptos** — ABM con claves ARCA/ARBA/AGIP, condición IIBB, estado y cuenta corriente.
- **Detalle de cliente** — Datos de contacto, CBU/banco, honorarios mensuales y cuenta corriente (debe/haber/saldo acumulado).
- **Panel de Honorarios** — Vista global de todos los movimientos, filtrable por tipo, año, mes y nombre de cliente.
- **Liquidador de Sueldos** — CCT 130/75 (Empleados de Comercio): básico proporcional, antigüedad, asistencia, horas extra, descuentos legales y exportación a PDF.
- **Calculadoras**
  - IVA y alícuotas: neto → total, total → neto, monto IVA → neto base, percepción → neto base.
  - Porcentajes: variación, aumento/descuento, deshacer aumento, y más.

---

## Requisitos

- Python 3.10 o superior
- PyQt6
- reportlab *(opcional, solo necesario para generar PDFs desde el Liquidador de Sueldos)*

Instalación de dependencias:

```bash
pip install PyQt6 reportlab
```

---

## Instalación y primer uso

1. Cloná o descargá el repositorio.
2. Asegurate de tener la carpeta `Data/` en el mismo directorio que los scripts. Si no existe, se crea automáticamente al primer inicio.
3. Ejecutá el punto de entrada:

```bash
python M1login.py
```

4. En el **primer inicio**, la app mostrará un formulario de configuración inicial donde definís:
   - Nombre del estudio (aparece en la interfaz y en los PDFs generados).
   - Usuario y contraseña (mínimo 6 caracteres).
   
   Estos datos se guardan localmente en `Data/credenciales.json`. **No hay credenciales por defecto en el código.**

5. Para **restablecer las credenciales** (por ejemplo, si olvidaste la contraseña), eliminá el archivo `Data/credenciales.json` y reiniciá la app, o usá el botón "Restablecer credenciales" en la pantalla de login.

---

## Estructura del proyecto

```
/
├── M1login.py            # Pantalla de login y configuración inicial
├── M2SWorkWindows.py     # Ventana principal de navegación
├── M3TablaMono.py        # Panel de Monotributistas
├── M4TablaResp.py        # Panel de Responsables Inscriptos
├── M6Calculadoras.py     # Calculadoras de IVA y porcentajes
├── M7LiquidadorSueldos.py# Liquidador CCT 130/75 + exportación PDF
├── MClienteDetalle.py    # Detalle de cliente y cuenta corriente
├── MHonorarios.py        # Panel global de honorarios
└── Data/                 # Generado automáticamente
    ├── credenciales.json # Configuración del estudio (excluido del repo)
    ├── datos_monot.db    # Base de datos Monotributistas
    ├── datos_resp.db     # Base de datos Responsables Inscriptos
    ├── clientes.db       # Detalle de clientes y cuenta corriente
    ├── liquidacion_sueldo.pdf  # PDF generado por el Liquidador
    └── logo1.jpg         # Logo del estudio (agregar manualmente)
```

---

## Agregar logo

Colocá una imagen llamada `logo1.jpg` dentro de la carpeta `Data/`. Se usa como ícono de las ventanas. Si no existe, la app funciona igual sin ícono.

---

## Bases de datos

La app usa SQLite. Los archivos `.db` se crean automáticamente en `Data/` al primer uso. No es necesario ningún servidor ni configuración previa.

| Archivo | Contenido |
|---|---|
| `datos_monot.db` | Clientes monotributistas |
| `datos_resp.db` | Responsables inscriptos |
| `clientes.db` | Datos de contacto, honorarios y cuenta corriente |

---

## .gitignore recomendado

Para no subir datos personales al repositorio, agregá este `.gitignore`:

```
Data/
*.db
*.pdf
__pycache__/
*.pyc
```

---

## Convenciones del código

- Módulos con prefijo `M` + número: pantallas principales en orden de flujo.
- Módulos con prefijo `M` + nombre: módulos funcionales auxiliares.
- Todas las ventanas se centran en pantalla automáticamente.
- Colores de estado: verde = activo/cobrado, rojo = baja/debe, amarillo = suspendido.

---

## Licencia

MIT — Libre para uso, modificación y distribución.
