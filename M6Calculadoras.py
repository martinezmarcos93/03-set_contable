import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QComboBox
from PyQt5.QtGui import QIcon, QPixmap


class VentanaCalculadoras(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadoras")
        self.setGeometry(100, 100, 300, 200)
        self.setWindowIcon(QIcon("logo1.jpg"))

        # Botón "Calculadora de netos"
        btn_netos = QPushButton("Calculadora de Netos", self)
        btn_netos.setGeometry(50, 50, 200, 30)
        btn_netos.clicked.connect(self.abrir_ventana_netos)

        # Botón "Calculadora de IVA"
        btn_iva = QPushButton("Calculadora de IVA", self)
        btn_iva.setGeometry(50, 100, 200, 30)
        btn_iva.clicked.connect(self.abrir_ventana_iva)

        # Botón "Calculadora de porcentajes"
        btn_porcentajes = QPushButton("Calculadora de Porcentajes", self)
        btn_porcentajes.setGeometry(50, 150, 200, 30)
        btn_porcentajes.clicked.connect(self.abrir_ventana_porcentajes)

    def abrir_ventana_netos(self):
        self.ventana_netos = VentanaNetos()
        self.ventana_netos.show()

    def abrir_ventana_iva(self):
        self.ventana_iva = VentanaIVA()
        self.ventana_iva.show()

    def abrir_ventana_porcentajes(self):
        self.ventana_porcentajes = VentanaPorcentaje()
        self.ventana_porcentajes.show()


class VentanaNetos(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Netos")
        self.setGeometry(200, 200, 300, 200)

        self.lbl_percepcion = QLabel("Cantidad percibida:", self)
        self.lbl_percepcion.setGeometry(20, 20, 120, 30)
        self.txt_percepcion = QLineEdit(self)
        self.txt_percepcion.setGeometry(150, 20, 120, 30)

        self.lbl_alicuota = QLabel("Alicuota (%):", self)
        self.lbl_alicuota.setGeometry(20, 70, 120, 30)
        self.txt_alicuota = QLineEdit(self)
        self.txt_alicuota.setGeometry(150, 70, 120, 30)

        self.btn_calcular = QPushButton("Calcular", self)
        self.btn_calcular.setGeometry(100, 120, 100, 30)
        self.btn_calcular.clicked.connect(self.calcular_netos)

        self.lbl_resultado = QLabel("", self)
        self.lbl_resultado.setGeometry(20, 170, 260, 30)

    def calcular_netos(self):
        percepcion = float(self.txt_percepcion.text())
        alicuota = float(self.txt_alicuota.text())

        x = (percepcion * 100) / alicuota

        self.lbl_resultado.setText(f"El neto de la percepcion es: {x}")


class VentanaIVA(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de IVA")
        self.setGeometry(200, 200, 300, 250)

        self.lbl_neto = QLabel("Neto:", self)
        self.lbl_neto.setGeometry(20, 20, 80, 30)
        self.txt_neto = QLineEdit(self)
        self.txt_neto.setGeometry(120, 20, 150, 30)

        self.lbl_iva = QLabel("Tipo de IVA:", self)
        self.lbl_iva.setGeometry(20, 70, 80, 30)
        self.combo_iva = QComboBox(self)
        self.combo_iva.setGeometry(120, 70, 150, 30)
        self.combo_iva.addItem("21%")
        self.combo_iva.addItem("27%")
        self.combo_iva.addItem("10.5%")

        self.btn_calcular = QPushButton("Calcular", self)
        self.btn_calcular.setGeometry(100, 120, 100, 30)
        self.btn_calcular.clicked.connect(self.calcular_total)

        self.lbl_total = QLabel("", self)
        self.lbl_total.setGeometry(20, 170, 260, 30)

        self.lbl_resultados = QLabel("", self)
        self.lbl_resultados.setGeometry(20, 210, 260, 60)

    def calcular_total(self):
        neto = float(self.txt_neto.text())
        iva = float(self.combo_iva.currentText().replace("%", ""))

        iva_calculado = (neto * iva) / 100
        total = neto + iva_calculado

        resultado_iva = f"IVA ({iva}%): {iva_calculado}"
        resultado_total = f"Total: {total}"

        self.lbl_resultados.setText(f"{resultado_iva}\n{resultado_total}")

    def calcular_neto(self):
        total = float(self.txt_neto.text())
        iva = float(self.combo_iva.currentText().replace("%", ""))

        neto_calculado = total / (1 + (iva / 100))
        iva_calculado = total - neto_calculado

        resultado_neto = f"Neto: {neto_calculado}"
        resultado_iva = f"IVA ({iva}%): {iva_calculado}"

        self.lbl_resultados.setText(f"{resultado_neto}\n{resultado_iva}")


class VentanaPorcentaje(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculadora de Porcentaje")
        self.setGeometry(200, 200, 300, 250)

        self.lbl_valor_x = QLabel("Valor X:", self)
        self.lbl_valor_x.setGeometry(20, 20, 80, 30)
        self.txt_valor_x = QLineEdit(self)
        self.txt_valor_x.setGeometry(120, 20, 150, 30)

        self.lbl_valor_y = QLabel("Valor Y:", self)
        self.lbl_valor_y.setGeometry(20, 70, 80, 30)
        self.txt_valor_y = QLineEdit(self)
        self.txt_valor_y.setGeometry(120, 70, 150, 30)

        self.btn_porcentaje_x = QPushButton("Calcular % de X", self)
        self.btn_porcentaje_x.setGeometry(20, 120, 250, 30)
        self.btn_porcentaje_x.clicked.connect(self.calcular_porcentaje_x)

        self.btn_porcentaje_y = QPushButton("Calcular % de Y", self)
        self.btn_porcentaje_y.setGeometry(20, 170, 250, 30)
        self.btn_porcentaje_y.clicked.connect(self.calcular_porcentaje_y)

        self.lbl_resultado_x = QLabel("", self)
        self.lbl_resultado_x.setGeometry(20, 220, 260, 30)

        self.lbl_resultado_y = QLabel("", self)
        self.lbl_resultado_y.setGeometry(20, 270, 260, 30)

    def calcular_porcentaje_x(self):
        valor_x = float(self.txt_valor_x.text())
        valor_y = float(self.txt_valor_y.text())

        porcentaje_x = (valor_x * 100) / valor_y

        self.lbl_resultado_x.setText(f"El {porcentaje_x}% de {valor_y} es: {valor_x}")

    def calcular_porcentaje_y(self):
        valor_x = float(self.txt_valor_x.text())
        valor_y = float(self.txt_valor_y.text())

        porcentaje_y = (valor_y * 100) / valor_x

        self.lbl_resultado_y.setText(f"El {porcentaje_y}% de {valor_x} es: {valor_y}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaCalculadoras()
    ventana.show()
    sys.exit(app.exec_())
