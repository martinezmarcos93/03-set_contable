"""
M9LSDExport.py — Generación del TXT para el Libro de Sueldos Digital
======================================================================
Este módulo tiene dos responsabilidades:

1. MOTOR DE CONSTRUCCIÓN TXT (funciones puras, sin GUI):
   - make_registro_01/02/03/04 y write_txt
   - build_txt_desde_liquidacion(): recibe el resultado de M7 + datos de nómina
     y devuelve las líneas listas para guardar.

2. VENTANA DE EXPORTACIÓN (VentanaExportLSD):
   - Se abre desde M7 tras calcular una liquidación.
   - Permite elegir empleado, período, número de liquidación.
   - Muestra preview de los conceptos que se incluirán.
   - Genera el TXT y guarda el historial en lsd.db.

Depende de M8LSDConfig (lectura de DB) pero NO de M7 directamente
(recibe un dict de resultados como parámetro).
"""

import os
import re
from datetime import date, datetime
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QFileDialog, QApplication, QFrame,
    QScrollArea
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QGuiApplication, QFont

DATA_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
LOGO_PATH = os.path.join(DATA_DIR, "logo1.jpg")

MESES_AAAAMM = {
    "Enero": "01", "Febrero": "02", "Marzo": "03", "Abril": "04",
    "Mayo": "05", "Junio": "06", "Julio": "07", "Agosto": "08",
    "Septiembre": "09", "Octubre": "10", "Noviembre": "11", "Diciembre": "12",
}


# ════════════════════════════════════════════════════════════════
# HELPERS DE FORMATO (idénticos al lsd_gui original, aquí como librería)
# ════════════════════════════════════════════════════════════════

def _pad_left(s, length, ch="0") -> str:
    s = "" if s is None else str(s)
    s = s[:length]
    return s.zfill(length) if ch == "0" else s.rjust(length, ch)


def _pad_right(s, length, ch=" ") -> str:
    s = "" if s is None else str(s)
    return s[:length].ljust(length, ch)


def _is_digits(s, n) -> bool:
    return bool(s) and str(s).isdigit() and len(str(s)) == n


def _fmt_decimal(valor_str, total_len: int) -> str:
    """Convierte un importe a entero con 2 decimales implícitos, relleno izquierdo con ceros."""
    try:
        s = str(valor_str).strip().replace(",", ".")
        if "." in s:
            partes = s.split(".")
            entero   = partes[0].lstrip("0") or "0"
            centavos = (partes[1] + "00")[:2]
        else:
            entero   = s.lstrip("0") or "0"
            centavos = "00"
        return _pad_left(entero + centavos, total_len, "0")
    except Exception:
        return "0" * total_len


def _fmt_pct5(valor_str) -> str:
    return _fmt_decimal(valor_str, 5)


# ════════════════════════════════════════════════════════════════
# CONSTRUCTORES DE REGISTROS
# ════════════════════════════════════════════════════════════════

def make_registro_01(cuit: str, periodo: str, ident_envio: str,
                     tipo_liq: str, nro_liq: int | str,
                     cant_reg_04: int) -> str:
    if not _is_digits(cuit, 11):
        raise ValueError("CUIT empresa: debe tener exactamente 11 dígitos.")
    if not _is_digits(periodo, 6):
        raise ValueError("Período: debe tener 6 dígitos (AAAAMM).")
    anio, mes = int(periodo[:4]), int(periodo[4:])
    if anio < 2010 or anio > 2099 or mes < 1 or mes > 12:
        raise ValueError(f"Período {periodo} inválido (AAAAMM, año 2010-2099, mes 01-12).")
    if ident_envio not in ("SJ", "RE"):
        raise ValueError("Identificación de envío debe ser 'SJ' o 'RE'.")

    if ident_envio == "RE":
        tipo_f = " "; nro_f = "00000"; dias_f = "00"
    else:
        if tipo_liq not in ("M", "Q", "D", "H"):
            raise ValueError("Tipo de liquidación debe ser M, Q, D o H.")
        nro = int(nro_liq)
        if not (1 <= nro <= 99999):
            raise ValueError("Número de liquidación debe estar entre 1 y 99999.")
        tipo_f = tipo_liq
        nro_f  = _pad_left(str(nro), 5)
        dias_f = "30"

    rec = ("01" + cuit + ident_envio + periodo + tipo_f
           + nro_f + dias_f + _pad_left(str(cant_reg_04), 6))
    assert len(rec) == 35, f"Reg01 mide {len(rec)} ≠ 35"
    return rec


def make_registro_02(cuil: str, fecha_pago: str, forma_pago: str,
                     legajo: str = "", dependencia: str = "",
                     cbu: str = "", dias_liquidados: str = "0",
                     fecha_rubrica: str = "") -> str:
    if not _is_digits(cuil, 11):
        raise ValueError(f"CUIL {cuil}: debe tener 11 dígitos.")
    if forma_pago not in ("1", "2", "3", "4"):
        raise ValueError("Forma de pago debe ser 1, 2, 3 o 4.")
    if forma_pago == "3" and len(cbu.strip()) != 22:
        raise ValueError(f"CBU debe tener 22 dígitos con pago por acreditación (CUIL {cuil}).")
    if not re.match(r"^\d{8}$", fecha_pago):
        raise ValueError(f"Fecha de pago inválida '{fecha_pago}' (yyyymmdd).")

    dias = max(0, min(999, int(dias_liquidados) if str(dias_liquidados).isdigit() else 0))
    cbu_f    = (_pad_left(cbu.strip(), 22) if forma_pago == "3"
                else _pad_right(cbu.strip(), 22))
    rub_f    = (fecha_rubrica.strip()
                if re.match(r"^\d{8}$", fecha_rubrica.strip()) else "        ")
    rec = ("02" + cuil + _pad_right(legajo, 10) + _pad_right(dependencia, 50)
           + cbu_f + _pad_left(str(dias), 3) + fecha_pago + rub_f + forma_pago)
    assert len(rec) == 115, f"Reg02 mide {len(rec)} ≠ 115"
    return rec


def make_registro_03(cuil: str, cod_concepto: str, cantidad: str,
                     unidad: str, importe: str, debcred: str,
                     periodo_ajuste: str = "000000") -> str:
    if not _is_digits(cuil, 11):
        raise ValueError(f"CUIL {cuil}: debe tener 11 dígitos.")
    if debcred not in ("D", "C"):
        raise ValueError(f"D/C debe ser 'D' o 'C' (CUIL {cuil}, concepto {cod_concepto}).")
    unid_f = unidad if unidad in ("$", "%", "A", "Q", "M", "D", "H", " ") else " "
    per_aj = periodo_ajuste if re.match(r"^\d{6}$", str(periodo_ajuste)) else "000000"
    rec = ("03" + cuil + _pad_right(cod_concepto, 10) + _fmt_decimal(cantidad, 5)
           + unid_f + _fmt_decimal(importe, 15) + debcred + per_aj)
    assert len(rec) == 51, f"Reg03 mide {len(rec)} ≠ 51"
    return rec


def make_registro_04(d: dict) -> str:
    cuil = str(d["cuil"])
    if not _is_digits(cuil, 11):
        raise ValueError(f"CUIL {cuil}: debe tener 11 dígitos.")

    def g(k, default="0"):
        return str(d.get(k, default)).strip() or default

    def gcod(k, length, default="0"):
        val = g(k, default)
        if len(val) > length:
            raise ValueError(f"Campo '{k}' (CUIL {cuil}): '{val}' excede {length} caracteres.")
        return _pad_left(val, length)

    def gi(k):
        return _fmt_decimal(g(k, "0"), 15)

    dias_t = g("dias_trabajados", "30")
    hs_t   = g("horas_trabajadas", "0")
    if int(dias_t or "0") > 0 and int(hs_t or "0") > 0:
        raise ValueError(f"CUIL {cuil}: días ({dias_t}) y horas ({hs_t}) no pueden ser ambos > 0.")

    rec = (
        "04" + cuil
        + ("1" if g("conyuge") in ("1", "S", "s") else "0")
        + _pad_left(g("cant_hijos", "0"), 2)
        + ("1" if g("cct") in ("1", "S", "s") else "0")
        + ("1" if g("scvo") in ("1", "S", "s") else "0")
        + ("1" if g("reduccion") in ("1", "S", "s") else "0")
        + (g("tipo_empresa", "1") if g("tipo_empresa", "1") in
           ("0","1","2","4","5","7","8") else "1")
        + "0"                                          # tipo_operacion fijo
        + gcod("cod_situacion",  2, "01")
        + gcod("cod_condicion",  2, "01")
        + gcod("cod_actividad",  3, "001")
        + gcod("cod_modalidad",  3, "102")
        + gcod("cod_siniestrado",2, "00")
        + gcod("cod_localidad",  2, "00")
        + _pad_left(g("sit_revista_1",  "01"), 2)
        + _pad_left(g("dia_inicio_revista_1", "01"), 2)
        + _pad_left(g("sit_revista_2",  "  "), 2, " ")
        + _pad_left(g("dia_inicio_revista_2","  "), 2, " ")
        + _pad_left(g("sit_revista_3",  "  "), 2, " ")
        + _pad_left(g("dia_inicio_revista_3","  "), 2, " ")
        + _pad_left(dias_t, 2)
        + _pad_left(hs_t,   3)
        + _fmt_pct5(g("aporte_adicional_ss_pct",       "0"))
        + _fmt_pct5(g("contrib_tarea_diferencial_pct", "0"))
        + _pad_left(g("cod_obra_social", "0"), 6)
        + _pad_left(g("cant_adherentes", "0"), 2)
        + gi("aporte_adicional_os")
        + gi("contrib_adicional_os")
        + gi("base_dif_aporte_os_fsr")
        + gi("base_dif_contrib_os_fsr")
        + gi("base_dif_lrt")
        + gi("rem_maternidad")
        + gi("rem_bruta")
        + gi("bi1") + gi("bi2") + gi("bi3") + gi("bi4") + gi("bi5")
        + gi("bi6") + gi("bi7") + gi("bi8") + gi("bi9")
        + gi("base_dif_aporte_ss")
        + gi("base_dif_contrib_ss")
        + gi("bi10")
        + gi("importe_detraer")
    )
    if len(rec) != 370:
        raise ValueError(f"Reg04 (CUIL {cuil}) mide {len(rec)} ≠ 370")
    return rec


def write_txt(path: str, lines: list[str]) -> None:
    """Escribe el archivo con CRLF, encoding latin-1, sin línea vacía final."""
    with open(path, "wb") as f:
        f.write("\r\n".join(lines).encode("latin-1", errors="replace"))


# ════════════════════════════════════════════════════════════════
# MOTOR: CONSTRUIR TXT DESDE UNA LIQUIDACIÓN DE M7
# ════════════════════════════════════════════════════════════════

def calcular_bases_imponibles(calculo: dict, tope: float | None) -> dict:
    """
    Deriva las bases imponibles BI1-BI9 a partir del resultado del liquidador.

    Reglas (CCT 130/75 / lógica general del instructivo ARCA):
      sub_rem  = remunerativo total (basico+antig+asist_rem+hex50+hex100+aguinaldo)
      sub_nr   = no remunerativo total (no_rem+asist_no_rem)
      BI1  = min(sub_rem, tope) si tope, si no sub_rem    — aportes previsionales
      BI2  = sub_rem                                        — contrib. prev. e INSSJyP
      BI3  = sub_rem                                        — FNE, AAFF, RENATRE
      BI4  = min(sub_rem + asist_no_rem + no_rem_base, tope_os) — aportes OS y FSR
             (usamos tope si existe, ya que OS también tiene tope = mismo que SIPA)
      BI5  = BI1                                            — aportes INSSJyP (= BI1)
      BI6  = 0                                              — dif. (no aplica CCT 130)
      BI7  = 0                                              — reg. especiales (ídem)
      BI8  = sub_rem + asist_no_rem + no_rem_base           — contrib. OS y FSR (sin tope)
      BI9  = sub_rem + asist_no_rem + no_rem_base           — LRT (sin tope)
      rem_bruta = sub_rem + sub_nr
    """
    sub_rem       = calculo.get("sub_rem", 0.0)
    asist_no_rem  = calculo.get("asist_no_rem", 0.0)
    no_rem_base   = calculo.get("no_rem_total", 0.0) - asist_no_rem
    sub_nr        = calculo.get("sub_no_rem", 0.0)
    rem_bruta     = sub_rem + sub_nr

    bi1 = min(sub_rem, tope) if tope else sub_rem
    bi4 = min(sub_rem + asist_no_rem + no_rem_base, tope) if tope else (sub_rem + asist_no_rem + no_rem_base)
    bi8 = sub_rem + asist_no_rem + no_rem_base

    return {
        "rem_bruta": rem_bruta,
        "bi1": bi1,
        "bi2": sub_rem,
        "bi3": sub_rem,
        "bi4": bi4,
        "bi5": bi1,
        "bi6": 0.0,
        "bi7": 0.0,
        "bi8": bi8,
        "bi9": bi8,
        "bi10": 0.0,
        "base_dif_aporte_ss":  0.0,
        "base_dif_contrib_ss": 0.0,
        "importe_detraer":     0.0,
        "aporte_adicional_os": 0.0,
        "contrib_adicional_os":0.0,
        "base_dif_aporte_os_fsr":  0.0,
        "base_dif_contrib_os_fsr": 0.0,
        "base_dif_lrt":        0.0,
        "rem_maternidad":      0.0,
    }


def _fmt_importe_str(valor: float) -> str:
    """Convierte float a string con 2 decimales para los constructores de registros."""
    return f"{valor:.2f}"


def build_txt_desde_liquidacion(
    calculo:     dict,          # resultado de M7._calcular() → self._ultimo_calculo
    empleado_m7: dict,          # inputs de M7 (cuil, dias, fecha_pago, etc.)
    nomina:      dict,          # fila de nomina_lsd para este empleado
    empleador:   dict,          # fila de empleador_lsd
    parametros:  list[dict],    # lista de parametros_arca
    tope:        float | None,  # tope ANSeS del período o None
    periodo:     str,           # AAAAMM
    nro_liq:     int,
    fecha_pago:  str,           # yyyymmdd
    aguinaldo:   bool = False,
) -> list[str]:
    """
    Construye las líneas del TXT para un empleado.
    Devuelve: [reg01, reg02, reg03×N, reg04]
    """
    from M8LSDConfig import leer_empleador  # importación tardía para evitar circular

    cuil        = str(empleado_m7.get("cuil", "")).strip()
    dias_liq    = str(int(empleado_m7.get("dias", 30)))
    forma_pago  = nomina.get("forma_pago", "1")
    cbu         = nomina.get("cbu", "")

    # ── Registro 01 ─────────────────────────────────────────
    reg01 = make_registro_01(
        cuit        = empleador["cuit"],
        periodo     = periodo,
        ident_envio = empleador.get("ident_envio", "SJ"),
        tipo_liq    = "M",
        nro_liq     = nro_liq,
        cant_reg_04 = 1,
    )

    # ── Registro 02 ─────────────────────────────────────────
    reg02 = make_registro_02(
        cuil            = cuil,
        fecha_pago      = fecha_pago,
        forma_pago      = forma_pago,
        legajo          = nomina.get("legajo", ""),
        cbu             = cbu,
        dias_liquidados = dias_liq if int(dias_liq) < 30 else "0",
    )

    # ── Registros 03 ────────────────────────────────────────
    # Mapa: key del calculo → cod_empleador en parametros_arca
    mapa_conceptos = {
        "basico_calc":  "BASICO",
        "antiguedad_c": "ANTIG",
        "asist_rem":    "ASIST_R",
        "asist_no_rem": "ASIST_NR",
        "hex50_c":      "HEX50",
        "hex100_c":     "HEX100",
        "aguinaldo_c":  "SAC",
        "jub":          "JUB",
        "ley19032":     "LEY19032",
        "ob_social":    "OSSOCIAL",
        "sec_100":      "SEC100",
        "sec_101":      "SEC101",
        "sindicato":    "SIND",
        "ceclac":       "CECLAC",
    }
    # El no_rem base va separado de asist_no_rem
    no_rem_base = calculo.get("no_rem_total", 0.0) - calculo.get("asist_no_rem", 0.0)
    calculo_ext = dict(calculo)
    calculo_ext["no_rem_base"] = no_rem_base
    mapa_conceptos["no_rem_base"] = "NO_REM"

    # Índice de parámetros por cod_empleador
    param_idx = {p["cod_empleador"]: p for p in parametros}

    regs03 = []
    for calc_key, cod_emp in mapa_conceptos.items():
        valor = calculo_ext.get(calc_key, 0.0)
        if valor == 0.0:
            continue                        # omitir conceptos vacíos
        # No incluir SAC si no se liquidó aguinaldo
        if calc_key == "aguinaldo_c" and not aguinaldo:
            continue

        param = param_idx.get(cod_emp)
        if not param:
            continue

        debcred = param["debcred"]
        regs03.append(make_registro_03(
            cuil          = cuil,
            cod_concepto  = cod_emp,
            cantidad      = "1",
            unidad        = "$",
            importe       = _fmt_importe_str(abs(valor)),
            debcred       = debcred,
        ))

    # ── Registro 04 ─────────────────────────────────────────
    bases = calcular_bases_imponibles(calculo, tope)
    reg04_data = {
        "cuil":             cuil,
        "conyuge":          "0",
        "cant_hijos":       "0",
        "cct":              "1" if nomina.get("cct", 1) else "0",
        "scvo":             "1" if nomina.get("scvo", 1) else "0",
        "reduccion":        "1" if nomina.get("reduccion", 0) else "0",
        "tipo_empresa":     empleador.get("tipo_empresa", "1"),
        "cod_situacion":    nomina.get("cod_situacion",  "01"),
        "cod_condicion":    nomina.get("cod_condicion",  "01"),
        "cod_actividad":    empleador.get("cod_actividad", "001"),
        "cod_modalidad":    empleador.get("cod_modalidad", "102"),
        "cod_siniestrado":  nomina.get("cod_siniestrado", "00"),
        "cod_localidad":    empleador.get("cod_localidad", "00"),
        "sit_revista_1":    "01",
        "dia_inicio_revista_1": "01",
        "sit_revista_2":    "  ",
        "dia_inicio_revista_2": "  ",
        "sit_revista_3":    "  ",
        "dia_inicio_revista_3": "  ",
        "dias_trabajados":  dias_liq if int(dias_liq) < 30 else "30",
        "horas_trabajadas": "0",
        "aporte_adicional_ss_pct":       "0",
        "contrib_tarea_diferencial_pct": "0",
        "cod_obra_social":  nomina.get("cod_obra_social", "000000"),
        "cant_adherentes":  "0",
    }
    for k, v in bases.items():
        reg04_data[k] = _fmt_importe_str(v)

    reg04 = make_registro_04(reg04_data)

    return [reg01, reg02] + regs03 + [reg04]


# ════════════════════════════════════════════════════════════════
# HELPERS UI
# ════════════════════════════════════════════════════════════════

def _icon() -> QIcon:
    return QIcon(LOGO_PATH) if os.path.exists(LOGO_PATH) else QIcon()


def _centrar(w, ancho, alto):
    w.resize(ancho, alto)
    geo = QGuiApplication.primaryScreen().availableGeometry()
    w.move(geo.center().x() - ancho // 2, geo.center().y() - alto // 2)


# ════════════════════════════════════════════════════════════════
# VENTANA DE EXPORTACIÓN
# ════════════════════════════════════════════════════════════════

class VentanaExportLSD(QWidget):
    """
    Ventana que se abre desde M7 después de calcular una liquidación.
    Permite revisar, completar y exportar el TXT al sistema de ARCA.
    """

    def __init__(self, calculo: dict, empleado_m7: dict,
                 nombre_estudio: str = ""):
        super().__init__()
        from M8LSDConfig import (init_db, leer_empleador, leer_nomina,
                                 leer_parametros, leer_tope, guardar_historial)
        init_db()

        self._calculo      = calculo
        self._empleado_m7  = empleado_m7
        self._guardar_hist = guardar_historial
        self._leer_tope    = leer_tope

        self._empleador  = leer_empleador()
        self._nomina     = leer_nomina(solo_activos=True)
        self._parametros = leer_parametros()

        self.setWindowTitle("Exportar al Libro de Sueldos Digital (ARCA)")
        self.setWindowIcon(_icon())
        _centrar(self, 820, 680)

        self._build()
        self._poblar_empleado()
        self._actualizar_preview()

    # ── Construcción de UI ───────────────────────────────────

    def _build(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner  = QWidget()
        main   = QVBoxLayout(inner)
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(12)

        # Encabezado
        titulo = QLabel("📄  Exportar liquidación al LSD — ARCA")
        titulo.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1a5276; padding: 4px 0;"
        )
        main.addWidget(titulo)

        # Advertencia si falta configuración
        emp = self._empleador
        if not emp.get("cuit"):
            warn = QLabel(
                "⚠  El CUIT del empleador no está configurado. "
                "Completá la configuración en M8 antes de generar el TXT."
            )
            warn.setStyleSheet(
                "background:#fff3cd; color:#856404; padding:6px; border-radius:4px;"
            )
            warn.setWordWrap(True)
            main.addWidget(warn)

        # ── Grupo: selección empleado + período ─────────────
        grp_sel = QGroupBox("Empleado y período")
        g = QGridLayout()

        g.addWidget(QLabel("Empleado *:"), 0, 0)
        self.cmb_empleado = QComboBox()
        self.cmb_empleado.setMinimumWidth(260)
        cuil_m7 = str(self._empleado_m7.get("cuil", "")).strip()
        for em in self._nomina:
            self.cmb_empleado.addItem(
                f"{em['apellido_nombre']}  ({em['cuil']})", em["cuil"]
            )
        # Preseleccionar si coincide con M7
        for i in range(self.cmb_empleado.count()):
            if self.cmb_empleado.itemData(i) == cuil_m7:
                self.cmb_empleado.setCurrentIndex(i)
                break
        self.cmb_empleado.currentIndexChanged.connect(self._actualizar_preview)
        g.addWidget(self.cmb_empleado, 0, 1, 1, 3)

        g.addWidget(QLabel("Período (AAAAMM) *:"), 1, 0)
        self.inp_periodo = QLineEdit()
        # Precalcular período del mes del liquidador
        mes_str  = self._empleado_m7.get("mes_nombre", "")
        anio_str = self._empleado_m7.get("anio", "")
        if mes_str and anio_str:
            mm = MESES_AAAAMM.get(mes_str, "")
            self.inp_periodo.setText(f"{anio_str}{mm}")
        else:
            self.inp_periodo.setPlaceholderText("Ej: 202506")
        self.inp_periodo.textChanged.connect(self._actualizar_preview)
        g.addWidget(self.inp_periodo, 1, 1)

        g.addWidget(QLabel("Nro. liquidación *:"), 1, 2)
        self.inp_nro_liq = QLineEdit("1")
        g.addWidget(self.inp_nro_liq, 1, 3)

        g.addWidget(QLabel("Fecha de pago (yyyymmdd) *:"), 2, 0)
        self.inp_fecha_pago = QLineEdit()
        self.inp_fecha_pago.setPlaceholderText("Ej: 20250630")
        # Default: último día del período si está ingresado
        self.inp_fecha_pago.setText(date.today().strftime("%Y%m%d"))
        g.addWidget(self.inp_fecha_pago, 2, 1)

        tope_lbl = QLabel("Tope ANSeS del período:")
        g.addWidget(tope_lbl, 2, 2)
        self.lbl_tope = QLabel("— (sin configurar)")
        self.lbl_tope.setStyleSheet("color: #c0392b; font-style: italic;")
        g.addWidget(self.lbl_tope, 2, 3)

        grp_sel.setLayout(g)
        main.addWidget(grp_sel)

        # ── Preview de conceptos ─────────────────────────────
        grp_prev = QGroupBox("Preview — Conceptos que se incluirán en el TXT")
        lay_prev = QVBoxLayout()

        cols_prev = ["Cód. Empleador", "Descripción", "Importe", "D/C", "Cód. ARCA"]
        self.tbl_prev = QTableWidget()
        self.tbl_prev.setColumnCount(len(cols_prev))
        self.tbl_prev.setHorizontalHeaderLabels(cols_prev)
        self.tbl_prev.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tbl_prev.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tbl_prev.setFixedHeight(260)

        self.lbl_totales = QLabel()
        self.lbl_totales.setStyleSheet("font-size: 12px; padding: 4px 0;")

        lay_prev.addWidget(self.tbl_prev)
        lay_prev.addWidget(self.lbl_totales)
        grp_prev.setLayout(lay_prev)
        main.addWidget(grp_prev)

        # ── Bases imponibles calculadas ───────────────────────
        grp_bi = QGroupBox("Bases Imponibles calculadas automáticamente")
        g_bi   = QGridLayout()
        self.lbl_bi = {}
        bi_labels = [
            ("bi1",      "BI 1 — Aportes previsionales"),
            ("bi2",      "BI 2 — Contrib. prev. e INSSJyP"),
            ("bi3",      "BI 3 — FNE, AAFF, RENATRE"),
            ("bi4",      "BI 4 — Aportes OS y FSR"),
            ("bi5",      "BI 5 — Aportes INSSJyP"),
            ("bi8",      "BI 8 — Contrib. OS y FSR"),
            ("bi9",      "BI 9 — LRT"),
            ("rem_bruta","Remuneración Bruta"),
        ]
        for i, (k, lbl) in enumerate(bi_labels):
            row, col = divmod(i, 2)
            g_bi.addWidget(QLabel(f"{lbl}:"), row, col * 2)
            lbl_val = QLabel("—")
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_val.setStyleSheet("font-weight: bold;")
            self.lbl_bi[k] = lbl_val
            g_bi.addWidget(lbl_val, row, col * 2 + 1)
        grp_bi.setLayout(g_bi)
        main.addWidget(grp_bi)

        # ── Botones ──────────────────────────────────────────
        f_sep = QFrame(); f_sep.setFrameShape(QFrame.Shape.HLine)
        main.addWidget(f_sep)

        btn_row = QHBoxLayout()
        self.btn_generar = QPushButton("💾  Generar TXT y guardar")
        self.btn_generar.setStyleSheet(
            "background:#1a5276; color:white; padding:8px 20px;"
            " border-radius:5px; font-size: 13px;"
        )
        self.btn_generar.clicked.connect(self._generar)

        btn_config = QPushButton("⚙ Ir a Configuración LSD")
        btn_config.clicked.connect(self._abrir_config)
        btn_config.setStyleSheet("color: #1a5276;")

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.close)

        btn_row.addWidget(btn_config)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancelar)
        btn_row.addWidget(self.btn_generar)
        main.addLayout(btn_row)

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def _poblar_empleado(self):
        """Si M7 tiene un CUIL, pre-seleccionar en el combo."""
        cuil = str(self._empleado_m7.get("cuil", "")).strip()
        if cuil:
            for i in range(self.cmb_empleado.count()):
                if self.cmb_empleado.itemData(i) == cuil:
                    self.cmb_empleado.setCurrentIndex(i)
                    return

    def _get_nomina_seleccionada(self) -> dict | None:
        cuil = self.cmb_empleado.currentData()
        for em in self._nomina:
            if em["cuil"] == cuil:
                return em
        return None

    def _actualizar_preview(self):
        """Recalcula el preview de conceptos y bases imponibles."""
        periodo = self.inp_periodo.text().strip()
        tope = None
        if len(periodo) == 6 and periodo.isdigit():
            tope = self._leer_tope(periodo)
            if tope:
                self.lbl_tope.setText(f"${tope:,.2f}")
                self.lbl_tope.setStyleSheet("color: #196f3d; font-weight: bold;")
            else:
                self.lbl_tope.setText("Sin tope configurado — se usará remuneración bruta")
                self.lbl_tope.setStyleSheet("color: #c0392b; font-style: italic;")

        nomina = self._get_nomina_seleccionada()
        if not nomina:
            return

        calculo = self._calculo
        aguinaldo = calculo.get("aguinaldo_c", 0.0) > 0

        # Construir filas del preview
        mapa = {
            "basico_calc":  "BASICO",
            "antiguedad_c": "ANTIG",
            "asist_rem":    "ASIST_R",
            "asist_no_rem": "ASIST_NR",
            "no_rem_base":  "NO_REM",
            "hex50_c":      "HEX50",
            "hex100_c":     "HEX100",
            "aguinaldo_c":  "SAC",
            "jub":          "JUB",
            "ley19032":     "LEY19032",
            "ob_social":    "OSSOCIAL",
            "sec_100":      "SEC100",
            "sec_101":      "SEC101",
            "sindicato":    "SIND",
            "ceclac":       "CECLAC",
        }
        calculo_ext = dict(calculo)
        calculo_ext["no_rem_base"] = (calculo.get("no_rem_total", 0.0)
                                      - calculo.get("asist_no_rem", 0.0))

        param_idx = {p["cod_empleador"]: p for p in self._parametros}
        filas = []
        total_hab = total_desc = 0.0

        for calc_key, cod_emp in mapa.items():
            valor = calculo_ext.get(calc_key, 0.0)
            if valor == 0.0:
                continue
            if calc_key == "aguinaldo_c" and not aguinaldo:
                continue
            param = param_idx.get(cod_emp)
            if not param:
                continue
            filas.append((cod_emp, param["descripcion"],
                          valor, param["debcred"], param["cod_arca"]))
            if param["debcred"] == "C":
                total_hab += valor
            else:
                total_desc += valor

        self.tbl_prev.setRowCount(len(filas))
        colores = {"C": "#e8f5e9", "D": "#fce4ec"}
        from PyQt6.QtGui import QColor
        for ri, (cod, desc, imp, dc, arca) in enumerate(filas):
            vals = [cod, desc, f"${imp:,.2f}", dc, arca]
            for ci, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(QColor(colores.get(dc, "#fff")))
                self.tbl_prev.setItem(ri, ci, item)

        self.lbl_totales.setText(
            f"  Total haberes: <b>${total_hab:,.2f}</b>   |   "
            f"Total descuentos: <b>${total_desc:,.2f}</b>   |   "
            f"Neto estimado: <b>${(total_hab - total_desc):,.2f}</b>"
        )
        self.lbl_totales.setTextFormat(Qt.TextFormat.RichText)

        # Actualizar bases imponibles
        bases = calcular_bases_imponibles(calculo, tope)
        for k, lbl_w in self.lbl_bi.items():
            v = bases.get(k, 0.0)
            lbl_w.setText(f"${v:,.2f}" if v else "—")

    def _generar(self):
        # Validaciones
        if not self._empleador.get("cuit"):
            QMessageBox.warning(self, "Sin configuración",
                "El CUIT del empleador no está configurado.\n"
                "Completá la sección Empleador en la configuración del LSD."); return

        nomina = self._get_nomina_seleccionada()
        if not nomina:
            QMessageBox.warning(self, "Sin empleado",
                "No hay empleados en la nómina. Agregalos en Configuración → Nómina."); return

        periodo = self.inp_periodo.text().strip()
        if len(periodo) != 6 or not periodo.isdigit():
            QMessageBox.warning(self, "Período inválido",
                "El período debe tener 6 dígitos (AAAAMM). Ej: 202506."); return

        fecha_pago = self.inp_fecha_pago.text().strip()
        if not re.match(r"^\d{8}$", fecha_pago):
            QMessageBox.warning(self, "Fecha inválida",
                "La fecha de pago debe tener 8 dígitos (yyyymmdd). Ej: 20250630."); return

        nro_liq_str = self.inp_nro_liq.text().strip()
        try:
            nro_liq = int(nro_liq_str)
            if not (1 <= nro_liq <= 99999):
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Nro. liquidación inválido",
                "El número de liquidación debe ser entre 1 y 99999."); return

        tope = self._leer_tope(periodo)
        aguinaldo = self._calculo.get("aguinaldo_c", 0.0) > 0

        # Construir líneas
        try:
            lines = build_txt_desde_liquidacion(
                calculo     = self._calculo,
                empleado_m7 = {**self._empleado_m7,
                               "cuil": nomina["cuil"]},
                nomina      = nomina,
                empleador   = self._empleador,
                parametros  = self._parametros,
                tope        = tope,
                periodo     = periodo,
                nro_liq     = nro_liq,
                fecha_pago  = fecha_pago,
                aguinaldo   = aguinaldo,
            )
        except (ValueError, AssertionError) as e:
            QMessageBox.critical(self, "Error al construir TXT", str(e)); return

        # Elegir destino
        default_name = (f"LSD_{periodo}_SJ_{nro_liq:05d}_"
                        f"{nomina['cuil']}.txt")
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar TXT — Libro de Sueldos Digital",
            os.path.join(DATA_DIR, default_name),
            "Archivo de texto (*.txt);;Todos los archivos (*.*)",
        )
        if not path:
            return

        try:
            write_txt(path, lines)
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", str(e)); return

        # Guardar historial
        self._guardar_hist(
            cuil    = nomina["cuil"],
            periodo = periodo,
            nro_liq = nro_liq,
            path_txt = path,
            fecha    = datetime.now().strftime("%d/%m/%Y %H:%M"),
        )

        # Resumen
        cant_03 = sum(1 for l in lines if l.startswith("03"))
        QMessageBox.information(self, "TXT generado", (
            f"✔  Archivo guardado en:\n{path}\n\n"
            f"Registros generados:\n"
            f"  01: 1\n"
            f"  02: 1\n"
            f"  03: {cant_03}\n"
            f"  04: 1\n"
            f"  Total líneas: {len(lines)}\n\n"
            f"Encoding: ANSI (latin-1)  ·  Fin de línea: CRLF"
        ))
        self.close()

    def _abrir_config(self):
        from M8LSDConfig import VentanaLSDConfig
        self._cfg_win = VentanaLSDConfig()
        self._cfg_win.show()


if __name__ == "__main__":
    import sys
    # Demo con datos ficticios
    app = QApplication(sys.argv)
    demo_calculo = {
        "basico_calc": 1200000, "antiguedad_c": 60000, "asist_rem": 99996,
        "asist_no_rem": 20832, "no_rem_total": 270832,
        "hex50_c": 0, "hex100_c": 0, "aguinaldo_c": 0,
        "sub_rem": 1359996, "sub_no_rem": 270832,
        "jub": 149599.56, "ley19032": 40799.88, "ob_social": 40799.88,
        "sec_100": 27199.92, "sec_101": 27199.92, "sindicato": 27199.92,
        "ceclac": 700, "sub_desc": 313499.08, "neto": 1317328.92,
    }
    demo_emp = {"cuil": "20123456789", "dias": 30,
                "mes_nombre": "Junio", "anio": "2025"}
    w = VentanaExportLSD(demo_calculo, demo_emp, "Estudio Demo")
    w.show()
    sys.exit(app.exec())
