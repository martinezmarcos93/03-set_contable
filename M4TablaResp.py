import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, \
    QPushButton, QMessageBox, QLabel, QLineEdit, QGridLayout
from PyQt5.QtCore import Qt
import sqlite3

conn = sqlite3.connect('datos_resp.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS estudio_contable_responsables_inscriptos
             (RAZON_SOCIAL TEXT, CUIT TEXT, CLAVE_AFIP TEXT, CLAVE_IIBB TEXT, CLAVE_CABA TEXT, CEL TEXT, MAIL TEXT)''')

class AddDataWindow(QWidget):
    def __init__(self, parent, table_name):
        super().__init__()
        self.parent = parent
        self.table_name = table_name
        self.setWindowTitle('Agregar Datos')
        self.setGeometry(400, 100, 400, 600)

        self.razon_social_label = QLabel('Razón Social:', self)
        self.cuit_label = QLabel('CUIT:', self)
        self.clave_afip_label = QLabel('Clave AFIP:', self)
        self.clave_iibb_label = QLabel('Clave IIBB:', self)
        self.clave_caba_label = QLabel('Clave CABA:', self)
        self.cel_label = QLabel('Cel:', self)
        self.mail_label = QLabel('Mail:', self)

        self.razon_social_input = QLineEdit(self)
        self.cuit_input = QLineEdit(self)
        self.clave_afip_input = QLineEdit(self)
        self.clave_iibb_input = QLineEdit(self)
        self.clave_caba_input = QLineEdit(self)
        self.cel_input = QLineEdit(self)
        self.mail_input = QLineEdit(self)

        self.save_button = QPushButton('Guardar', self)
        self.save_button.clicked.connect(self.save_data)

        layout = QGridLayout()
        layout.addWidget(self.razon_social_label, 0, 0)
        layout.addWidget(self.cuit_label, 1, 0)
        layout.addWidget(self.clave_afip_label, 2, 0)
        layout.addWidget(self.clave_iibb_label, 3, 0)
        layout.addWidget(self.clave_caba_label, 4, 0)
        layout.addWidget(self.cel_label, 5, 0)
        layout.addWidget(self.mail_label, 6, 0)

        layout.addWidget(self.razon_social_input, 0, 1)
        layout.addWidget(self.cuit_input, 1, 1)
        layout.addWidget(self.clave_afip_input, 2, 1)
        layout.addWidget(self.clave_iibb_input, 3, 1)
        layout.addWidget(self.clave_caba_input, 4, 1)
        layout.addWidget(self.cel_input, 5, 1)
        layout.addWidget(self.mail_input, 6, 1)

        layout.addWidget(self.save_button, 7, 0, 1, 2)

        self.setLayout(layout)

    def save_data(self):
        razon_social = self.razon_social_input.text()
        cuit = self.cuit_input.text()
        clave_afip = self.clave_afip_input.text()
        clave_iibb = self.clave_iibb_input.text()
        clave_caba = self.clave_caba_input.text()
        cel = self.cel_input.text()
        mail = self.mail_input.text()

        conn = sqlite3.connect('datos_resp.db')
        c = conn.cursor()

        c.execute(f'INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?, ?, ?)',
                  (razon_social, cuit, clave_afip, clave_iibb, clave_caba, cel, mail))

        conn.commit()
        conn.close()

        self.parent.load_data()
        self.close()


class MainWindowRI(QWidget):
    def __init__(self, table_name, window_title):
        super().__init__()
        self.table_name = table_name
        self.setWindowTitle(window_title)
        self.setGeometry(500, 100, 800, 900)

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
                cell_item.setTextAlignment(Qt.AlignCenter)  # Centrar el texto
                self.table.setItem(row_index, column_index, cell_item)
        conn.close()

    def add_data(self):
        self.add_data_window = AddDataWindow(self, self.table_name)
        self.add_data_window.show()

    def modify_data(self):
        selected_items = self.table.selectedItems()
        if len(selected_items) != self.table.columnCount():
            QMessageBox.warning(self, 'Error', 'Debes seleccionar una fila completa para modificar.')
            return

        data = [item.text() for item in selected_items]

        conn = sqlite3.connect('datos_resp.db')
        c = conn.cursor()
        c.execute(f'UPDATE {self.table_name} SET RAZON_SOCIAL = ?, CUIT = ?, CLAVE_AFIP = ?, CLAVE_IIBB = ?, CLAVE_CABA = ?, CEL = ?, MAIL = ? WHERE CUIT = ?',
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
            c.execute(f'DELETE FROM {self.table_name} WHERE CUIT = ?', (data[1],))
            conn.commit()
            conn.close()

            self.load_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindowRI('estudio_contable_responsables_inscriptos', 'Estudio Contable - Responsables Inscriptos')
    main_window.table.setShowGrid(True)  # Mostrar líneas de cuadrícula
    main_window.show()
    sys.exit(app.exec_())
