import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt6.QtGui import QIcon, QPixmap

class VentanaTipoCliente(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tipo de cliente")
        self.setGeometry(200, 200, 400, 200)
        self.setWindowIcon(QIcon("logo1.jpg"))

        self.monotributistas_button = QPushButton("Monotributistas")
        self.responsables_button = QPushButton("Responsables Inscriptos")
        self.automotor_button = QPushButton("Automotor")  # Nuevo botón

        layout = QVBoxLayout()
        layout.addWidget(self.monotributistas_button)
        layout.addWidget(self.responsables_button)
        layout.addWidget(self.automotor_button)  # Agregar el nuevo botón al diseño

        self.setLayout(layout)

        self.monotributistas_button.clicked.connect(self.abrir_ventana_monotributistas)
        self.responsables_button.clicked.connect(self.abrir_ventana_responsables)
        self.automotor_button.clicked.connect(self.abrir_ventana_automotor)  # Conectar la señal del nuevo botón

    def abrir_ventana_monotributistas(self):
        # Aquí puedes agregar la lógica para abrir la ventana específica para los monotributistas
        print("Ventana para Monotributistas")

    def abrir_ventana_responsables(self):
        # Aquí puedes agregar la lógica para abrir la ventana específica para los responsables inscriptos
        print("Ventana para Responsables Inscriptos")

    def abrir_ventana_automotor(self):
        # Aquí puedes agregar la lógica para abrir la ventana específica para el automotor
        print("Ventana para Automotor")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    ventana_tipo_cliente = VentanaTipoCliente()
    ventana_tipo_cliente.show()

    sys.exit(app.exec())
