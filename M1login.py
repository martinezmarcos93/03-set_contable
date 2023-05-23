import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QCheckBox
from PyQt6.QtCore import Qt
import sqlite3

class VentanaInicioSesion(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Estudio Contable")
        self.setGeometry(200, 200, 400, 200)

        self.usuario_label = QLabel("Usuario:")
        self.usuario_input = QLineEdit()
        self.contrasena_label = QLabel("Contraseña:")
        self.contrasena_input = QLineEdit()
        self.contrasena_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.recordar_checkbox = QCheckBox("Recordar usuario y contraseña")
        self.iniciar_sesion_button = QPushButton("Iniciar Sesión")

        layout = QVBoxLayout()
        layout.addWidget(self.usuario_label)
        layout.addWidget(self.usuario_input)
        layout.addWidget(self.contrasena_label)
        layout.addWidget(self.contrasena_input)
        layout.addWidget(self.recordar_checkbox)
        layout.addWidget(self.iniciar_sesion_button)

        self.setLayout(layout)

        self.iniciar_sesion_button.clicked.connect(self.iniciar_sesion)

    def iniciar_sesion(self):
        usuario = self.usuario_input.text()
        contrasena = self.contrasena_input.text()

        # Verificar el usuario y la contraseña
        if usuario == "estudiocristalli" and contrasena == "bacacay1197":
            if self.recordar_checkbox.isChecked():
                # Guardar el usuario y la contraseña en la base de datos
                guardar_credenciales(usuario, contrasena)

            # Abrir la siguiente ventana o realizar las acciones necesarias después del inicio de sesión exitoso
            QMessageBox.information(self, "Inicio de Sesión", "Inicio de sesión exitoso")
        else:
            QMessageBox.warning(self, "Inicio de Sesión", "Usuario o contraseña incorrectos")

def guardar_credenciales(usuario, contrasena):
    # Conexión a la base de datos
    conexion = sqlite3.connect("datos_usuarios.db")
    cursor = conexion.cursor()

    # Crear la tabla si no existe
    cursor.execute("CREATE TABLE IF NOT EXISTS usuarios (usuario TEXT, contrasena TEXT)")

    # Verificar si el usuario ya existe en la base de datos
    cursor.execute("SELECT * FROM usuarios WHERE usuario=?", (usuario,))
    resultado = cursor.fetchone()
    if resultado:
        # Actualizar el registro existente
        cursor.execute("UPDATE usuarios SET contrasena=? WHERE usuario=?", (contrasena, usuario))
    else:
        # Insertar un nuevo registro
        cursor.execute("INSERT INTO usuarios VALUES (?, ?)", (usuario, contrasena))

    # Guardar los cambios y cerrar la conexión
    conexion.commit()
    conexion.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    ventana_inicio_sesion = VentanaInicioSesion()
    ventana_inicio_sesion.show()

    sys.exit(app.exec())
