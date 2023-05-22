import tkinter as tk
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def ejecutar_codigo():
    # Aquí va el código existente que deseas ejecutar
    # Asegúrate de adaptarlo para utilizar las respuestas ingresadas por el usuario
    # Crear el documento PDF
    pdf_filename = "liquidacion_sueldos.pdf"
    pdf_canvas = canvas.Canvas(pdf_filename, pagesize=letter)
    
    # Obtener los valores ingresados por el usuario desde la interfaz gráfica
    nombre = entrada_nombre.get()
    cuit = entrada_cuit.get()
    domicilio = entrada_domicilio.get()
    legajo = entrada_legajo.get()
    apellido_nombre = entrada_apellido_nombre.get()
    cuil = entrada_cuil.get()
    periodo = entrada_periodo.get()
    convenio = entrada_convenio.get()
    fecha_ingreso = entrada_fecha_ingreso.get()
    sueldo_jornal = float(entrada_sueldo_jornal.get())
    obra_social = entrada_obra_social.get()
    puesto = entrada_puesto.get()
    dias_trabajados = int(entrada_dias_trabajados.get())
    remunerativo = float(entrada_remunerativo.get())

    # Solicitar los demás datos necesarios y almacenarlos en variables correspondientes
    #nombre = input("Ingrese el nombre: ")
    #cuit = input("Ingrese el CUIT: ")
    #domicilio = input("Ingrese el domicilio: ")
    #legajo = input("Ingrese el número de legajo: ")
    #apellido_nombre = input("Ingrese el apellido y nombre: ")
    #cuil = input("Ingrese el CUIL: ")
    #periodo = input("Ingrese el período: ")
    #convenio = input("Ingrese el convenio: ")
    #fecha_ingreso = input("Ingrese la fecha de ingreso: ")
    #sueldo_jornal = float(input("Ingrese el sueldo jornal: "))
    #obra_social = input("Ingrese la obra social: ")
    #puesto = input("Ingrese el puesto: ")
    #dias_trabajados = int(input("Ingrese los días trabajados: "))
    #remunerativo = float(input("Ingrese el valor remunerativo: "))

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
    pdf_canvas.drawString(50, 250, "Recibí conforme la suma de pesos: .......... en concepto de haberes correspondientes al período indicado ")
    pdf_canvas.drawString(50, 230," y según la presente liquidación, dejando constancia de haber recibido duplicado de este recibo.")
    pdf_canvas.drawString(50, 90, "ORIGINAL - Firma del empleado")
    pdf_canvas.drawString(50, 30, "Hecho por Marcos Martinez en Estudio Cristalli")
    # Finalizar el documento PDF
    pdf_canvas.showPage()
    pdf_canvas.save()



# Mostrar un mensaje de éxito
    messagebox.showinfo("Éxito", "La liquidación ha sido generada correctamente.")

    # Limpiar los campos de entrada
    limpiar_campos()

    # Preguntar si se desea realizar otra liquidación
    confirmar_liquidacion()

def limpiar_campos():
    # Restablecer los campos de entrada a su estado inicial
    entrada_nombre.delete(0, tk.END)
    entrada_cuit.delete(0, tk.END)
    entrada_domicilio.delete(0, tk.END)
    entrada_legajo.delete(0, tk.END)
    entrada_apellido_nombre.delete(0, tk.END)
    entrada_cuil.delete(0, tk.END)
    entrada_periodo.delete(0, tk.END)
    entrada_convenio.delete(0, tk.END)
    entrada_fecha_ingreso.delete(0, tk.END)
    entrada_sueldo_jornal.delete(0, tk.END)
    entrada_obra_social.delete(0, tk.END)
    entrada_puesto.delete(0, tk.END)
    entrada_dias_trabajados.delete(0, tk.END)
    entrada_remunerativo.delete(0, tk.END)

def confirmar_liquidacion():
    respuesta = messagebox.askyesno("Confirmación", "¿Desea liquidar otro sueldo?")
    if respuesta:
        # Limpiar los campos de entrada
        limpiar_campos()
    else:
        # Cerrar la aplicación
        ventana.destroy()



# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Liquidador de Sueldos")

# Etiquetas y campos de entrada para las preguntas
etiqueta_nombre = tk.Label(ventana, text="Nombre:")
etiqueta_nombre.grid(row=0, column=0, padx=10, pady=5)
entrada_nombre = tk.Entry(ventana)
entrada_nombre.grid(row=0, column=1)

etiqueta_cuit = tk.Label(ventana, text="CUIT:")
etiqueta_cuit.grid(row=1, column=0, padx=10, pady=5)
entrada_cuit = tk.Entry(ventana)
entrada_cuit.grid(row=1, column=1)

etiqueta_domicilio = tk.Label(ventana, text="Domicilio:")
etiqueta_domicilio.grid(row=2, column=0, padx=10, pady=5)
entrada_domicilio = tk.Entry(ventana)
entrada_domicilio.grid(row=2, column=1)

etiqueta_legajo = tk.Label(ventana, text="Número de legajo:")
etiqueta_legajo.grid(row=3, column=0, padx=10, pady=5)
entrada_legajo = tk.Entry(ventana)
entrada_legajo.grid(row=3, column=1)

etiqueta_apellido_nombre = tk.Label(ventana, text="Apellido y Nombre:")
etiqueta_apellido_nombre.grid(row=4, column=0, padx=10, pady=5)
entrada_apellido_nombre = tk.Entry(ventana)
entrada_apellido_nombre.grid(row=4, column=1)

etiqueta_cuil = tk.Label(ventana, text="CUIL:")
etiqueta_cuil.grid(row=5, column=0, padx=10, pady=5)
entrada_cuil = tk.Entry(ventana)
entrada_cuil.grid(row=5, column=1)

etiqueta_periodo = tk.Label(ventana, text="Período:")
etiqueta_periodo.grid(row=6, column=0, padx=10, pady=5)
entrada_periodo = tk.Entry(ventana)
entrada_periodo.grid(row=6, column=1)

etiqueta_convenio = tk.Label(ventana, text="Convenio:")
etiqueta_convenio.grid(row=7, column=0, padx=10, pady=5)
entrada_convenio = tk.Entry(ventana)
entrada_convenio.grid(row=7, column=1)

etiqueta_fecha_ingreso = tk.Label(ventana, text="Fecha de ingreso:")
etiqueta_fecha_ingreso.grid(row=8, column=0, padx=10, pady=5)
entrada_fecha_ingreso = tk.Entry(ventana)
entrada_fecha_ingreso.grid(row=8, column=1)

etiqueta_sueldo_jornal = tk.Label(ventana, text="Sueldo jornal:")
etiqueta_sueldo_jornal.grid(row=9, column=0, padx=10, pady=5)
entrada_sueldo_jornal = tk.Entry(ventana)
entrada_sueldo_jornal.grid(row=9, column=1)

etiqueta_obra_social = tk.Label(ventana, text="Obra social:")
etiqueta_obra_social.grid(row=10, column=0, padx=10, pady=5)
entrada_obra_social = tk.Entry(ventana)
entrada_obra_social.grid(row=10, column=1)

etiqueta_puesto = tk.Label(ventana, text="Puesto:")
etiqueta_puesto.grid(row=11, column=0, padx=10, pady=5)
entrada_puesto = tk.Entry(ventana)
entrada_puesto.grid(row=11, column=1)

etiqueta_dias_trabajados = tk.Label(ventana, text="Días trabajados:")
etiqueta_dias_trabajados.grid(row=12, column=0, padx=10, pady=5)
entrada_dias_trabajados = tk.Entry(ventana)
entrada_dias_trabajados.grid(row=12, column=1)

etiqueta_remunerativo = tk.Label(ventana, text="Valor remunerativo:")
etiqueta_remunerativo.grid(row=13, column=0, padx=10, pady=5)
entrada_remunerativo = tk.Entry(ventana)
entrada_remunerativo.grid(row=13, column=1)

# Botón para ejecutar el código
boton_ejecutar = tk.Button(ventana, text="Liquidar Sueldo", command=ejecutar_codigo)
boton_ejecutar.grid(row=14, column=0, columnspan=2, padx=10, pady=10)


# Ejecutar la ventana principal
ventana.mainloop()

# Limpiar los campos de entrada
limpiar_campos()

# Mostrar un mensaje de confirmación después de 2 segundos
ventana.after(2000, confirmar_liquidacion)

