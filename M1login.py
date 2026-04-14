"""
M1login.py — Pantalla de inicio de sesión
==========================================
Primera ejecución: si no existe Data/credenciales.json, se muestra
un formulario de configuración inicial para definir nombre del estudio,
usuario y contraseña.  No contiene credenciales hardcodeadas.
"""

import sys
import json
import hashlib
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QFormLayout,
    QGroupBox, QMessageBox, QCheckBox
)
from PyQt6.QtGui import QIcon, QGuiApplication

from M2SWorkWindows import VentanaTipoCliente

DATA_DIR          = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
CREDENCIALES_PATH = os.path.join(DATA_DIR, "credenciales.json")
LOGO_PATH         = os.path.join(DATA_DIR, "logo1.jpg")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _icon():
    return QIcon(LOGO_PATH) if os.path.exists(LOGO_PATH) else QIcon()


def _centrar(widget, w, h):
    widget.resize(w, h)
    geo = QGuiApplication.primaryScreen().availableGeometry()
    widget.move(geo.center().x() - w // 2, geo.center().y() - h // 2)


# ─────────────────────────────────────────────────────────────
class VentanaPrimerUso(QWidget):
    """
    Se muestra SOLO la primera vez (cuando no existe credenciales.json).
    El usuario configura nombre del estudio, usuario y contraseña propios.
    No existe ningún valor por defecto — la app no puede usarse sin completar esto.
    """
    def __init__(self, on_complete):
        super().__init__()
        self.on_complete = on_complete
        self.setWindowTitle("Configuración inicial")
        self.setWindowIcon(_icon())
        _centrar(self, 420, 360)

        grp = QGroupBox("Bienvenido — Primera configuración")
        form = QFormLayout()

        self.inp_estudio = QLineEdit()
        self.inp_estudio.setPlaceholderText("Ej: Estudio Contable García")
        form.addRow("Nombre del estudio:", self.inp_estudio)

        self.inp_usuario = QLineEdit()
        self.inp_usuario.setPlaceholderText("Ej: admin")
        form.addRow("Usuario:", self.inp_usuario)

        self.inp_pass1 = QLineEdit()
        self.inp_pass1.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Contraseña:", self.inp_pass1)

        self.inp_pass2 = QLineEdit()
        self.inp_pass2.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Repetir contraseña:", self.inp_pass2)

        grp.setLayout(form)

        lbl_info = QLabel(
            "Estos datos se guardan localmente en Data/credenciales.json.\n"
            "Para cambiarlos, eliminá ese archivo y reiniciá la aplicación."
        )
        lbl_info.setStyleSheet("color: gray; font-size: 10px;")
        lbl_info.setWordWrap(True)

        btn = QPushButton("Guardar y continuar")
        btn.clicked.connect(self._guardar)
        self.inp_pass2.returnPressed.connect(self._guardar)

        layout = QVBoxLayout()
        layout.addWidget(grp)
        layout.addSpacing(6)
        layout.addWidget(lbl_info)
        layout.addSpacing(6)
        layout.addWidget(btn)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

    def _guardar(self):
        estudio = self.inp_estudio.text().strip()
        usuario = self.inp_usuario.text().strip()
        pass1   = self.inp_pass1.text()
        pass2   = self.inp_pass2.text()

        if not estudio:
            QMessageBox.warning(self, "Error", "Ingresá el nombre del estudio."); return
        if not usuario:
            QMessageBox.warning(self, "Error", "Ingresá un nombre de usuario."); return
        if len(pass1) < 6:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 6 caracteres."); return
        if pass1 != pass2:
            QMessageBox.warning(self, "Error", "Las contraseñas no coinciden."); return

        os.makedirs(DATA_DIR, exist_ok=True)
        config = {
            "estudio":  estudio,
            "usuario":  usuario,
            "hash":     hash_password(pass1),
            "recordar": False
        }
        with open(CREDENCIALES_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        QMessageBox.information(self, "Listo", f"Configuración guardada.\nBienvenido, {usuario}.")
        self.close()
        self.on_complete()


# ─────────────────────────────────────────────────────────────
class VentanaInicioSesion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Software Contable")
        self.setWindowIcon(_icon())
        _centrar(self, 320, 270)

        self.usuario_input    = QLineEdit()
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.recordar_checkbox = QCheckBox("Recordar usuario")
        self.mostrar_checkbox  = QCheckBox("Mostrar contraseña")
        self.iniciar_button    = QPushButton("Iniciar Sesión")

        self.reset_button = QPushButton("Restablecer credenciales")
        self.reset_button.setStyleSheet("color: gray; font-size: 10px;")
        self.reset_button.setFlat(True)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Usuario:"))
        layout.addWidget(self.usuario_input)
        layout.addWidget(QLabel("Contraseña:"))
        layout.addWidget(self.contrasena_input)
        layout.addWidget(self.recordar_checkbox)
        layout.addWidget(self.mostrar_checkbox)
        layout.addWidget(self.iniciar_button)
        layout.addWidget(self.reset_button)
        layout.setContentsMargins(24, 24, 24, 24)
        self.setLayout(layout)

        self.mostrar_checkbox.stateChanged.connect(self._toggle_echo)
        self.iniciar_button.clicked.connect(self._iniciar_sesion)
        self.contrasena_input.returnPressed.connect(self._iniciar_sesion)
        self.reset_button.clicked.connect(self._reset_credenciales)

        self._cargar_usuario_recordado()

    def _toggle_echo(self, state):
        modo = QLineEdit.EchoMode.Normal if state == 2 else QLineEdit.EchoMode.Password
        self.contrasena_input.setEchoMode(modo)

    def _iniciar_sesion(self):
        usuario    = self.usuario_input.text().strip()
        contrasena = self.contrasena_input.text()

        if not usuario or not contrasena:
            QMessageBox.warning(self, "Campos vacíos", "Completá usuario y contraseña.")
            return

        creds = self._leer_credenciales()
        if not creds:
            QMessageBox.critical(self, "Error",
                "No hay credenciales configuradas. Reiniciá la aplicación.")
            return

        hash_ok = creds.get("hash", "")
        if not isinstance(hash_ok, str) or len(hash_ok) != 64:
            QMessageBox.critical(self, "Error de configuración",
                "Las credenciales guardadas están corruptas.\n"
                "Usá 'Restablecer credenciales' para reconfigurar.")
            return

        if usuario == creds.get("usuario", "") and hash_password(contrasena) == hash_ok:
            if self.recordar_checkbox.isChecked():
                self._guardar_usuario_recordado(usuario, creds)
            else:
                self._borrar_usuario_recordado(creds)
            self._abrir_ventana_principal(creds.get("estudio", "Software Contable"))
        else:
            QMessageBox.warning(self, "Acceso denegado", "Usuario o contraseña incorrectos.")

    def _abrir_ventana_principal(self, nombre_estudio: str):
        self.work_window = VentanaTipoCliente(nombre_estudio=nombre_estudio)
        self.work_window.show()
        self.close()

    def _reset_credenciales(self):
        confirm = QMessageBox.question(
            self, "Restablecer credenciales",
            "Esto eliminará las credenciales guardadas y te pedirá configurarlas de nuevo.\n¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            if os.path.exists(CREDENCIALES_PATH):
                os.remove(CREDENCIALES_PATH)
            self.close()
            lanzar_app()

    def _cargar_usuario_recordado(self):
        creds = self._leer_credenciales()
        if creds.get("recordar") and creds.get("usuario_recordado"):
            self.usuario_input.setText(creds["usuario_recordado"])
            self.recordar_checkbox.setChecked(True)

    def _leer_credenciales(self) -> dict:
        try:
            with open(CREDENCIALES_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return {}

    def _guardar_usuario_recordado(self, usuario: str, creds: dict):
        creds["recordar"]          = True
        creds["usuario_recordado"] = usuario
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(CREDENCIALES_PATH, "w", encoding="utf-8") as f:
            json.dump(creds, f, ensure_ascii=False, indent=2)

    def _borrar_usuario_recordado(self, creds: dict):
        creds.pop("recordar", None)
        creds.pop("usuario_recordado", None)
        with open(CREDENCIALES_PATH, "w", encoding="utf-8") as f:
            json.dump(creds, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────
def lanzar_app():
    """
    Decide si mostrar la configuración inicial (primer uso)
    o la pantalla de login normal.
    """
    if not os.path.exists(CREDENCIALES_PATH):
        ventana = VentanaPrimerUso(on_complete=lanzar_app)
    else:
        ventana = VentanaInicioSesion()
    ventana.show()
    lanzar_app._ref = ventana   # evitar garbage collection


if __name__ == "__main__":
    app = QApplication(sys.argv)
    lanzar_app()
    sys.exit(app.exec())
