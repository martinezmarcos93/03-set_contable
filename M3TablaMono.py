"""
M3TablaMono.py — Panel de Monotributistas
"""

import sys
import os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout,
    QHBoxLayout, QGridLayout, QHeaderView, QCheckBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QColor, QGuiApplication

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
DB_PATH   = os.path.join(DATA_DIR, "datos_monot.db")
LOGO_PATH = os.path.join(DATA_DIR, "logo1.jpg")

COLS_DISPLAY = [
    "Rev.", "Nombre", "Cat", "Actividad", "CUIT",
    "Clave AFIP", "Clave Agip/Arba", "IIBB",
    "Observaciones", "Condición"
]
CONDICIONES = ["Casual", "Mensual", "Baja"]

COLORES_CONDICION = {
    "Baja":    QColor("#ffcccc"),
    "Mensual": QColor("#ccffcc"),
    "Casual":  QColor("#ffffff"),
}
COLOR_DEFAULT = QColor("#ffffff")


def get_conn():
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS monotributistas (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            revision        INTEGER DEFAULT 0,
            nombre          TEXT,
            categoria       TEXT,
            actividad       TEXT,
            cuit            TEXT,
            clave_afip      TEXT,
            clave_agip_arba TEXT,
            iibb            TEXT,
            observaciones   TEXT,
            condicion       TEXT
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
        self.resize(380, 420)
        self.move(screen.center().x() - 190, screen.center().y() - 210)

        grid = QGridLayout()
        self.fields = {}

        labels_keys = [
            ("Nombre",          "nombre"),
            ("Categoría",       "categoria"),
            ("Actividad",       "actividad"),
            ("CUIT",            "cuit"),
            ("Clave AFIP",      "clave_afip"),
            ("Clave Agip/Arba", "clave_agip_arba"),
            ("IIBB",            "iibb"),
            ("Observaciones",   "observaciones"),
        ]

        for i, (label, key) in enumerate(labels_keys):
            grid.addWidget(QLabel(f"{label}:"), i, 0)
            if key == "observaciones":
                w = QTextEdit()
                w.setFixedHeight(60)
            else:
                w = QLineEdit()
            self.fields[key] = w
            grid.addWidget(w, i, 1)

        grid.addWidget(QLabel("Condición:"), len(labels_keys), 0)
        self.combo_condicion = QComboBox()
        self.combo_condicion.addItems(CONDICIONES)
        grid.addWidget(self.combo_condicion, len(labels_keys), 1)

        self.chk_revision = QCheckBox("Marcado para revisión")
        grid.addWidget(self.chk_revision, len(labels_keys) + 1, 0, 1, 2)

        btn = QPushButton("Guardar")
        btn.clicked.connect(self._guardar)
        grid.addWidget(btn, len(labels_keys) + 2, 0, 1, 2)

        grid.setContentsMargins(16, 16, 16, 16)
        grid.setVerticalSpacing(8)
        self.setLayout(grid)

        if is_edit:
            _, rev, nombre, cat, activ, cuit, c_afip, c_agip, iibb, obs, cond = row_data
            self.fields["nombre"].setText(nombre or "")
            self.fields["categoria"].setText(cat or "")
            self.fields["actividad"].setText(activ or "")
            self.fields["cuit"].setText(cuit or "")
            self.fields["clave_afip"].setText(c_afip or "")
            self.fields["clave_agip_arba"].setText(c_agip or "")
            self.fields["iibb"].setText(iibb or "")
            w_obs = self.fields["observaciones"]
            if isinstance(w_obs, QTextEdit):
                w_obs.setPlainText(obs or "")
            else:
                w_obs.setText(obs or "")
            idx = self.combo_condicion.findText(cond or "")
            if idx >= 0:
                self.combo_condicion.setCurrentIndex(idx)
            self.chk_revision.setChecked(bool(rev))

    def _guardar(self):
        def val(k):
            w = self.fields[k]
            return w.toPlainText().strip() if isinstance(w, QTextEdit) else w.text().strip()

        data = {k: val(k) for k in self.fields}
        data["condicion"] = self.combo_condicion.currentText()
        data["revision"]  = 1 if self.chk_revision.isChecked() else 0

        with get_conn() as conn:
            if self.row_id is None:
                conn.execute(
                    '''INSERT INTO monotributistas
                       (revision,nombre,categoria,actividad,cuit,
                        clave_afip,clave_agip_arba,iibb,observaciones,condicion)
                       VALUES (?,?,?,?,?,?,?,?,?,?)''',
                    (data["revision"], data["nombre"], data["categoria"],
                     data["actividad"], data["cuit"], data["clave_afip"],
                     data["clave_agip_arba"], data["iibb"],
                     data["observaciones"], data["condicion"])
                )
            else:
                conn.execute(
                    '''UPDATE monotributistas SET
                       revision=?,nombre=?,categoria=?,actividad=?,cuit=?,
                       clave_afip=?,clave_agip_arba=?,iibb=?,observaciones=?,condicion=?
                       WHERE id=?''',
                    (data["revision"], data["nombre"], data["categoria"],
                     data["actividad"], data["cuit"], data["clave_afip"],
                     data["clave_agip_arba"], data["iibb"],
                     data["observaciones"], data["condicion"],
                     self.row_id)
                )
        self.parent_window.load_data()
        self.close()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        init_db()
        self.setWindowTitle("Monotributistas")
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
        self.search_input.setPlaceholderText("Buscar por nombre, CUIT o actividad...")
        self.search_input.textChanged.connect(self.load_data)
        search_bar.addWidget(QLabel("Buscar:"))
        search_bar.addWidget(self.search_input)

        self.combo_filtro = QComboBox()
        self.combo_filtro.addItems(["Todos"] + CONDICIONES)
        self.combo_filtro.currentTextChanged.connect(self.load_data)
        search_bar.addWidget(QLabel("Condición:"))
        search_bar.addWidget(self.combo_filtro)

        self.table = QTableWidget()
        self.table.setColumnCount(len(COLS_DISPLAY))
        self.table.setHorizontalHeaderLabels(COLS_DISPLAY)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
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
                'SELECT * FROM monotributistas ORDER BY nombre'
            ).fetchall()

        if q:
            rows = [r for r in rows if
                    q in (r[2] or "").lower() or
                    q in (r[5] or "").lower() or
                    q in (r[4] or "").lower()]
        if filtro != "Todos":
            rows = [r for r in rows if (r[10] or "") == filtro]

        self._row_ids = [r[0] for r in rows]
        self.table.setRowCount(len(rows))

        for r_i, row in enumerate(rows):
            display_vals = [
                "✔" if row[1] else "",
                row[2] or "", row[3] or "", row[4] or "", row[5] or "",
                row[6] or "", row[7] or "", row[8] or "",
                row[9] or "", row[10] or "",
            ]
            color = COLORES_CONDICION.get(row[10] or "", COLOR_DEFAULT)
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
                'SELECT * FROM monotributistas WHERE id=?', (row_id,)
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
        self._detalle = VentanaDetalle(cliente_id=row_id, tipo="mono", nombre=nombre)
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
                conn.execute('DELETE FROM monotributistas WHERE id=?', (row_id,))
            self.load_data()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow(); w.show()
    sys.exit(app.exec())
