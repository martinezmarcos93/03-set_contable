import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class VentanaLiquidadorSueldos():
    def ejecutar_codigo(self):
        # Obtener los valores ingresados por el usuario desde la interfaz gráfica
        nombre = entrada_nombre.text()
        cuit = entrada_cuit.text()
        domicilio = entrada_domicilio.text()
        legajo = entrada_legajo.text()
        apellido_nombre = entrada_apellido_nombre.text()
        cuil = entrada_cuil.text()
        periodo = entrada_periodo.text()
        convenio = entrada_convenio.text()
        fecha_ingreso = entrada_fecha_ingreso.text()
        sueldo_jornal = float(entrada_sueldo_jornal.text())
        obra_social = entrada_obra_social.text()
        puesto = entrada_puesto.text()
        dias_trabajados = int(entrada_dias_trabajados.text())
        remunerativo = float(entrada_remunerativo.text())

        # Crear el documento PDF
        pdf_filename = 'Data\liquidacion_sueldo.pdf'
        pdf_canvas = canvas.Canvas(pdf_filename, pagesize=letter)

        # Dibujar el encabezado
        pdf_canvas.setFont("Helvetica-Bold", 12)
        pdf_canvas.drawString(50, 750, "NOMBRE: " + nombre)
        pdf_canvas.drawString(50, 730, "CUIT: " + cuit)
        pdf_canvas.drawString(50, 710, "DOMICILIO: " + domicilio)

        # Dibujar las celdas
        pdf_canvas.drawString(50, 680, "Nº Legajo: " + legajo)
        pdf_canvas.drawString(220, 680, "Apellido y Nombre: " + apellido_nombre)
        pdf_canvas.drawString(50, 660, "CUIL: " + cuil)
        pdf_canvas.drawString(220, 660, "Período: " + periodo)
        pdf_canvas.drawString(390, 660, "Convenio: " + convenio)
        pdf_canvas.drawString(50, 640, "Fecha de Ingreso: " + fecha_ingreso)
        pdf_canvas.drawString(220, 640, "Sueldo Jornal: " + str(sueldo_jornal))
        pdf_canvas.drawString(390, 640, "Obra Social: " + obra_social)
        pdf_canvas.drawString(50, 620, "Puesto: " + puesto)

        # Dibujar los encabezados de las columnas
        pdf_canvas.setFont("Helvetica-Bold", 10)
        pdf_canvas.drawString(50, 600, "Nº")
        pdf_canvas.drawString(80, 600, "Concepto")
        pdf_canvas.drawString(200, 600, "Unidad")
        pdf_canvas.drawString(260, 600, "Remunerativo")
        pdf_canvas.drawString(360, 600, "No Remunerativo")
        pdf_canvas.drawString(450, 600, "Descuentos")

        # Dibujar la línea divisoria
        pdf_canvas.line(48, 590, 550, 590)

        # Dibujar las líneas separadoras entre las columnas
        x_positions = [48, 78, 198, 258, 358, 448, 548]  # Coordenadas x de las columnas
        y_top = 610  # Coordenada y de la línea superior
        y_bottom = 350  # Coordenada y de la línea inferior

        for x in x_positions:
            pdf_canvas.line(x, y_top, x, y_bottom)
            
        # Dibujar los conceptos y valores en las columnas
        pdf_canvas.setFont("Helvetica", 10)

        # Dibujar la respuesta del input dias_trabajados en la primera línea de la columna Unidad
        pdf_canvas.drawString(200, 580, str(dias_trabajados))

        # Lista para la columna Nº
        numeros = [
            "10",
            "16",
            "400",
            "410",
            "420"
        ]

        # Dibujar los números
        x_numeros = 50  # Coordenada x para los números
        y_numeros = 580  # Coordenada y inicial para los números

        for numero in numeros:
            pdf_canvas.drawString(x_numeros, y_numeros, numero)
            y_numeros -= 20  # Mover a la siguiente celda

        # Lista de conceptos
        conceptos = [
            "Sueldo básico",
            "Bonif.Asistencia",
            "Jubilación",
            "Ley 19.032",
            "Ob Social",
            "Aporte solid UECARA",
            "Cuota Sindical"
        ]

        # Lista de unidades
        unidades = [
            "   ",
            "10%",
            "11%",
            "3%",
            "3%",
            "1%",
            "2%"
        ]

        # Dibujar los conceptos y unidades
        x_concepto = 85  # Coordenada x para los conceptos
        y_concepto = 580  # Coordenada y inicial para los conceptos
        x_unidad = 200  # Coordenada x para las unidades
        y_unidad = 580  # Coordenada y inicial para las unidades

        for concepto, unidad in zip(conceptos, unidades):
            pdf_canvas.drawString(x_concepto, y_concepto, concepto)
            pdf_canvas.drawString(x_unidad, y_unidad, unidad)
            y_concepto -= 20  # Mover a la siguiente celda
            y_unidad -= 20  # Mover a la siguiente celda
            
        # Dibujar la respuesta del input remunerativo debajo de la columna Remunerativo
        pdf_canvas.drawString(260, 580, str(remunerativo))

        # Calcular los valores de las celdas en la columna No Remunerativo
        bonif_asistencia = remunerativo * 0.10

        # Dibujar los valores en la columna No Remunerativo
        pdf_canvas.drawString(380, 560, f"{bonif_asistencia:.2f}")

        # Calcular los valores de las celdas en la columna Descuentos
        descuentos = [
            remunerativo * 0.11,
            remunerativo * 0.03,
            remunerativo * 0.03,
            remunerativo * 0.01,
            remunerativo * 0.02
        ]

        # Dibujar los valores en la columna Descuentos
        x_descuentos = 450  # Coordenada x para la columna Descuentos
        y_descuentos = 540  # Coordenada y inicial para la columna Descuentos (la altura de "Jubilación")

        for descuento in descuentos:
            pdf_canvas.drawString(x_descuentos, y_descuentos, f"{descuento:.2f}")
            y_descuentos -= 20  # Mover a la siguiente celda

        subtotal_remunerativo = remunerativo
        subtotal_no_remunerativo = bonif_asistencia
        subtotal_descuentos = sum(descuentos)

        sueldo_neto = subtotal_remunerativo - subtotal_descuentos + subtotal_no_remunerativo

        # Agregar los subtotales y el sueldo neto al documento PDF
        pdf_canvas.drawString(50, 340, f"Subtotal Remunerativo: {subtotal_remunerativo:.2f}")
        pdf_canvas.drawString(50, 320, f"Subtotal No remunerativo: {subtotal_no_remunerativo:.2f}")
        pdf_canvas.drawString(50, 300, f"Subtotal Descuentos: {subtotal_descuentos:.2f}")
        pdf_canvas.drawString(50, 280, f"Sueldo Neto: {sueldo_neto:.2f}")

        # Agregar el texto final al documento PDF
        pdf_canvas.drawString(50, 250, "Recibí conforme la suma de pesos: .......... en concepto de haberes correspondientes al período indicado")
        pdf_canvas.drawString(50, 230, "y según la presente liquidación, dejando constancia de haber recibido duplicado de este recibo.")
        pdf_canvas.drawString(50, 90, "ORIGINAL - Firma del empleado")
        pdf_canvas.drawString(50, 30, "Hecho por Marcos Martinez en Estudio Cristalli")

        # Finalizar el documento PDF
        pdf_canvas.showPage()
        pdf_canvas.save()
                
        
        # Dibujar la respuesta del input remunerativo debajo de la columna Remunerativo
        pdf_canvas.drawString(260, 580, str(remunerativo))

        # Calcular los valores de las celdas en la columna No Remunerativo
        bonif_asistencia = remunerativo * 0.10

        # Dibujar los valores en la columna No Remunerativo
        pdf_canvas.drawString(380, 560, f"{bonif_asistencia:.2f}")

        # Calcular los valores de las celdas en la columna Descuentos
        descuentos = [
            remunerativo * 0.11,
            remunerativo * 0.03,
            remunerativo * 0.03,
            remunerativo * 0.01,
            remunerativo * 0.02
        ]

        # Dibujar los valores en la columna Descuentos
        x_descuentos = 450  # Coordenada x para la columna Descuentos
        y_descuentos = 540  # Coordenada y inicial para la columna Descuentos (la altura de "Jubilación")

        for descuento in descuentos:
            pdf_canvas.drawString(x_descuentos, y_descuentos, f"{descuento:.2f}")
            y_descuentos -= 20  # Mover a la siguiente celda

        subtotal_remunerativo = remunerativo
        subtotal_no_remunerativo = bonif_asistencia
        subtotal_descuentos = sum(descuentos)

        sueldo_neto = subtotal_remunerativo - subtotal_descuentos + subtotal_no_remunerativo

        # Agregar los subtotales y el sueldo neto al documento PDF
        pdf_canvas.drawString(50, 340, f"Subtotal Remunerativo: {subtotal_remunerativo:.2f}")
        pdf_canvas.drawString(50, 320, f"Subtotal No remunerativo: {subtotal_no_remunerativo:.2f}")
        pdf_canvas.drawString(50, 300, f"Subtotal Descuentos: {subtotal_descuentos:.2f}")
        pdf_canvas.drawString(50, 280, f"Sueldo Neto: {sueldo_neto:.2f}")

        # Agregar el texto final al documento PDF
        pdf_canvas.drawString(50, 250, "Recibí conforme la suma de pesos: .......... en concepto de haberes correspondientes al período indicado ")
        pdf_canvas.drawString(50, 230," y según la presente liquidación, dejando constancia de haber recibido duplicado de este recibo.")
        pdf_canvas.drawString(50, 90, "ORIGINAL - Firma del empleado")
        pdf_canvas.drawString(50, 30, "Hecho por Marcos Martinez en Estudio Cristalli")
        # Finalizar el documento PDF
        pdf_canvas.showPage()
        pdf_canvas.save()

    def limpiar_campos(self):
        # Restablecer los campos de entrada a su estado inicial
        entrada_nombre.setText("")
        entrada_cuit.setText("")
        entrada_domicilio.setText("")
        entrada_legajo.setText("")
        entrada_apellido_nombre.setText("")
        entrada_cuil.setText("")
        entrada_periodo.setText("")
        entrada_convenio.setText("")
        entrada_fecha_ingreso.setText("")
        entrada_sueldo_jornal.setText("")
        entrada_obra_social.setText("")
        entrada_puesto.setText("")
        entrada_dias_trabajados.setText("")
        entrada_remunerativo.setText("")
                

    def confirmar_liquidacion(self):
        respuesta = QMessageBox.question(ventana, "Confirmación", "¿Desea liquidar otro sueldo?", QMessageBox.Yes | QMessageBox.No)
        if respuesta == QMessageBox.Yes:
            # Limpiar los campos de entrada
            VentanaLiquidadorSueldos.limpiar_campos(self)
            # Mostrar mensaje de éxito
            QMessageBox.information(None, "Éxito", "El cálculo de la liquidación de sueldos se ha completado y el PDF ha sido generado correctamente.")
            # Mostrar un mensaje de éxito
            QMessageBox.information(None, "Éxito", "La liquidación ha sido generada correctamente.")
        else:
            # Cerrar la aplicación
            ventana.close()


# Crear la aplicación y la ventana principal
app = QtWidgets.QApplication(sys.argv)
ventana = QtWidgets.QWidget()
ventana.setWindowTitle("Liquidación de Sueldos")
ventana.setGeometry(100, 100, 500, 500)


# Crear los componentes de la interfaz gráfica
etiqueta_nombre = QtWidgets.QLabel("Nombre:")
entrada_nombre = QtWidgets.QLineEdit()
etiqueta_cuit = QtWidgets.QLabel("CUIT:")
entrada_cuit = QtWidgets.QLineEdit()
etiqueta_domicilio = QtWidgets.QLabel("Domicilio:")
entrada_domicilio = QtWidgets.QLineEdit()
etiqueta_legajo = QtWidgets.QLabel("Nº Legajo:")
entrada_legajo = QtWidgets.QLineEdit()
etiqueta_apellido_nombre = QtWidgets.QLabel("Apellido y Nombre:")
entrada_apellido_nombre = QtWidgets.QLineEdit()
etiqueta_cuil = QtWidgets.QLabel("CUIL:")
entrada_cuil = QtWidgets.QLineEdit()
etiqueta_periodo = QtWidgets.QLabel("Período:")
entrada_periodo = QtWidgets.QLineEdit()
etiqueta_convenio = QtWidgets.QLabel("Convenio:")
entrada_convenio = QtWidgets.QLineEdit()
etiqueta_fecha_ingreso = QtWidgets.QLabel("Fecha de Ingreso:")
entrada_fecha_ingreso = QtWidgets.QLineEdit()
etiqueta_sueldo_jornal = QtWidgets.QLabel("Sueldo Jornal:")
entrada_sueldo_jornal = QtWidgets.QLineEdit()
etiqueta_obra_social = QtWidgets.QLabel("Obra Social:")
entrada_obra_social = QtWidgets.QLineEdit()
etiqueta_puesto = QtWidgets.QLabel("Puesto:")
entrada_puesto = QtWidgets.QLineEdit()
etiqueta_dias_trabajados = QtWidgets.QLabel("Días Trabajados:")
entrada_dias_trabajados = QtWidgets.QLineEdit()
etiqueta_remunerativo = QtWidgets.QLabel("Remunerativo:")
entrada_remunerativo = QtWidgets.QLineEdit()

boton_calcular = QtWidgets.QPushButton("Calcular")
boton_calcular.clicked.connect(VentanaLiquidadorSueldos.confirmar_liquidacion)


# Crear el diseño de la ventana
layout = QtWidgets.QGridLayout()
layout.addWidget(etiqueta_nombre, 0, 0)
layout.addWidget(entrada_nombre, 0, 1)
layout.addWidget(etiqueta_cuit, 0, 2)
layout.addWidget(entrada_cuit, 0, 3)
layout.addWidget(etiqueta_domicilio, 1, 0)
layout.addWidget(entrada_domicilio, 1, 1)
layout.addWidget(etiqueta_legajo, 1, 2)
layout.addWidget(entrada_legajo, 1, 3)
layout.addWidget(etiqueta_apellido_nombre, 2, 0)
layout.addWidget(entrada_apellido_nombre, 2, 1)
layout.addWidget(etiqueta_cuil, 2, 2)
layout.addWidget(entrada_cuil, 2, 3)
layout.addWidget(etiqueta_periodo, 3, 0)
layout.addWidget(entrada_periodo, 3, 1)
layout.addWidget(etiqueta_convenio, 3, 2)
layout.addWidget(entrada_convenio, 3, 3)
layout.addWidget(etiqueta_fecha_ingreso, 4, 0)
layout.addWidget(entrada_fecha_ingreso, 4, 1)
layout.addWidget(etiqueta_sueldo_jornal, 4, 2)
layout.addWidget(entrada_sueldo_jornal, 4, 3)
layout.addWidget(etiqueta_obra_social, 5, 0)
layout.addWidget(entrada_obra_social, 5, 1)
layout.addWidget(etiqueta_puesto, 5, 2)
layout.addWidget(entrada_puesto, 5, 3)
layout.addWidget(etiqueta_dias_trabajados, 6, 0)
layout.addWidget(entrada_dias_trabajados, 6, 1)
layout.addWidget(etiqueta_remunerativo, 6, 2)
layout.addWidget(entrada_remunerativo, 6, 3)
layout.addWidget(boton_calcular, 7, 0, 1, 4)

ventana.setLayout(layout)
ventana.show()

sys.exit(app.exec_())