import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox,
    QMessageBox, QGroupBox, QFrame, QScrollArea
)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib import colors
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False

DATA_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
LOGO_PATH = os.path.join(DATA_DIR, "logo1.jpg")
PDF_PATH  = os.path.join(DATA_DIR, "liquidacion_sueldo.pdf")

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]

CATEGORIAS = [
    "Administrativo A", "Administrativo B", "Administrativo C",
    "Cajero A", "Cajero B",
    "Repositor", "Maestranza",
    "Otro"
]

OBRAS_SOCIALES = ["O.S.E.C.A.C.", "OSDE", "Swiss Medical", "Galeno", "Otra"]

JORNADAS = ["4", "5", "6", "7", "8"]


# ─────────────────────────────────────────────────────────────
class VentanaLiquidadorSueldos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Liquidador de Sueldos — CCT 130/75 — MMAC")
        self.setGeometry(80, 60, 700, 780)
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        main_layout = QVBoxLayout(inner)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # ── DATOS EMPLEADOR ──────────────────────────────────
        grp_emp = QGroupBox("Datos del empleador")
        g_emp = QGridLayout()
        self.inp = {}
        campos_emp = [
            ("razon_social", "Razón Social / Nombre", 0, 0),
            ("cuit_emp",     "CUIT Empleador",        0, 2),
            ("domicilio",    "Domicilio",             1, 0),
        ]
        for key, lbl, r, c in campos_emp:
            g_emp.addWidget(QLabel(f"{lbl}:"), r, c)
            w = QLineEdit()
            self.inp[key] = w
            span = 3 if key == "domicilio" else 1
            g_emp.addWidget(w, r, c+1, 1, span)
        grp_emp.setLayout(g_emp)

        # ── DATOS EMPLEADO ────────────────────────────────────
        grp_empl = QGroupBox("Datos del empleado")
        g_empl = QGridLayout()

        campos_empl = [
            ("apellido_nombre", "Apellido y Nombre", 0, 0),
            ("cuil",            "CUIL",              0, 2),
            ("legajo",          "Nº Legajo",         1, 0),
            ("fecha_ingreso",   "Fecha de Ingreso",  1, 2),
            ("puesto",          "Puesto",            2, 0),
            ("convenio",        "Convenio",          2, 2),
        ]
        for key, lbl, r, c in campos_empl:
            g_empl.addWidget(QLabel(f"{lbl}:"), r, c)
            w = QLineEdit()
            if key == "convenio":
                w.setText("CCT 130/75")
            self.inp[key] = w
            g_empl.addWidget(w, r, c+1)

        # Categoría
        g_empl.addWidget(QLabel("Categoría:"), 3, 0)
        self.combo_cat = QComboBox()
        self.combo_cat.addItems(CATEGORIAS)
        g_empl.addWidget(self.combo_cat, 3, 1)

        # Obra Social
        g_empl.addWidget(QLabel("Obra Social:"), 3, 2)
        self.combo_os = QComboBox()
        self.combo_os.addItems(OBRAS_SOCIALES)
        g_empl.addWidget(self.combo_os, 3, 3)

        grp_empl.setLayout(g_empl)

        # ── PERIODO / LIQUIDACIÓN ─────────────────────────────
        grp_liq = QGroupBox("Período y valores")
        g_liq = QGridLayout()

        # Año
        g_liq.addWidget(QLabel("Año:"), 0, 0)
        self.combo_anio = QComboBox()
        self.combo_anio.addItems([str(y) for y in range(2020, 2031)])
        self.combo_anio.setCurrentText("2025")
        g_liq.addWidget(self.combo_anio, 0, 1)

        # Mes
        g_liq.addWidget(QLabel("Mes:"), 0, 2)
        self.combo_mes = QComboBox()
        self.combo_mes.addItems(MESES)
        g_liq.addWidget(self.combo_mes, 0, 3)

        # Antigüedad (años)
        g_liq.addWidget(QLabel("Antigüedad (años):"), 1, 0)
        self.inp["antiguedad"] = QLineEdit("0")
        g_liq.addWidget(self.inp["antiguedad"], 1, 1)

        # Jornada
        g_liq.addWidget(QLabel("Jornada (hs/día):"), 1, 2)
        self.combo_jornada = QComboBox()
        self.combo_jornada.addItems(JORNADAS)
        self.combo_jornada.setCurrentText("8")
        g_liq.addWidget(self.combo_jornada, 1, 3)

        # Días trabajados
        g_liq.addWidget(QLabel("Días trabajados:"), 2, 0)
        self.inp["dias"] = QLineEdit("30")
        g_liq.addWidget(self.inp["dias"], 2, 1)

        # Sueldo básico
        g_liq.addWidget(QLabel("Sueldo Básico ($):"), 2, 2)
        self.inp["basico"] = QLineEdit()
        self.inp["basico"].setPlaceholderText("Ej: 1156207")
        g_liq.addWidget(self.inp["basico"], 2, 3)

        # No Remunerativo (Acuerdo)
        g_liq.addWidget(QLabel("No Remunerativo ($):"), 3, 0)
        self.inp["no_rem"] = QLineEdit("0")
        self.inp["no_rem"].setPlaceholderText("Acuerdo / adicional")
        g_liq.addWidget(self.inp["no_rem"], 3, 1)

        # % Sindicato
        g_liq.addWidget(QLabel("% Sindicato:"), 3, 2)
        self.inp["pct_sind"] = QLineEdit("2.0")
        g_liq.addWidget(self.inp["pct_sind"], 3, 3)

        # Horas extras 50%
        g_liq.addWidget(QLabel("Horas extra 50%:"), 4, 0)
        self.inp["hex50"] = QLineEdit("0")
        g_liq.addWidget(self.inp["hex50"], 4, 1)

        # Horas extras 100%
        g_liq.addWidget(QLabel("Horas extra 100%:"), 4, 2)
        self.inp["hex100"] = QLineEdit("0")
        g_liq.addWidget(self.inp["hex100"], 4, 3)

        # Aguinaldo
        g_liq.addWidget(QLabel("Aguinaldo:"), 5, 0)
        self.combo_agui = QComboBox()
        self.combo_agui.addItems(["No", "Sí"])
        g_liq.addWidget(self.combo_agui, 5, 1)

        grp_liq.setLayout(g_liq)

        # ── RESULTADO ─────────────────────────────────────────
        grp_res = QGroupBox("Resultado")
        g_res = QGridLayout()

        self.lbl_res = {}
        conceptos_res = [
            ("basico_calc",   "Básico"),
            ("antiguedad_c",  "Antigüedad"),
            ("asist_rem",     "Asistencia y Puntualidad (rem.)"),
            ("asist_no_rem",  "Asistencia y Puntualidad (no rem.)"),
            ("no_rem_total",  "No Remunerativo total"),
            ("hex50_c",       "Horas extra 50%"),
            ("hex100_c",      "Horas extra 100%"),
            ("aguinaldo_c",   "Aguinaldo"),
            ("sep1",          ""),
            ("sub_rem",       "Sub Total Remunerativo"),
            ("sub_no_rem",    "Sub Total No Remunerativo"),
            ("sep2",          ""),
            ("jub",           "↓ Jubilación 11%"),
            ("ley19032",      "↓ Ley 19.032  3%"),
            ("ob_social",     "↓ Obra Social  3%"),
            ("sec_100",       "↓ S.E.C. Art.100 CCT 130/75  2%"),
            ("sec_101",       "↓ S.E.C. Art.101 CCT 130/75  2%"),
            ("sindicato",     "↓ Cuota Sindical"),
            ("ceclac",        "↓ Aporte Caja CECLAC  $700"),
            ("sep3",          ""),
            ("sub_desc",      "Sub Total Descuentos"),
            ("sep4",          ""),
            ("neto",          "NETO A COBRAR"),
        ]

        for i, (key, lbl) in enumerate(conceptos_res):
            if key.startswith("sep"):
                sep = QFrame()
                sep.setFrameShape(QFrame.Shape.HLine)
                g_res.addWidget(sep, i, 0, 1, 2)
                continue
            g_res.addWidget(QLabel(f"{lbl}:"), i, 0)
            val_lbl = QLabel("—")
            val_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            if key == "neto":
                val_lbl.setStyleSheet(
                    "font-size: 16px; font-weight: bold; color: #1a5276;"
                )
            self.lbl_res[key] = val_lbl
            g_res.addWidget(val_lbl, i, 1)

        grp_res.setLayout(g_res)

        # ── BOTONES ───────────────────────────────────────────
        btn_layout = QHBoxLayout()
        self.btn_calcular = QPushButton("Calcular")
        self.btn_pdf      = QPushButton("Generar PDF")
        self.btn_limpiar  = QPushButton("Limpiar")
        self.btn_pdf.setEnabled(False)

        self.btn_calcular.clicked.connect(self._calcular)
        self.btn_pdf.clicked.connect(self._generar_pdf)
        self.btn_limpiar.clicked.connect(self._limpiar)

        for b in (self.btn_calcular, self.btn_pdf, self.btn_limpiar):
            btn_layout.addWidget(b)

        # ── ARMAR LAYOUT ──────────────────────────────────────
        main_layout.addWidget(grp_emp)
        main_layout.addWidget(grp_empl)
        main_layout.addWidget(grp_liq)
        main_layout.addWidget(grp_res)
        main_layout.addLayout(btn_layout)

        scroll.setWidget(inner)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        # Guardamos resultado para el PDF
        self._ultimo_calculo = None

    # ── helpers ──────────────────────────────────────────────

    def _v(self, key):
        return self.inp[key].text().strip().replace(",", ".")

    def _f(self, key, default=0.0):
        try:
            return float(self._v(key))
        except ValueError:
            return default

    # ── cálculo principal ─────────────────────────────────────
    def _calcular(self):
        basico    = self._f("basico")
        if basico <= 0:
            QMessageBox.warning(self, "Error", "Ingresá el sueldo básico.")
            return

        dias      = self._f("dias", 30)
        antig_yr  = self._f("antiguedad", 0)
        no_rem    = self._f("no_rem", 0)
        pct_sind  = self._f("pct_sind", 2.0)
        hex50     = self._f("hex50", 0)
        hex100    = self._f("hex100", 0)
        jornada   = int(self.combo_jornada.currentText())
        aguinaldo = self.combo_agui.currentText() == "Sí"

        # Proporcional por días
        basico_prop = basico * dias / 30

        # Antigüedad: 1% por año sobre el básico proporcional
        antig_c = basico_prop * antig_yr / 100

        # Asistencia y Puntualidad — 8.33% del básico (rem. y no rem.)
        asist_rem    = basico_prop * 0.0833
        asist_no_rem = no_rem * 0.0833 if no_rem > 0 else 0

        # Horas extras
        valor_hora = basico / 30 / jornada
        hex50_c  = valor_hora * 1.50 * hex50
        hex100_c = valor_hora * 2.00 * hex100

        # Aguinaldo (SAC) = mitad del mejor sueldo mensual / 2
        agui_c = (basico_prop + antig_c + asist_rem) / 2 if aguinaldo else 0

        sub_rem    = basico_prop + antig_c + asist_rem + hex50_c + hex100_c + agui_c
        sub_no_rem = no_rem + asist_no_rem

        # Descuentos sobre remunerativo
        jub_c      = sub_rem * 0.11
        ley19_c    = sub_rem * 0.03
        obs_c      = sub_rem * 0.03
        sec100_c   = sub_rem * 0.02
        sec101_c   = sub_rem * 0.02
        sind_c     = sub_rem * (pct_sind / 100)
        ceclac_c   = 700.0

        sub_desc = jub_c + ley19_c + obs_c + sec100_c + sec101_c + sind_c + ceclac_c
        neto     = sub_rem + sub_no_rem - sub_desc

        # Guardar para PDF
        self._ultimo_calculo = dict(
            basico_calc=basico_prop, antiguedad_c=antig_c,
            asist_rem=asist_rem, asist_no_rem=asist_no_rem,
            no_rem_total=sub_no_rem, hex50_c=hex50_c, hex100_c=hex100_c,
            aguinaldo_c=agui_c,
            sub_rem=sub_rem, sub_no_rem=sub_no_rem,
            jub=jub_c, ley19032=ley19_c, ob_social=obs_c,
            sec_100=sec100_c, sec_101=sec101_c,
            sindicato=sind_c, ceclac=ceclac_c,
            sub_desc=sub_desc, neto=neto
        )

        # Mostrar resultados
        fmt = lambda v: f"${v:>14,.2f}" if v != 0 else "—"
        for key, val in self._ultimo_calculo.items():
            if key in self.lbl_res:
                self.lbl_res[key].setText(fmt(val))

        self.lbl_res["neto"].setText(f"$ {neto:,.2f}")
        self.btn_pdf.setEnabled(True)

    # ── PDF ───────────────────────────────────────────────────
    def _generar_pdf(self):
        if not REPORTLAB_OK:
            QMessageBox.critical(self, "Dependencia faltante",
                "Instalá reportlab:\n  pip install reportlab")
            return
        if self._ultimo_calculo is None:
            QMessageBox.warning(self, "Error", "Calculá primero antes de generar el PDF.")
            return

        os.makedirs(DATA_DIR, exist_ok=True)
        c = rl_canvas.Canvas(PDF_PATH, pagesize=letter)
        W, H = letter

        c.setFont("Helvetica-Bold", 13)
        c.drawString(50, H-50,
            f"RECIBO DE SUELDO — CCT 130/75 Empleados de Comercio")
        c.setFont("Helvetica", 11)

        # Empleador
        c.drawString(50, H-75,  f"Empleador: {self._v('razon_social')}")
        c.drawString(50, H-90,  f"CUIT: {self._v('cuit_emp')}    Domicilio: {self._v('domicilio')}")

        # Periodo
        mes  = self.combo_mes.currentText()
        anio = self.combo_anio.currentText()
        c.drawString(50, H-110, f"Período: {mes} {anio}")
        c.line(50, H-115, W-50, H-115)

        # Empleado
        c.drawString(50, H-130, f"Empleado: {self._v('apellido_nombre')}    CUIL: {self._v('cuil')}")
        c.drawString(50, H-145,
            f"Legajo: {self._v('legajo')}    Ingreso: {self._v('fecha_ingreso')}    "
            f"Puesto: {self._v('puesto')}")
        c.drawString(50, H-160,
            f"Categoría: {self.combo_cat.currentText()}    "
            f"Jornada: {self.combo_jornada.currentText()}hs    "
            f"Obra Social: {self.combo_os.currentText()}")
        c.drawString(50, H-175,
            f"Antigüedad: {self._v('antiguedad')} años    "
            f"Convenio: {self._v('convenio')}    "
            f"Días trabajados: {self._v('dias')}")
        c.line(50, H-180, W-50, H-180)

        # Tabla de conceptos
        c.setFont("Helvetica-Bold", 9)
        cols = [50, 200, 320, 430, 520]
        headers = ["Concepto", "Unidad/Base", "Remunerativo", "No Remunerativo", "Descuentos"]
        y = H - 195
        for hdr, x in zip(headers, cols):
            c.drawString(x, y, hdr)
        c.line(50, y-4, W-50, y-4)

        c.setFont("Helvetica", 9)
        d = self._ultimo_calculo
        filas = [
            ("Básico",                  f"30d",      d["basico_calc"],  0,               0),
            ("Antigüedad",              f"{self._v('antiguedad')}%", d["antiguedad_c"], 0, 0),
            ("Asist. y Puntualidad",    "8.33%",     d["asist_rem"],    d["asist_no_rem"], 0),
            ("No Remunerativo",         "",          0,                 d["no_rem_total"] - d["asist_no_rem"], 0),
            ("Horas extra 50%",         f"{self._v('hex50')}hs", d["hex50_c"], 0, 0),
            ("Horas extra 100%",        f"{self._v('hex100')}hs", d["hex100_c"], 0, 0),
            ("Aguinaldo (SAC)",         "",          d["aguinaldo_c"],  0,               0),
            ("",                        "",          0,                 0,               0),
            ("Jubilación",              "11%",       0,                 0,               d["jub"]),
            ("Ley 19.032",              "3%",        0,                 0,               d["ley19032"]),
            ("Obra Social",             "3%",        0,                 0,               d["ob_social"]),
            ("S.E.C. Art.100 CCT",      "2%",        0,                 0,               d["sec_100"]),
            ("S.E.C. Art.101 CCT",      "2%",        0,                 0,               d["sec_101"]),
            (f"Cuota Sindical",         f"{self._v('pct_sind')}%", 0,  0,               d["sindicato"]),
            ("Aporte Caja CECLAC",      "",          0,                 0,               d["ceclac"]),
        ]

        y -= 14
        for concepto, unidad, rem, no_rem, desc in filas:
            if not concepto:
                continue
            c.drawString(cols[0], y, concepto)
            c.drawString(cols[1], y, unidad)
            if rem:    c.drawRightString(cols[3]-10, y, f"${rem:,.2f}")
            if no_rem: c.drawRightString(cols[4]-10, y, f"${no_rem:,.2f}")
            if desc:   c.drawRightString(cols[4]+75, y, f"${desc:,.2f}")
            y -= 13

        c.line(50, y, W-50, y)
        y -= 12
        c.setFont("Helvetica-Bold", 9)
        c.drawString(cols[0], y, "Sub Totales")
        c.drawRightString(cols[3]-10, y, f"${d['sub_rem']:,.2f}")
        c.drawRightString(cols[4]-10, y, f"${d['sub_no_rem']:,.2f}")
        c.drawRightString(cols[4]+75, y, f"${d['sub_desc']:,.2f}")

        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(cols[0], y, f"NETO  $  {d['neto']:,.2f}")

        # Pie
        c.setFont("Helvetica", 9)
        c.line(50, 120, W-50, 120)
        c.drawString(50, 105,
            "Recibí conforme la suma indicada en concepto de haberes correspondientes al período señalado,")
        c.drawString(50, 93,
            "dejando constancia de haber recibido duplicado del presente recibo.")
        c.drawString(50, 65, "Firma del empleado: ____________________________")
        c.drawString(50, 30, "MMAC — Marcos Martinez Analista Contable")

        c.showPage()
        c.save()

        QMessageBox.information(self, "PDF generado",
            f"Recibo guardado en:\n{PDF_PATH}")

        resp = QMessageBox.question(
            self, "Nueva liquidación", "¿Liquidar otro sueldo?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            self._limpiar()
        else:
            self.close()

    def _limpiar(self):
        for w in self.inp.values():
            w.clear()
        self.inp["dias"].setText("30")
        self.inp["antiguedad"].setText("0")
        self.inp["no_rem"].setText("0")
        self.inp["pct_sind"].setText("2.0")
        self.inp["hex50"].setText("0")
        self.inp["hex100"].setText("0")
        self.inp["convenio"].setText("CCT 130/75")
        for lbl in self.lbl_res.values():
            lbl.setText("—")
        self._ultimo_calculo = None
        self.btn_pdf.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    v = VentanaLiquidadorSueldos()
    v.show()
    sys.exit(app.exec())
