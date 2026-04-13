import sys
import os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox, QLabel, QLineEdit, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
DB_PATH = os.path.join(DATA_DIR, "datos_resp.db")
LOGO_PATH = os.path.join(DATA_DIR, "logo1.jpg")

COLUMNAS = ['RAZON SOCIAL', 'CUIT', 'CLAVE AFIP', 'CLAVE IIBB', 'CLAVE CABA', 'CEL', 'MAIL']
FIELDS_DB = ['RAZON_SOCIAL', 'CUIT', 'CLAVE_AFIP', 'CLAVE_IIBB', 'CLAVE_CABA', 'CEL', 'MAIL']


def get_conn():
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db(table_name: str):
    with get_conn() as conn:
        conn.execute(f'''CREATE TABLE IF NOT EXISTS {table_name}
            (RAZON_SOCIAL TEXT, CUIT TEXT, CLAVE_AFIP TEXT,
             CLAVE_IIBB TEXT, CLAVE_CABA TEXT, CEL TEXT, MAIL TEXT)''')


class AddDataWindow(QWidget):
    def __init__(self, parent, table_name: str):
        super().__init__()
        self.parent_window = parent
        self.table_name = table_name
        self.setWindowTitle("Agregar Responsable Inscripto")
        self.setGeometry(400, 150, 380, 320)
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))

        self.inputs = {}
        layout = QGridLayout()

        for i, (col_display, field) in enumerate(zip(COLUMNAS, FIELDS_DB)):
            layout.addWidget(QLabel(f"{col_display}:"), i, 0)
            inp = QLineEdit()
            self.inputs[field] = inp
            layout.addWidget(inp, i, 1)

        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self._save_data)
        layout.addWidget(self.save_button, len(COLUMNAS), 0, 1, 2)
        self.setLayout(layout)

    def _save_data(self):
        values = [self.inputs[f].text() for f in FIELDS_DB]
        with get_conn() as conn:
            conn.execute(
                f'INSERT INTO {self.table_name} VALUES (?,?,?,?,?,?,?)',
                values
            )
        self.parent_window.load_data()
        self.close()


class MainWindowRI(QWidget):
    def __init__(self, table_name: str, window_title: str):
        super().__init__()
        self.table_name = table_name
        init_db(table_name)
        self.setWindowTitle(window_title)
        self.setGeometry(500, 100, 800, 700)
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))

        self.table = QTableWidget()
        self.table.setColumnCount(len(COLUMNAS))
        self.table.setHorizontalHeaderLabels(COLUMNAS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.add_button = QPushButton("Añadir")
        self.modify_button = QPushButton("Guardar cambios")
        self.delete_button = QPushButton("Eliminar")

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.add_button)
        layout.addWidget(self.modify_button)
        layout.addWidget(self.delete_button)
        self.setLayout(layout)

        self.add_button.clicked.connect(self._add_data)
        self.modify_button.clicked.connect(self._modify_data)
        self.delete_button.clicked.connect(self._delete_data)

        self.load_data()

    def load_data(self):
        with get_conn() as conn:
            rows = conn.execute(f'SELECT * FROM {self.table_name}').fetchall()
        self.table.setRowCount(len(rows))
        for r_i, row in enumerate(rows):
            for c_i, val in enumerate(row):
                item = QTableWidgetItem(str(val) if val else "")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(r_i, c_i, item)

    def _add_data(self):
        self._add_window = AddDataWindow(self, self.table_name)
        self._add_window.show()

    def _modify_data(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccioná una fila para modificar.")
            return
        data = [self.table.item(row, c).text() for c in range(self.table.columnCount())]
        with get_conn() as conn:
            conn.execute(
                f'''UPDATE {self.table_name}
                    SET RAZON_SOCIAL=?,CUIT=?,CLAVE_AFIP=?,CLAVE_IIBB=?,CLAVE_CABA=?,CEL=?,MAIL=?
                    WHERE CUIT=?''',
                data + [data[1]]
            )
        self.load_data()

    def _delete_data(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccioná una fila para eliminar.")
            return
        cuit = self.table.item(row, 1).text()
        confirm = QMessageBox.question(
            self, "Confirmar", f"¿Eliminar el cliente con CUIT {cuit}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            with get_conn() as conn:
                conn.execute(f'DELETE FROM {self.table_name} WHERE CUIT=?', (cuit,))
            self.load_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindowRI(
        'estudio_contable_responsables_inscriptos',
        'Responsables Inscriptos — MMAC'
    )
    w.show()
    sys.exit(app.exec())
