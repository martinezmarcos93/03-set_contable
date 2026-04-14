"""
M4TablaResp.py — Panel de Responsables Inscriptos
==================================================
Nombre de tabla SQLite cambiado de 'estudio_contable_responsables_inscriptos'
a 'responsables_inscriptos' (genérico, sin nombre personal).
"""

import sys
import os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
    QLabel, QLineEdit, QHeaderView, QComboBox, QCheckBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QColor, QGuiApplication

DATA_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
DB_PATH   = os.path.join(DATA_DIR, "datos_resp.db")
LOGO_PATH = os.path.join(DATA_DIR, "logo1.jpg")

TABLE_NAME = "responsables_inscriptos"

COLS_DISPLAY = [
    "Rev.", "Razón Social", "CUIT", "Clave ARCA",
    "Clave ARBA", "Clave AGIP", "Condición IIBB", "Observaciones"
]
CONDICIONES_IIBB = ["Contribuyente", "Convenio Multilateral", "Exento", "No inscripto"]
CONDICIONES_GRAL = ["Activo", "Baja", "Suspendido"]

COLORES = {
    "Activo":     QColor("#ccffcc"),
    "Baja":       QColor("#ffcccc"),
    "Suspendido": QColor("#fff3cc"),
}
COLOR_DEFAULT = QColor("#ffffff")


def get_conn():
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute(f'''CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            revision       INTEGER DEFAULT 0,
            razon_social   TEXT,
            cuit           TEXT,
            clave_arca     TEXT,
            clave_arba     TEXT,
            clave_agip     TEXT,
            condicion_iibb TEXT,
            observaciones  TEXT,
            condicion      TEXT DEFAULT 'Activo'
        )''')


class FormDialog(QWidget):
    def __init__(self, parent_window, row_data=None, row_id=None):
        super().__init__()
        self.parent_window = parent_window
        self.row_id = row_id
        is_edit = row_data is not None
        self.setWindowTitle("Editar cliente" if is_edit else "Agregar cliente")
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))

        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(420, 400)
        self.move(screen.center().x() - 210, screen.center().y() - 200)

        grid = QGridLayout()
        self.fields = {}

        text_fields = [
            ("Razón Social", "razon_social"),
            ("CUIT",         "cuit"),
            ("Clave ARCA",   "clave_arca"),
            ("Clave ARBA",   "clave_arba"),
            ("Clave AGIP",   "clave_agip"),
        ]
        for i, (lbl, key) in enumerate(text_fields):
            grid.addWidget(QLabel(f"{lbl}:"), i, 0)
            w = QLineEdit()
            self.fields[key] = w
            grid.addWidget(w, i, 1)

        r = len(text_fields)
        grid.addWidget(QLabel("Condición IIBB:"), r, 0)
        self.combo_iibb = QComboBox()
        self.combo_iibb.addItems(CONDICIONES_IIBB)
        grid.addWidget(self.combo_iibb, r, 1)

        grid.addWidget(QLabel("Observaciones:"), r+1, 0, Qt.AlignmentFlag.AlignTop)
        self.txt_obs = QTextEdit()
        self.txt_obs.setFixedHeight(60)
        grid.addWidget(self.txt_obs, r+1, 1)

        grid.addWidget(QLabel("Estado:"), r+2, 0)
        self.combo_cond = QComboBox()
        self.combo_cond.addItems(CONDICIONES_GRAL)
        grid.addWidget(self.combo_cond, r+2, 1)

        self.chk_rev = QCheckBox("Marcado para revisión")
        grid.addWidget(self.chk_rev, r+3, 0, 1, 2)

        btn = QPushButton("Guardar")
        btn.clicked.connect(self._guardar)
        grid.addWidget(btn, r+4, 0, 1, 2)

        grid.setContentsMargins(16, 16, 16, 16)
        grid.setVerticalSpacing(8)
        self.setLayout(grid)

        if is_edit:
            _, rev, rs, cuit, arca, arba, agip, c_iibb, obs, cond = row_data
            self.fields["razon_social"].setText(rs or "")
            self.fields["cuit"].setText(cuit or "")
            self.fields["clave_arca"].setText(arca or "")
            self.fields["clave_arba"].setText(arba or "")
            self.fields["clave_agip"].setText(agip or "")
            idx = self.combo_iibb.findText(c_iibb or "")
            if idx >= 0: self.combo_iibb.setCurrentIndex(idx)
            self.txt_obs.setPlainText(obs or "")
            idx2 = self.combo_cond.findText(cond or "")
            if idx2 >= 0: self.combo_cond.setCurrentIndex(idx2)
            self.chk_rev.setChecked(bool(rev))

    def _guardar(self):
        rs     = self.fields["razon_social"].text().strip()
        cuit   = self.fields["cuit"].text().strip()
        arca   = self.fields["clave_arca"].text().strip()
        arba   = self.fields["clave_arba"].text().strip()
        agip   = self.fields["clave_agip"].text().strip()
        c_iibb = self.combo_iibb.currentText()
        obs    = self.txt_obs.toPlainText().strip()
        cond   = self.combo_cond.currentText()
        rev    = 1 if self.chk_rev.isChecked() else 0

        with get_conn() as conn:
            if self.row_id is None:
                conn.execute(
                    f'''INSERT INTO {TABLE_NAME}
                        (revision,razon_social,cuit,clave_arca,clave_arba,
                         clave_agip,condicion_iibb,observaciones,condicion)
                        VALUES (?,?,?,?,?,?,?,?,?)''',
                    (rev, rs, cuit, arca, arba, agip, c_iibb, obs, cond)
                )
            else:
                conn.execute(
                    f'''UPDATE {TABLE_NAME} SET
                        revision=?,razon_social=?,cuit=?,clave_arca=?,clave_arba=?,
                        clave_agip=?,condicion_iibb=?,observaciones=?,condicion=?
                        WHERE id=?''',
                    (rev, rs, cuit, arca, arba, agip, c_iibb, obs, cond, self.row_id)
                )
        self.parent_window.load_data()
        self.close()


class MainWindowRI(QWidget):
    def __init__(self, window_title="Responsables Inscriptos"):
        super().__init__()
        init_db()
        self.setWindowTitle(window_title)
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))

        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(1100, 700)
        self.move(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2
        )

        search_bar = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por razón social o CUIT...")
        self.search_input.textChanged.connect(self.load_data)
        search_bar.addWidget(QLabel("Buscar:"))
        search_bar.addWidget(self.search_input)

        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Todos"] + CONDICIONES_GRAL)
        self.combo_filtro.currentTextChanged.connect(self.load_data)
        search_bar.addWidget(QLabel("Estado:"))
        search_bar.addWidget(self.combo_filtro)

        self.table = QTableWidget()
        self.table.setColumnCount(len(COLS_DISPLAY))
        self.table.setHorizontalHeaderLabels(COLS_DISPLAY)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._abrir_detalle)

        btn_layout = QHBoxLayout()
        self.btn_add    = QPushButton("+ Agregar")
        self.btn_edit   = QPushButton("Editar datos")
        self.btn_detail = QPushButton("Ver detalle / CC")
        self.btn_detail.setStyleSheet(
            "background:#1a5276; color:white; padding:5px 10px; border-radius:4px;"
        )
        self.btn_delete = QPushButton("Eliminar")
        for b in (self.btn_add, self.btn_edit, self.btn_detail, self.btn_delete):
            btn_layout.addWidget(b)

        self.btn_add.clicked.connect(self._agregar)
        self.btn_edit.clicked.connect(self._editar)
        self.btn_detail.clicked.connect(self._abrir_detalle)
        self.btn_delete.clicked.connect(self._eliminar)

        lbl_hint = QLabel("  Doble clic en una fila para abrir detalle y cuenta corriente")
        lbl_hint.setStyleSheet("color: gray; font-size: 11px;")

        layout = QVBoxLayout()
        layout.addLayout(search_bar)
        layout.addWidget(self.table)
        layout.addWidget(lbl_hint)
        layout.addLayout(btn_layout)
        layout.setContentsMargins(16, 16, 16, 16)
        self.setLayout(layout)

        self._row_ids = []
        self.load_data()

    def load_data(self):
        q      = self.search_input.text().strip().lower()
        filtro = self.combo_filtro.currentText()

        with get_conn() as conn:
            rows = conn.execute(
                f'SELECT * FROM {TABLE_NAME} ORDER BY razon_social'
            ).fetchall()

        if q:
            rows = [r for r in rows if
                    q in (r[2] or "").lower() or
                    q in (r[3] or "").lower()]
        if filtro != "Todos":
            rows = [r for r in rows if (r[9] or "") == filtro]

        self._row_ids = [r[0] for r in rows]
        self.table.setRowCount(len(rows))

        for r_i, row in enumerate(rows):
            display_vals = [
                "✔" if row[1] else "",
                row[2] or "", row[3] or "", row[4] or "",
                row[5] or "", row[6] or "", row[7] or "",
                row[8] or "",
            ]
            color = COLORES.get(row[9] or "", COLOR_DEFAULT)
            for c_i, val in enumerate(display_vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(color)
                self.table.setItem(r_i, c_i, item)

    def _get_selected_id(self):
        row = self.table.currentRow()
        if row < 0 or row >= len(self._row_ids):
            return None, None
        return row, self._row_ids[row]

    def _get_row_data(self, row_id):
        with get_conn() as conn:
            return conn.execute(
                f'SELECT * FROM {TABLE_NAME} WHERE id=?', (row_id,)
            ).fetchone()

    def _agregar(self):
        self._form = FormDialog(self); self._form.show()

    def _editar(self):
        row, row_id = self._get_selected_id()
        if row_id is None:
            QMessageBox.warning(self, "Error", "Seleccioná una fila para editar."); return
        self._form = FormDialog(self, row_data=self._get_row_data(row_id), row_id=row_id)
        self._form.show()

    def _abrir_detalle(self):
        row, row_id = self._get_selected_id()
        if row_id is None:
            QMessageBox.warning(self, "Error", "Seleccioná una fila."); return
        nombre_item = self.table.item(row, 1)
        nombre = nombre_item.text() if nombre_item else f"Cliente #{row_id}"
        from MClienteDetalle import VentanaDetalle
        self._detalle = VentanaDetalle(cliente_id=row_id, tipo="resp", nombre=nombre)
        self._detalle.show()

    def _eliminar(self):
        row, row_id = self._get_selected_id()
        if row_id is None:
            QMessageBox.warning(self, "Error", "Seleccioná una fila para eliminar."); return
        nombre = self.table.item(row, 1).text()
        if QMessageBox.question(
            self, "Confirmar eliminación", f"¿Eliminar a {nombre}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            with get_conn() as conn:
                conn.execute(f'DELETE FROM {TABLE_NAME} WHERE id=?', (row_id,))
            self.load_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindowRI(); w.show()
    sys.exit(app.exec())
