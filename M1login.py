import sys
import json
import hashlib
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from M2SWorkWindows import VentanaTipoCliente

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
CREDENCIALES_PATH = os.path.join(DATA_DIR, "credenciales.json")
LOGO_PATH = os.path.join(DATA_DIR, "logo1.jpg")

# Credenciales por defecto: usuario "mmac" / contraseña "mmac1234"
# Para cambiarlas, modificar estos valores o implementar un panel de configuración.
DEFAULT_USER = "mmac"
DEFAULT_PASS_HASH = hashlib.sha256("mmac1234".encode()).hexdigest()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class VentanaInicioSesion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Software Contable — MMAC")
        self.setGeometry(200, 200, 320, 240)
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))

        self.usuario_label = QLabel("Usuario:")
        self.usuario_input = QLineEdit()

        self.contrasena_label = QLabel("Contraseña:")
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.recordar_checkbox = QCheckBox("Recordar usuario")
        self.mostrar_checkbox = QCheckBox("Mostrar contraseña")
        self.iniciar_button = QPushButton("Iniciar Sesión")

        layout = QVBoxLayout()
        layout.addWidget(self.usuario_label)
        layout.addWidget(self.usuario_input)
        layout.addWidget(self.contrasena_label)
        layout.addWidget(self.contrasena_input)
        layout.addWidget(self.recordar_checkbox)
        layout.addWidget(self.mostrar_checkbox)
        layout.addWidget(self.iniciar_button)
        self.setLayout(layout)

        self.mostrar_checkbox.stateChanged.connect(self._toggle_echo)
        self.iniciar_button.clicked.connect(self._iniciar_sesion)
        self.contrasena_input.returnPressed.connect(self._iniciar_sesion)

        self._cargar_credenciales()

    # ------------------------------------------------------------------ slots

    def _toggle_echo(self, state):
        # En PyQt6, stateChanged emite un int: 2=checked, 0=unchecked
        modo = QLineEdit.EchoMode.Normal if state == 2 else QLineEdit.EchoMode.Password
        self.contrasena_input.setEchoMode(modo)

    def _iniciar_sesion(self):
        usuario = self.usuario_input.text().strip()
        contrasena = self.contrasena_input.text()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Campos vacíos", "Completá usuario y contraseña.")
            return

        pass_hash = hash_password(contrasena)
        creds = self._leer_credenciales_guardadas()
        usuario_ok = creds.get("usuario", DEFAULT_USER)
        hash_ok = creds.get("hash", DEFAULT_PASS_HASH)

        if usuario == usuario_ok and pass_hash == hash_ok:
            if self.recordar_checkbox.isChecked():
                self._guardar_credenciales(usuario, pass_hash)
            else:
                self._eliminar_credenciales()
            self._abrir_ventana_principal()
        else:
            QMessageBox.warning(self, "Acceso denegado", "Usuario o contraseña incorrectos.")

    def _abrir_ventana_principal(self):
        self.work_window = VentanaTipoCliente()
        self.work_window.show()
        self.close()

    # ---------------------------------------------------------------- helpers

    def _cargar_credenciales(self):
        creds = self._leer_credenciales_guardadas()
        if creds.get("recordar") and creds.get("usuario"):
            self.usuario_input.setText(creds["usuario"])
            self.recordar_checkbox.setChecked(True)

    def _leer_credenciales_guardadas(self) -> dict:
        try:
            with open(CREDENCIALES_PATH, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _guardar_credenciales(self, usuario: str, pass_hash: str):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CREDENCIALES_PATH, "w") as f:
            json.dump({"usuario": usuario, "hash": pass_hash, "recordar": True}, f)

    def _eliminar_credenciales(self):
        if os.path.exists(CREDENCIALES_PATH):
            os.remove(CREDENCIALES_PATH)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaInicioSesion()
    ventana.show()
    sys.exit(app.exec())
