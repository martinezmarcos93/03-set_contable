import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QComboBox
from PyQt5.QtCore import Qt
import sqlite3


# Conexión a la base de datos SQLite
conn = sqlite3.connect('datos_monot.db')
c = conn.cursor()

# Crear tabla si no existe
c.execute('''CREATE TABLE IF NOT EXISTS monotributistas
             (Cliente TEXT, Actividad TEXT, Cuit TEXT, Categoria TEXT, ClaveAfip TEXT, IngresosBrutos TEXT,
              ClaveIIBB TEXT, Cel TEXT, Mail TEXT, Otros TEXT)''')
conn.commit()
conn.close()


class AddDataWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle('Añadir Datos')
        self.setGeometry(100, 100, 300, 400)

        self.cliente_label = QLabel('Cliente:', self)
        self.cliente_input = QLineEdit(self)
        

        self.actividad_label = QLabel('Actividad:', self)
        self.actividad_input = QLineEdit(self)

        self.cuit_label = QLabel('Cuit:', self)
        self.cuit_input = QLineEdit(self)

        self.categoria_label = QLabel('Categoría:', self)
        self.categoria_input = QLineEdit(self)

        self.clave_afip_label = QLabel('Clave AFIP:', self)
        self.clave_afip_input = QLineEdit(self)

        self.ingresos_brutos_label = QLabel('Ingresos Brutos:', self)
        self.ingresos_brutos_input = QLineEdit(self)

        self.clave_iibb_label = QLabel('Clave IIBB:', self)
        self.clave_iibb_input = QLineEdit(self)

        self.cel_label = QLabel('Cel:', self)
        self.cel_input = QLineEdit(self)

        self.mail_label = QLabel('Mail:', self)
        self.mail_input = QLineEdit(self)

        self.otros_label = QLabel('Otros:', self)
        self.otros_input = QLineEdit(self)

        self.add_button = QPushButton('Añadir', self)
        self.add_button.clicked.connect(self.add_data)

        layout = QVBoxLayout()
        layout.addWidget(self.cliente_label)
        layout.addWidget(self.cliente_input)
        layout.addWidget(self.actividad_label)
        layout.addWidget(self.actividad_input)
        layout.addWidget(self.cuit_label)
        layout.addWidget(self.cuit_input)
        layout.addWidget(self.categoria_label)
        layout.addWidget(self.categoria_input)
        layout.addWidget(self.clave_afip_label)
        layout.addWidget(self.clave_afip_input)
        layout.addWidget(self.ingresos_brutos_label)
        layout.addWidget(self.ingresos_brutos_input)
        layout.addWidget(self.clave_iibb_label)
        layout.addWidget(self.clave_iibb_input)
        layout.addWidget(self.cel_label)
        layout.addWidget(self.cel_input)
        layout.addWidget(self.mail_label)
        layout.addWidget(self.mail_input)
        layout.addWidget(self.otros_label)
        layout.addWidget(self.otros_input)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def add_data(self):
        cliente = self.cliente_input.text()
        actividad = self.actividad_input.text()
        cuit = self.cuit_input.text()
        categoria = self.categoria_input.text()
        clave_afip = self.clave_afip_input.text()
        ingresos_brutos = self.ingresos_brutos_input.text()
        clave_iibb = self.clave_iibb_input.text()
        cel = self.cel_input.text()
        mail = self.mail_input.text()
        otros = self.otros_input.text()

        # Conexión a la base de datos SQLite
        conn = sqlite3.connect('datos_monot.db')
        c = conn.cursor()

        # Insertar los datos en la tabla monotributistas
        c.execute('INSERT INTO monotributistas VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                  (cliente, actividad, cuit, categoria, clave_afip, ingresos_brutos, clave_iibb, cel, mail, otros))
        conn.commit()
        conn.close()

        self.parent.load_data()
        self.close()


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Estudio Contable - Inicio de Sesión')
        self.setGeometry(100, 100, 300, 150)

        self.username_label = QLabel('Usuario:', self)
        self.username_label.move(20, 20)
        self.username_input = QLineEdit(self)
        self.username_input.move(100, 20)

        self.password_label = QLabel('Contraseña:', self)
        self.password_label.move(20, 50)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.move(100, 50)

        self.login_button = QPushButton('Iniciar sesión', self)
        self.login_button.clicked.connect(self.login)
        self.login_button.move(100, 80)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if username == 'estudiocristalli' and password == 'bacacay1197':
            self.hide()
            self.select_client_type_window = SelectClientTypeWindow()
            self.select_client_type_window.show()
        else:
            QMessageBox.warning(self, 'Error', 'Credenciales incorrectas.')


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Estudio Contable - Monotributistas')
        self.setGeometry(500, 100, 1000, 900)

        self.table = QTableWidget(self)
        self.table.setColumnCount(10)
        self.table.setRowCount(100)
        self.table.setHorizontalHeaderLabels(['Cliente', 'Actividad', 'Cuit', 'Categoria', 'Clave AFIP',
                                               'Ingresos Brutos', 'Clave IIBB', 'Cel', 'Mail', 'Otros'])

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
        conn = sqlite3.connect('datos_monot.db')
        c = conn.cursor()
        c.execute('SELECT * FROM monotributistas')
        data = c.fetchall()
        self.table.setRowCount(100)
        # Establecer ancho de las columnas
        self.table.setColumnWidth(0, 150)  # Cliente
        self.table.setColumnWidth(1, 150)  # Actividad
# Establecer el ancho para las demás columnas según sea necesario

        for row_index, row_data in enumerate(data):
            for column_index, item in enumerate(row_data):
                cell_item = QTableWidgetItem(item)
                cell_item.setTextAlignment(Qt.AlignCenter)  # Centrar y ajustar el texto al centro de cada celda
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
        conn = sqlite3.connect('datos_monot.db')
        c = conn.cursor()

        # Modificar los datos en la tabla monotributistas
        c.execute('UPDATE monotributistas SET Cliente=?, Actividad=?, Cuit=?, Categoria=?, ClaveAfip=?, IngresosBrutos=?, '
                  'ClaveIIBB=?, Cel=?, Mail=?, Otros=? WHERE Cliente=?', tuple(data + [data[0]]))
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
        conn = sqlite3.connect('datos_monot.db')
        c = conn.cursor()

        # Eliminar los datos de la tabla monotributistas
        c.execute('DELETE FROM monotributistas WHERE Cliente=?', (data[0],))
        conn.commit()
        conn.close()

        # Actualizar la tabla sin la fila eliminada
        self.table.removeRow(selected_row)
        
# Conexión a la base de datos SQLite
conn = sqlite3.connect('datos_resp.db')
c = conn.cursor()


c.execute('''CREATE TABLE IF NOT EXISTS responsable_inscripto
             (RAZON_SOCIAL TEXT, CUIT TEXT, CLAVE_AFIP TEXT, CLAVE_IIBB TEXT, CLAVE_CABA TEXT, CEL TEXT, MAIL TEXT)''')

class MainWindowRI(QWidget):
    def __init__(self, table_name, window_title):
        super().__init__()
        self.table_name = table_name
        self.setWindowTitle(window_title)
        self.setGeometry(100, 100, 800, 600)

        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['RAZON SOCIAL', 'CUIT', 'CLAVE AFIP', 'CLAVE IIBB', 'CLAVE CABA', 'CEL', 'MAIL'])

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
        conn = sqlite3.connect('datos_resp.db')
        c = conn.cursor()
        c.execute(f'SELECT * FROM {self.table_name}')
        data = c.fetchall()
        self.table.setRowCount(len(data))
        for row_index, row_data in enumerate(data):
            for column_index, item in enumerate(row_data):
                cell_item = QTableWidgetItem(item)
                self.table.setItem(row_index, column_index, cell_item)
        conn.close()

    def add_data(self):
        self.add_data_window = AddDataWindow(self)
        self.add_data_window.show()

    def modify_data(self):
        selected_items = self.table.selectedItems()
        if len(selected_items) != self.table.columnCount():
            QMessageBox.warning(self, 'Error', 'Debes seleccionar una fila completa para modificar.')
            return

        data = [item.text() for item in selected_items]

        conn = sqlite3.connect('datos_resp.db')
        c = conn.cursor()
        c.execute(f'UPDATE {self.table_name} SET razon_social = ?, cuit = ?, clave_afip = ?, clave_iibb = ?, clave_caba = ?, cel = ?, mail = ? WHERE cuit = ?',
                  (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[1]))
        conn.commit()
        conn.close()

        self.load_data()

    def delete_data(self):
        selected_items = self.table.selectedItems()
        if len(selected_items) != self.table.columnCount():
            QMessageBox.warning(self, 'Error', 'Debes seleccionar una fila completa para eliminar.')
            return

        data = [item.text() for item in selected_items]

        reply = QMessageBox.question(self, 'Eliminar', '¿Estás seguro de que quieres eliminar este cliente?',
                                      QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect('datos_resp.db')
            c = conn.cursor()
            c.execute(f'DELETE FROM {self.table_name} WHERE cuit = ?', (data[1],))
            conn.commit()
            conn.close()

            self.load_data()


class MainWindowRI(MainWindowRI):  # Hereda de MainWindow
    def __init__(self, table_name, window_title):
        super().__init__(table_name, window_title)


class SelectClientTypeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Estudio Contable - Selección de Tipo de Cliente')
        self.setGeometry(100, 100, 300, 150)

        self.client_type_label = QLabel('Selecciona el tipo de cliente:', self)
        self.client_type_label.move(20, 20)

        self.monotributista_button = QPushButton('Monotributista', self)
        self.monotributista_button.clicked.connect(self.open_monotributista_window)
        self.monotributista_button.move(50, 50)

        self.responsable_inscripto_button = QPushButton('Responsable Inscripto', self)
        self.responsable_inscripto_button.clicked.connect(self.open_responsable_inscripto_window)
        self.responsable_inscripto_button.move(50, 80)

        self.otro_button = QPushButton('Otro', self)
        self.otro_button.clicked.connect(self.open_otro_window)
        self.otro_button.move(50, 110)

    def open_monotributista_window(self):
        self.hide()
        self.main_window = MainWindow('monotributistas', 'Estudio Contable - Monotributistas')
        self.main_window.show()

    def open_responsable_inscripto_window(self):
        self.hide()
        self.main_window_ri = MainWindowRI('responsable_inscripto', 'Estudio Contable - Responsable Inscripto')
        self.main_window_ri.show()

    def open_otro_window(self):
        # Agrega el código para abrir la ventana correspondiente al tipo de cliente "Otro"
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())