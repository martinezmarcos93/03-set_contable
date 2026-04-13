import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
LOGO_PATH = os.path.join(DATA_DIR, "logo1.jpg")


class VentanaTipoCliente(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Software Contable — MMAC")
        self.setGeometry(200, 200, 380, 240)
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))

        titulo = QLabel("MMAC — Marcos Martinez Analista Contable")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-weight: bold; font-size: 13px; padding: 8px 0;")

        self.btn_mono = QPushButton("Panel de Monotributistas")
        self.btn_resp = QPushButton("Panel de Responsables Inscriptos")
        self.btn_calc = QPushButton("Calculadoras")
        self.btn_liq  = QPushButton("Liquidador de Sueldos")

        layout = QVBoxLayout()
        layout.addWidget(titulo)
        layout.addSpacing(8)
        for btn in (self.btn_mono, self.btn_resp, self.btn_calc, self.btn_liq):
            layout.addWidget(btn)
        layout.setContentsMargins(20, 12, 20, 20)
        self.setLayout(layout)

        self.btn_mono.clicked.connect(self._abrir_monotributistas)
        self.btn_resp.clicked.connect(self._abrir_responsables)
        self.btn_calc.clicked.connect(self._abrir_calculadora)
        self.btn_liq.clicked.connect(self._abrir_liquidador)

        self._ventanas = []

    def _abrir_monotributistas(self):
        from M3TablaMono import MainWindow
        v = MainWindow(); v.show(); self._ventanas.append(v)

    def _abrir_responsables(self):
        from M4TablaResp import MainWindowRI
        v = MainWindowRI(
            table_name="estudio_contable_responsables_inscriptos",
            window_title="Responsables Inscriptos — MMAC"
        ); v.show(); self._ventanas.append(v)

    def _abrir_calculadora(self):
        from M6Calculadoras import VentanaCalculadoras
        v = VentanaCalculadoras(); v.show(); self._ventanas.append(v)

    def _abrir_liquidador(self):
        from M7LiquidadorSueldos import VentanaLiquidadorSueldos
        v = VentanaLiquidadorSueldos(); v.show(); self._ventanas.append(v)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaTipoCliente()
    ventana.show()
    sys.exit(app.exec())
