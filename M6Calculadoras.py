import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QPushButton, QLineEdit,
    QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QTabWidget
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

DATA_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
LOGO_PATH = os.path.join(DATA_DIR, "logo1.jpg")


def _icon():
    return QIcon(LOGO_PATH) if os.path.exists(LOGO_PATH) else QIcon()


def _resultado_label():
    lbl = QLabel("")
    lbl.setStyleSheet("font-weight: bold; color: #1a5276; padding: 6px 0;")
    lbl.setWordWrap(True)
    return lbl


def _safe_float(text):
    return float(text.strip().replace(",", ".").replace(" ", ""))


# ══════════════════════════════════════════════════════════════
class TabIVA(QWidget):
    """IVA y alícuotas — calcula neto→total, total→neto,
    percepción→neto base, y el nuevo: monto IVA → neto base."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # ── Neto → Total ──────────────────────────────────────
        grp1 = QGroupBox("Neto → Total con IVA")
        g1 = QGridLayout()
        g1.addWidget(QLabel("Neto ($):"), 0, 0)
        self.txt_neto_in = QLineEdit()
        g1.addWidget(self.txt_neto_in, 0, 1)
        g1.addWidget(QLabel("Alícuota IVA:"), 1, 0)
        self.combo_iva1 = QComboBox()
        self.combo_iva1.addItems(["21%", "27%", "10.5%", "Otro..."])
        self.combo_iva1.currentTextChanged.connect(self._toggle_otro1)
        g1.addWidget(self.combo_iva1, 1, 1)
        self.txt_otro1 = QLineEdit()
        self.txt_otro1.setPlaceholderText("% personalizado")
        self.txt_otro1.hide()
        g1.addWidget(self.txt_otro1, 2, 1)
        btn1 = QPushButton("Calcular")
        btn1.clicked.connect(self._neto_a_total)
        g1.addWidget(btn1, 3, 0, 1, 2)
        self.res1 = _resultado_label()
        g1.addWidget(self.res1, 4, 0, 1, 2)
        grp1.setLayout(g1)

        # ── Total → Neto ──────────────────────────────────────
        grp2 = QGroupBox("Total → Neto (descontar IVA)")
        g2 = QGridLayout()
        g2.addWidget(QLabel("Total ($):"), 0, 0)
        self.txt_total_in = QLineEdit()
        g2.addWidget(self.txt_total_in, 0, 1)
        g2.addWidget(QLabel("Alícuota IVA:"), 1, 0)
        self.combo_iva2 = QComboBox()
        self.combo_iva2.addItems(["21%", "27%", "10.5%", "Otro..."])
        self.combo_iva2.currentTextChanged.connect(self._toggle_otro2)
        g2.addWidget(self.combo_iva2, 1, 1)
        self.txt_otro2 = QLineEdit()
        self.txt_otro2.setPlaceholderText("% personalizado")
        self.txt_otro2.hide()
        g2.addWidget(self.txt_otro2, 2, 1)
        btn2 = QPushButton("Calcular")
        btn2.clicked.connect(self._total_a_neto)
        g2.addWidget(btn2, 3, 0, 1, 2)
        self.res2 = _resultado_label()
        g2.addWidget(self.res2, 4, 0, 1, 2)
        grp2.setLayout(g2)

        # ── IVA → Neto base (NUEVA FUNCIÓN) ──────────────────
        # Caso de uso: tenés el monto del IVA discriminado en una factura
        # y necesitás saber cuál es el neto que lo generó.
        # Fórmula: Neto = Monto_IVA / (alícuota / 100)
        grp_iva_neto = QGroupBox("Monto de IVA → Neto base")
        g_in = QGridLayout()
        g_in.addWidget(QLabel("Monto del IVA ($):"), 0, 0)
        self.txt_iva_monto = QLineEdit()
        self.txt_iva_monto.setPlaceholderText("Ej: 2100")
        g_in.addWidget(self.txt_iva_monto, 0, 1)
        g_in.addWidget(QLabel("Alícuota IVA:"), 1, 0)
        self.combo_iva_n = QComboBox()
        self.combo_iva_n.addItems(["21%", "27%", "10.5%", "Otro..."])
        self.combo_iva_n.currentTextChanged.connect(self._toggle_otro_iva_n)
        g_in.addWidget(self.combo_iva_n, 1, 1)
        self.txt_otro_iva_n = QLineEdit()
        self.txt_otro_iva_n.setPlaceholderText("% personalizado")
        self.txt_otro_iva_n.hide()
        g_in.addWidget(self.txt_otro_iva_n, 2, 1)
        btn_in = QPushButton("Calcular")
        btn_in.clicked.connect(self._iva_a_neto)
        g_in.addWidget(btn_in, 3, 0, 1, 2)
        self.res_iva_neto = _resultado_label()
        g_in.addWidget(self.res_iva_neto, 4, 0, 1, 2)
        grp_iva_neto.setLayout(g_in)

        # ── Percepción → Neto ─────────────────────────────────
        grp3 = QGroupBox("Percepción → Neto base")
        g3 = QGridLayout()
        g3.addWidget(QLabel("Monto percepción ($):"), 0, 0)
        self.txt_perc = QLineEdit()
        g3.addWidget(self.txt_perc, 0, 1)
        g3.addWidget(QLabel("Alícuota (%):"), 1, 0)
        self.txt_alic = QLineEdit()
        g3.addWidget(self.txt_alic, 1, 1)
        btn3 = QPushButton("Calcular")
        btn3.clicked.connect(self._percepcion_neto)
        g3.addWidget(btn3, 2, 0, 1, 2)
        self.res3 = _resultado_label()
        g3.addWidget(self.res3, 3, 0, 1, 2)
        grp3.setLayout(g3)

        layout.addWidget(grp1)
        layout.addWidget(grp2)
        layout.addWidget(grp_iva_neto)
        layout.addWidget(grp3)
        layout.addStretch()
        self.setLayout(layout)

    def _get_iva(self, combo, txt_otro):
        t = combo.currentText()
        if t == "Otro...":
            return _safe_float(txt_otro.text())
        return _safe_float(t.replace("%", ""))

    def _toggle_otro1(self, t):
        self.txt_otro1.setVisible(t == "Otro...")

    def _toggle_otro2(self, t):
        self.txt_otro2.setVisible(t == "Otro...")

    def _toggle_otro_iva_n(self, t):
        self.txt_otro_iva_n.setVisible(t == "Otro...")

    def _neto_a_total(self):
        try:
            neto = _safe_float(self.txt_neto_in.text())
            iva  = self._get_iva(self.combo_iva1, self.txt_otro1)
            iva_monto = neto * iva / 100
            total = neto + iva_monto
            self.res1.setText(
                f"IVA ({iva}%):  ${iva_monto:,.2f}\n"
                f"Total:         ${total:,.2f}"
            )
        except Exception:
            self.res1.setText("Ingresá valores numéricos válidos.")

    def _total_a_neto(self):
        try:
            total = _safe_float(self.txt_total_in.text())
            iva   = self._get_iva(self.combo_iva2, self.txt_otro2)
            neto  = total / (1 + iva / 100)
            iva_monto = total - neto
            self.res2.setText(
                f"Neto:          ${neto:,.2f}\n"
                f"IVA ({iva}%):  ${iva_monto:,.2f}"
            )
        except Exception:
            self.res2.setText("Ingresá valores numéricos válidos.")

    def _iva_a_neto(self):
        """Dado el MONTO del IVA y la alícuota, calcula el neto que lo generó.
        Ejemplo: IVA = $2100 con alícuota 21% → Neto = 2100 / 0.21 = $10.000
        También muestra el total (neto + IVA) como verificación."""
        try:
            iva_monto = _safe_float(self.txt_iva_monto.text())
            iva = self._get_iva(self.combo_iva_n, self.txt_otro_iva_n)
            if iva == 0:
                self.res_iva_neto.setText("La alícuota no puede ser 0.")
                return
            neto  = iva_monto / (iva / 100)
            total = neto + iva_monto
            self.res_iva_neto.setText(
                f"Neto base:     ${neto:,.2f}\n"
                f"IVA ({iva}%):  ${iva_monto:,.2f}\n"
                f"Total:         ${total:,.2f}"
            )
        except Exception:
            self.res_iva_neto.setText("Ingresá valores numéricos válidos.")

    def _percepcion_neto(self):
        try:
            perc  = _safe_float(self.txt_perc.text())
            alic  = _safe_float(self.txt_alic.text())
            if alic == 0:
                self.res3.setText("La alícuota no puede ser 0.")
                return
            neto = perc / (alic / 100)
            self.res3.setText(f"Neto base: ${neto:,.2f}")
        except Exception:
            self.res3.setText("Ingresá valores numéricos válidos.")


# ══════════════════════════════════════════════════════════════
class TabPorcentajes(QWidget):
    """Todas las operaciones de porcentaje útiles."""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        calcs = [
            ("¿Qué % es A de B?",
             ["Valor A", "Total B"],
             self._que_pct_es_a_de_b),
            ("¿Cuánto es el X% de A?",
             ["Porcentaje X (%)", "Valor A"],
             self._cuanto_es_xpct_de_a),
            ("A se eleva / descuenta un B% → resultado",
             ["Valor A", "B (%)  [positivo=sube, negativo=baja]"],
             self._a_sube_baja_b),
            ("¿Cuánto % creció/bajó A respecto a B?",
             ["Valor anterior B", "Valor nuevo A"],
             self._variacion),
            ("X es el resultado de subir A un B% → A original",
             ["Resultado X", "B (%) que se subió"],
             self._deshacer_aumento),
        ]

        for titulo, labels, fn in calcs:
            grp = QGroupBox(titulo)
            g = QGridLayout()
            inputs = []
            for i, lbl in enumerate(labels):
                g.addWidget(QLabel(f"{lbl}:"), i, 0)
                inp = QLineEdit()
                inputs.append(inp)
                g.addWidget(inp, i, 1)
            res = _resultado_label()
            btn = QPushButton("Calcular")
            btn.clicked.connect(lambda checked, f=fn, ins=inputs, r=res: f(ins, r))
            g.addWidget(btn, len(labels), 0, 1, 2)
            g.addWidget(res, len(labels)+1, 0, 1, 2)
            grp.setLayout(g)
            layout.addWidget(grp)

        layout.addStretch()
        self.setLayout(layout)

    def _que_pct_es_a_de_b(self, ins, res):
        try:
            a = _safe_float(ins[0].text())
            b = _safe_float(ins[1].text())
            if b == 0: res.setText("B no puede ser 0."); return
            res.setText(f"{a:,.2f} es el {(a/b*100):.4f}% de {b:,.2f}")
        except Exception:
            res.setText("Ingresá valores numéricos válidos.")

    def _cuanto_es_xpct_de_a(self, ins, res):
        try:
            x = _safe_float(ins[0].text())
            a = _safe_float(ins[1].text())
            res.setText(f"El {x}% de {a:,.2f} = {a*x/100:,.2f}")
        except Exception:
            res.setText("Ingresá valores numéricos válidos.")

    def _a_sube_baja_b(self, ins, res):
        try:
            a = _safe_float(ins[0].text())
            b = _safe_float(ins[1].text())
            resultado = a * (1 + b/100)
            accion = "sube" if b >= 0 else "baja"
            res.setText(
                f"{a:,.2f} {accion} un {abs(b)}% → ${resultado:,.2f}\n"
                f"Diferencia: ${resultado-a:,.2f}"
            )
        except Exception:
            res.setText("Ingresá valores numéricos válidos.")

    def _variacion(self, ins, res):
        try:
            b = _safe_float(ins[0].text())
            a = _safe_float(ins[1].text())
            if b == 0: res.setText("Valor anterior no puede ser 0."); return
            pct = (a - b) / b * 100
            signo = "▲ subió" if pct >= 0 else "▼ bajó"
            res.setText(f"{signo} un {abs(pct):.4f}%  ({b:,.2f} → {a:,.2f})")
        except Exception:
            res.setText("Ingresá valores numéricos válidos.")

    def _deshacer_aumento(self, ins, res):
        try:
            x = _safe_float(ins[0].text())
            b = _safe_float(ins[1].text())
            original = x / (1 + b/100)
            res.setText(
                f"Valor original (antes de +{b}%): ${original:,.2f}\n"
                f"El aumento fue: ${x-original:,.2f}"
            )
        except Exception:
            res.setText("Ingresá valores numéricos válidos.")


# ══════════════════════════════════════════════════════════════
class VentanaCalculadoras(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadoras — MMAC")
        self.setGeometry(100, 100, 520, 780)
        self.setWindowIcon(_icon())

        tabs = QTabWidget()
        tabs.addTab(TabIVA(),         "IVA y Alícuotas")
        tabs.addTab(TabPorcentajes(), "Porcentajes")

        self.setCentralWidget(tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    v = VentanaCalculadoras()
    v.show()
    sys.exit(app.exec())
