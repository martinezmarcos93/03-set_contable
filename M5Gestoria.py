import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
import sqlite3

# Conexión a la base de datos SQLite
conn = sqlite3.connect('gestoria.db')
c = conn.cursor()

# Crear tabla si no existe
c.execute('''CREATE TABLE IF NOT EXISTS clientes_gestoria
             (Nombre TEXT, Cel TEXT, Vehiculo TEXT, Tramites TEXT)''')
conn.commit()
conn.close()

class AddDataWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle('Añadir Datos')
        self.setGeometry(100, 100, 300, 400)
        self.setWindowIcon(QIcon("logo1.jpg"))

        self.nombre_label = QLabel('Nombre:', self)
        self.nombre_input = QLineEdit(self)

        self.cel_label = QLabel('Cel:', self)
        self.cel_input = QLineEdit(self)

        self.vehiculo_label = QLabel('Vehículo:', self)
        self.vehiculo_input = QLineEdit(self)

        self.tramites_label = QLabel('Trámites:', self)
        self.tramites_input = QLineEdit(self)

        self.add_button = QPushButton('Añadir', self)
        self.add_button.clicked.connect(self.add_data)

        layout = QVBoxLayout()
        layout.addWidget(self.nombre_label)
        layout.addWidget(self.nombre_input)
        layout.addWidget(self.cel_label)
        layout.addWidget(self.cel_input)
        layout.addWidget(self.vehiculo_label)
        layout.addWidget(self.vehiculo_input)
        layout.addWidget(self.tramites_label)
        layout.addWidget(self.tramites_input)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def add_data(self):
        nombre = self.nombre_input.text()
        cel = self.cel_input.text()
        vehiculo = self.vehiculo_input.text()
        tramites = self.tramites_input.text()

        # Conexión a la base de datos SQLite
        conn = sqlite3.connect('gestoria.db')
        c = conn.cursor()

        # Insertar los datos en la tabla clientes_gestoria
        c.execute('INSERT INTO clientes_gestoria VALUES (?, ?, ?, ?)',
                  (nombre, cel, vehiculo, tramites))
        conn.commit()
        conn.close()

        self.parent.load_data()
        self.close()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gestoría de Automotores')
        self.setGeometry(500, 100, 1000, 900)
        self.setWindowIcon(QIcon("logo1.jpg"))

        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setRowCount(100)
        self.table.setHorizontalHeaderLabels(['Nombre', 'Cel', 'Vehículo', 'Trámites'])

        self.add_button = QPushButton('Añadir', self)
        self.add_button.clicked.connect(self.add_data)

        self.modify_button = QPushButton('Modificar', self)
        self.modify_button.clicked.connect(self.modify_data)

        self.delete_button = QPushButton('Eliminar', self)
        self.delete_button.clicked.connect(self.delete_data)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.add_button)
        layout.addWidget(self.modify_button)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)

        self.load_data()

    def load_data(self):
        conn = sqlite3.connect('gestoria.db')
        c = conn.cursor()
        c.execute('SELECT * FROM clientes_gestoria')
        data = c.fetchall()
        self.table.setRowCount(100)
        # Establecer ancho de las columnas
        self.table.setColumnWidth(0, 150)  # Nombre
        self.table.setColumnWidth(1, 150)  # Cel
        # Establecer el ancho para las demás columnas según sea necesario

        for row_index, row_data in enumerate(data):
            for column_index, item in enumerate(row_data):
                cell_item = QTableWidgetItem(item)
                cell_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrar y ajustar el texto al centro de cada celda
                self.table.setItem(row_index, column_index, cell_item)
        conn.close()

    def add_data(self):
        self.add_data_window = AddDataWindow(self)
        self.add_data_window.show()

    def modify_data(self):
        # Obtener los datos ingresados en las celdas seleccionadas
        selected_items = self.table.selectedItems()
        if len(selected_items) != self.table.columnCount():
            QMessageBox.warning(self, 'Error', 'Debes seleccionar una fila completa para modificar.')
            return

        data = [item.text() for item in selected_items]

        # Conexión a la base de datos SQLite
        conn = sqlite3.connect('gestoria.db')
        c = conn.cursor()

        # Modificar los datos en la tabla clientes_gestoria
        c.execute('UPDATE clientes_gestoria SET Nombre=?, Cel=?, Vehiculo=?, Tramites=? WHERE Nombre=?', tuple(data + [data[0]]))
        conn.commit()
        conn.close()

        # Actualizar la tabla con los datos modificados
        self.load_data()

    def delete_data(self):
        # Obtener la fila seleccionada
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, 'Error', 'Debes seleccionar una fila para eliminar.')
            return

        # Obtener los datos de la fila seleccionada
        data = [self.table.item(selected_row, column_index).text() for column_index in range(self.table.columnCount())]

        # Conexión a la base de datos SQLite
        conn = sqlite3.connect('gestoria.db')
        c = conn.cursor()

        # Eliminar los datos de la tabla clientes_gestoria
        c.execute('DELETE FROM clientes_gestoria WHERE Nombre=?', (data[0],))
        conn.commit()
        conn.close()

        # Actualizar la tabla sin la fila eliminada
        self.table.removeRow(selected_row)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
