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
DEFAULT_USER = "mmac"
DEFAULT_PASS_HASH = hashlib.sha256("mmac1234".encode()).hexdigest()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


class VentanaInicioSesion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Software Contable — MMAC")
        self.setGeometry(200, 200, 320, 260)
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

        # ── CORRECCIÓN: botón de reset para cuando las credenciales
        # guardadas quedaron corruptas y el login no responde.
        self.reset_button = QPushButton("Restablecer credenciales")
        self.reset_button.setStyleSheet("color: gray; font-size: 10px;")
        self.reset_button.setFlat(True)

        layout = QVBoxLayout()
        layout.addWidget(self.usuario_label)
        layout.addWidget(self.usuario_input)
        layout.addWidget(self.contrasena_label)
        layout.addWidget(self.contrasena_input)
        layout.addWidget(self.recordar_checkbox)
        layout.addWidget(self.mostrar_checkbox)
        layout.addWidget(self.iniciar_button)
        layout.addWidget(self.reset_button)
        self.setLayout(layout)

        self.mostrar_checkbox.stateChanged.connect(self._toggle_echo)
        self.iniciar_button.clicked.connect(self._iniciar_sesion)
        self.contrasena_input.returnPressed.connect(self._iniciar_sesion)
        self.reset_button.clicked.connect(self._reset_credenciales)

        self._cargar_credenciales()

    # ------------------------------------------------------------------ slots

    def _toggle_echo(self, state):
        modo = QLineEdit.EchoMode.Normal if state == 2 else QLineEdit.EchoMode.Password
        self.contrasena_input.setEchoMode(modo)

    def _iniciar_sesion(self):
        usuario = self.usuario_input.text().strip()
        contrasena = self.contrasena_input.text()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Campos vacíos", "Completá usuario y contraseña.")
            return

        pass_hash = hash_password(contrasena)

        # ── CORRECCIÓN PRINCIPAL: leer credenciales guardadas pero validar
        # que el JSON tenga la estructura esperada. Si el archivo existe pero
        # tiene datos inconsistentes (p.ej. hash guardado de una sesión rota),
        # se ignora y se usan los defaults — así el login nunca queda bloqueado
        # por un archivo corrupto.
        creds = self._leer_credenciales_guardadas()
        usuario_ok = creds.get("usuario") or DEFAULT_USER
        hash_ok    = creds.get("hash")    or DEFAULT_PASS_HASH

        # Sanidad extra: si el hash guardado no tiene el largo correcto de
        # SHA-256 (64 hex chars), descartarlo y usar el default.
        if not isinstance(hash_ok, str) or len(hash_ok) != 64:
            hash_ok = DEFAULT_PASS_HASH

        if usuario == usuario_ok and pass_hash == hash_ok:
            if self.recordar_checkbox.isChecked():
                # ── CORRECCIÓN: solo guardar usuario, NO el hash de la
                # contraseña en "recordar". El hash ya está en DEFAULT_PASS_HASH
                # o se valida cada vez. Guardar el hash aquí era la causa de
                # que contraseñas incorrectas "se recordaran" y bloquearan el acceso.
                self._guardar_usuario(usuario)
            else:
                self._eliminar_credenciales()
            self._abrir_ventana_principal()
        else:
            QMessageBox.warning(self, "Acceso denegado", "Usuario o contraseña incorrectos.")

    def _abrir_ventana_principal(self):
        self.work_window = VentanaTipoCliente()
        self.work_window.show()
        self.close()

    def _reset_credenciales(self):
        """Elimina el archivo de credenciales guardadas y limpia los campos.
        Usar cuando el login no responde con usuario/contraseña correctos."""
        self._eliminar_credenciales()
        self.usuario_input.clear()
        self.contrasena_input.clear()
        self.recordar_checkbox.setChecked(False)
        QMessageBox.information(
            self,
            "Credenciales restablecidas",
            "Se eliminaron las credenciales guardadas.\n"
            "Ingresá con usuario: mmac / contraseña: mmac1234"
        )

    # ---------------------------------------------------------------- helpers

    def _cargar_credenciales(self):
        creds = self._leer_credenciales_guardadas()
        if creds.get("recordar") and creds.get("usuario"):
            self.usuario_input.setText(creds["usuario"])
            self.recordar_checkbox.setChecked(True)

    def _leer_credenciales_guardadas(self) -> dict:
        try:
            with open(CREDENCIALES_PATH, "r") as f:
                data = json.load(f)
                # Asegurarse de que sea un dict válido
                return data if isinstance(data, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def _guardar_usuario(self, usuario: str):
        """Guarda solo el nombre de usuario para el autocompletado.
        NO persiste el hash de contraseña para evitar bloqueos por datos corruptos."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CREDENCIALES_PATH, "w") as f:
            json.dump({"usuario": usuario, "recordar": True}, f)

    def _eliminar_credenciales(self):
        if os.path.exists(CREDENCIALES_PATH):
            try:
                os.remove(CREDENCIALES_PATH)
            except OSError:
                pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaInicioSesion()
    ventana.show()
    sys.exit(app.exec())
