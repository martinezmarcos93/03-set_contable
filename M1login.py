import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QCheckBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
import json
from M2SWorkWindows import VentanaTipoCliente



class VentanaInicioSesion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Estudio Contable")
        self.setGeometry(200, 200, 300, 200)
        self.setWindowIcon(QIcon("Data\logo1.jpg"))

        self.usuario_label = QLabel("Usuario:")
        self.usuario_input = QLineEdit()
        self.contrasena_label = QLabel("Contraseña:")
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.recordar_checkbox = QCheckBox("Recordar usuario y contraseña")
        self.mostrar_contrasena_checkbox = QCheckBox("Mostrar contraseña")
        self.iniciar_sesion_button = QPushButton("Iniciar Sesión")

        layout = QVBoxLayout()
        layout.addWidget(self.usuario_label)
        layout.addWidget(self.usuario_input)
        layout.addWidget(self.contrasena_label)
        layout.addWidget(self.contrasena_input)
        layout.addWidget(self.recordar_checkbox)
        layout.addWidget(self.mostrar_contrasena_checkbox)
        layout.addWidget(self.iniciar_sesion_button)

        self.setLayout(layout)

        self.mostrar_contrasena_checkbox.stateChanged.connect(self.mostrar_contrasena)
        self.iniciar_sesion_button.clicked.connect(self.iniciar_sesion)

        # Cargar las credenciales almacenadas
        self.credenciales = self.cargar_credenciales()
        if self.credenciales:
            self.usuario_input.setText(self.credenciales["usuario"])
            self.contrasena_input.setText(self.credenciales["contrasena"])
            self.recordar_checkbox.setChecked(True)

    def mostrar_contrasena(self, state):
        if state == Qt.CheckState.Checked:
            self.contrasena_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.contrasena_input.setEchoMode(QLineEdit.EchoMode.Password)

    def iniciar_sesion(self):
        usuario = self.usuario_input.text()
        contrasena = self.contrasena_input.text()

        # Verificar el usuario y la contraseña
        if usuario == "estudiocristalli" and contrasena == "bacacay1197":
            if self.recordar_checkbox.isChecked():
                # Guardar el usuario y la contraseña
                self.guardar_credenciales(usuario, contrasena)
            else:
                # Eliminar las credenciales almacenadas
                self.eliminar_credenciales()

            # Abrir la siguiente ventana o realizar las acciones necesarias después del inicio de sesión exitoso
            self.show_successful_login_dialog()
        else:
            QMessageBox.warning(self, "Inicio de Sesión", "Usuario o contraseña incorrectos")
    
    def show_successful_login_dialog(self):
        dialog = SuccessfulLoginDialog()
        dialog.accepted.connect(self.open_work_window)
        dialog.exec_()

    def open_work_window(self):
        self.work_window = VentanaTipoCliente()
        self.work_window.show()
        self.close()

    def guardar_credenciales(self, usuario, contrasena):
        credenciales = {
            "usuario": usuario,
            "contrasena": contrasena
        }

        with open("Data\credenciales.json", "w") as archivo:
            json.dump(credenciales, archivo)

    def cargar_credenciales(self):
        try:
            with open("Data\credenciales.json", "r") as archivo:
                credenciales = json.load(archivo)
                return credenciales
        except FileNotFoundError:
            return None

    def eliminar_credenciales(self):
        try:
            with open("Data\credenciales.json", "w") as archivo:
                archivo.write("")
        except FileNotFoundError:
            pass

class SuccessfulLoginDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inicio de Sesión Exitoso")
        self.setText("Inicio de sesión exitoso")
        self.addButton(QMessageBox.StandardButton.Ok)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    ventana_inicio_sesion = VentanaInicioSesion()
    ventana_inicio_sesion.show()

    sys.exit(app.exec())
