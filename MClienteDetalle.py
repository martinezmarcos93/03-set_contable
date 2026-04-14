"""
MClienteDetalle.py
──────────────────
Pantalla de detalle de cliente: datos de contacto, honorarios y cuenta corriente.
Reutilizable tanto para Monotributistas como para Responsables Inscriptos.

Uso:
    w = VentanaDetalle(cliente_id=5, tipo="mono",  nombre="Juan Pérez")
    w = VentanaDetalle(cliente_id=3, tipo="resp",  nombre="Empresa SA")
"""

import os
import sqlite3
from datetime import date, datetime

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QGridLayout, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QDoubleSpinBox, QComboBox, QTextEdit,
    QFrame, QSplitter, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QIcon, QColor, QFont, QGuiApplication

DATA_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
DB_PATH   = os.path.join(DATA_DIR, "clientes.db")
LOGO_PATH = os.path.join(DATA_DIR, "logo1.jpg")

MESES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio",
         "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"]


# ──────────────────────────────────────────────────────────────────────────────
# DB helpers
# ──────────────────────────────────────────────────────────────────────────────

def get_conn():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clientes_detalle (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo          TEXT NOT NULL,   -- 'mono' | 'resp'
                cliente_id    INTEGER NOT NULL,
                cel           TEXT DEFAULT '',
                mail          TEXT DEFAULT '',
                banco         TEXT DEFAULT '',
                cbu           TEXT DEFAULT '',
                honorarios    REAL DEFAULT 0,
                notas         TEXT DEFAULT '',
                UNIQUE(tipo, cliente_id)
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cuenta_corriente (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo          TEXT NOT NULL,
                cliente_id    INTEGER NOT NULL,
                fecha         TEXT NOT NULL,   -- ISO  YYYY-MM-DD
                descripcion   TEXT NOT NULL,
                debe          REAL DEFAULT 0,
                haber         REAL DEFAULT 0
            )""")


def get_detalle(tipo: str, cliente_id: int) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT cel,mail,banco,cbu,honorarios,notas "
            "FROM clientes_detalle WHERE tipo=? AND cliente_id=?",
            (tipo, cliente_id)
        ).fetchone()
    if row:
        return dict(zip(["cel","mail","banco","cbu","honorarios","notas"], row))
    return {"cel":"","mail":"","banco":"","cbu":"","honorarios":0.0,"notas":""}


def save_detalle(tipo: str, cliente_id: int, data: dict):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO clientes_detalle (tipo,cliente_id,cel,mail,banco,cbu,honorarios,notas)
            VALUES (?,?,?,?,?,?,?,?)
            ON CONFLICT(tipo,cliente_id) DO UPDATE SET
                cel=excluded.cel, mail=excluded.mail, banco=excluded.banco,
                cbu=excluded.cbu, honorarios=excluded.honorarios, notas=excluded.notas
        """, (tipo, cliente_id,
              data["cel"], data["mail"], data["banco"], data["cbu"],
              data["honorarios"], data["notas"]))


def get_movimientos(tipo: str, cliente_id: int):
    with get_conn() as conn:
        return conn.execute(
            "SELECT id,fecha,descripcion,debe,haber "
            "FROM cuenta_corriente "
            "WHERE tipo=? AND cliente_id=? "
            "ORDER BY fecha, id",
            (tipo, cliente_id)
        ).fetchall()


def add_movimiento(tipo: str, cliente_id: int,
                   fecha: str, descripcion: str,
                   debe: float, haber: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO cuenta_corriente (tipo,cliente_id,fecha,descripcion,debe,haber) "
            "VALUES (?,?,?,?,?,?)",
            (tipo, cliente_id, fecha, descripcion, debe, haber)
        )


def del_movimiento(mov_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM cuenta_corriente WHERE id=?", (mov_id,))


def get_saldo(tipo: str, cliente_id: int) -> float:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(debe),0) - COALESCE(SUM(haber),0) "
            "FROM cuenta_corriente WHERE tipo=? AND cliente_id=?",
            (tipo, cliente_id)
        ).fetchone()
    return row[0] if row else 0.0


# ──────────────────────────────────────────────────────────────────────────────
# Diálogo: nuevo movimiento manual
# ──────────────────────────────────────────────────────────────────────────────

class DialogMovimiento(QDialog):
    def __init__(self, parent=None, debe_o_haber="debe"):
        super().__init__(parent)
        self.setWindowTitle("Registrar movimiento")
        self.setMinimumWidth(340)

        layout = QGridLayout()

        layout.addWidget(QLabel("Fecha (AAAA-MM-DD):"), 0, 0)
        self.inp_fecha = QLineEdit(date.today().isoformat())
        layout.addWidget(self.inp_fecha, 0, 1)

        layout.addWidget(QLabel("Descripción:"), 1, 0)
        self.inp_desc = QLineEdit()
        layout.addWidget(self.inp_desc, 1, 1)

        layout.addWidget(QLabel("Monto ($):"), 2, 0)
        self.inp_monto = QLineEdit()
        self.inp_monto.setPlaceholderText("0.00")
        layout.addWidget(self.inp_monto, 2, 1)

        layout.addWidget(QLabel("Tipo:"), 3, 0)
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Debe (cargo)", "Haber (pago)"])
        if debe_o_haber == "haber":
            self.combo_tipo.setCurrentIndex(1)
        layout.addWidget(self.combo_tipo, 3, 1)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns, 4, 0, 1, 2)

        self.setLayout(layout)

    def get_data(self):
        try:
            monto = float(self.inp_monto.text().replace(",", "."))
        except ValueError:
            monto = 0.0
        es_haber = self.combo_tipo.currentIndex() == 1
        return {
            "fecha":       self.inp_fecha.text().strip(),
            "descripcion": self.inp_desc.text().strip(),
            "debe":        0.0 if es_haber else monto,
            "haber":       monto if es_haber else 0.0,
        }


# ──────────────────────────────────────────────────────────────────────────────
# Pantalla principal de detalle
# ──────────────────────────────────────────────────────────────────────────────

class VentanaDetalle(QWidget):
    def __init__(self, cliente_id: int, tipo: str, nombre: str):
        super().__init__()
        init_db()
        self.cliente_id = cliente_id
        self.tipo       = tipo
        self.nombre     = nombre

        self.setWindowTitle(f"Detalle — {nombre}")
        self.setMinimumSize(820, 680)
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))

        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(900, 720)
        self.move(screen.center().x() - 450, screen.center().y() - 360)

        main = QVBoxLayout(self)
        main.setContentsMargins(16, 16, 16, 16)

        # Título cliente
        lbl_titulo = QLabel(f"{'Monotributista' if tipo == 'mono' else 'Resp. Inscripto'}: {nombre}")
        lbl_titulo.setStyleSheet("font-size:14px; font-weight:bold; padding:4px 0;")
        main.addWidget(lbl_titulo)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # ── Sección superior ──────────────────────────────────
        top = QWidget()
        top_layout = QHBoxLayout(top)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Contacto
        grp_contacto = QGroupBox("Datos de contacto")
        g_c = QGridLayout()
        self.inp = {}
        campos = [
            ("cel",   "Teléfono"),
            ("mail",  "Mail"),
            ("banco", "Banco"),
            ("cbu",   "CBU"),
        ]
        for i, (key, lbl) in enumerate(campos):
            g_c.addWidget(QLabel(f"{lbl}:"), i, 0)
            w = QLineEdit()
            self.inp[key] = w
            g_c.addWidget(w, i, 1)
        g_c.addWidget(QLabel("Notas:"), len(campos), 0, Qt.AlignmentFlag.AlignTop)
        self.inp_notas = QTextEdit()
        self.inp_notas.setFixedHeight(60)
        g_c.addWidget(self.inp_notas, len(campos), 1)
        grp_contacto.setLayout(g_c)

        # Honorarios
        grp_hon = QGroupBox("Honorarios")
        g_h = QVBoxLayout()
        h_row = QHBoxLayout()
        h_row.addWidget(QLabel("Honorario mensual ($):"))
        self.inp_hon = QLineEdit()
        self.inp_hon.setPlaceholderText("0.00")
        self.inp_hon.setFixedWidth(120)
        h_row.addWidget(self.inp_hon)
        h_row.addStretch()
        g_h.addLayout(h_row)

        btn_cuota = QPushButton("Cargar cuota del mes actual")
        btn_cuota.setStyleSheet("background:#1a5276; color:white; padding:6px 12px; border-radius:4px;")
        btn_cuota.clicked.connect(self._cargar_cuota)
        g_h.addWidget(btn_cuota)

        self.lbl_saldo = QLabel("Saldo: —")
        self.lbl_saldo.setStyleSheet("font-weight:bold; font-size:13px;")
        g_h.addWidget(self.lbl_saldo)
        g_h.addStretch()

        btn_guardar_datos = QPushButton("Guardar datos de contacto")
        btn_guardar_datos.clicked.connect(self._guardar_datos)
        g_h.addWidget(btn_guardar_datos)

        grp_hon.setLayout(g_h)

        top_layout.addWidget(grp_contacto, 3)
        top_layout.addWidget(grp_hon, 2)

        # ── Sección inferior: cuenta corriente ───────────────
        grp_cc = QGroupBox("Cuenta corriente")
        g_cc = QVBoxLayout()

        self.table_cc = QTableWidget()
        self.table_cc.setColumnCount(6)
        self.table_cc.setHorizontalHeaderLabels(
            ["ID", "Fecha", "Descripción", "Debe", "Haber", "Saldo"]
        )
        self.table_cc.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_cc.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_cc.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_cc.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table_cc.verticalHeader().setVisible(False)
        g_cc.addWidget(self.table_cc)

        btn_row = QHBoxLayout()
        btn_nuevo_debe  = QPushButton("+ Cargo manual")
        btn_nuevo_haber = QPushButton("+ Registrar pago")
        btn_nuevo_haber.setStyleSheet("background:#1e8449; color:white; padding:5px 10px; border-radius:4px;")
        btn_nuevo_debe.setStyleSheet("background:#922b21; color:white; padding:5px 10px; border-radius:4px;")
        btn_eliminar    = QPushButton("Eliminar movimiento")
        btn_nuevo_debe.clicked.connect(lambda: self._nuevo_mov("debe"))
        btn_nuevo_haber.clicked.connect(lambda: self._nuevo_mov("haber"))
        btn_eliminar.clicked.connect(self._eliminar_mov)
        for b in (btn_nuevo_debe, btn_nuevo_haber, btn_eliminar):
            btn_row.addWidget(b)
        g_cc.addLayout(btn_row)
        grp_cc.setLayout(g_cc)

        splitter.addWidget(top)
        splitter.addWidget(grp_cc)
        splitter.setSizes([260, 420])
        main.addWidget(splitter)

        self._cargar_todo()

    # ── helpers ──────────────────────────────────────────────

    def _cargar_todo(self):
        det = get_detalle(self.tipo, self.cliente_id)
        for key in ("cel", "mail", "banco", "cbu"):
            self.inp[key].setText(det[key])
        self.inp_notas.setPlainText(det["notas"])
        self.inp_hon.setText(str(det["honorarios"]) if det["honorarios"] else "")
        self._reload_cc()

    def _reload_cc(self):
        movs = get_movimientos(self.tipo, self.cliente_id)
        self.table_cc.setRowCount(len(movs))
        saldo = 0.0
        for r_i, (mov_id, fecha, desc, debe, haber) in enumerate(movs):
            saldo += debe - haber
            vals = [str(mov_id), fecha, desc,
                    f"${debe:,.2f}" if debe else "",
                    f"${haber:,.2f}" if haber else "",
                    f"${saldo:,.2f}"]
            for c_i, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if c_i == 3 and debe:
                    item.setBackground(QColor("#fdecea"))
                elif c_i == 4 and haber:
                    item.setBackground(QColor("#eafaf1"))
                if c_i == 5:
                    item.setBackground(
                        QColor("#fdecea") if saldo > 0 else QColor("#eafaf1")
                    )
                self.table_cc.setItem(r_i, c_i, item)

        color = "#922b21" if saldo > 0 else "#1e8449"
        signo = "Debe" if saldo > 0 else "A favor"
        self.lbl_saldo.setText(f"Saldo actual: {signo}  ${abs(saldo):,.2f}")
        self.lbl_saldo.setStyleSheet(f"font-weight:bold; font-size:13px; color:{color};")
        self.table_cc.scrollToBottom()

    def _guardar_datos(self):
        try:
            hon = float(self.inp_hon.text().replace(",", ".")) if self.inp_hon.text().strip() else 0.0
        except ValueError:
            hon = 0.0
        save_detalle(self.tipo, self.cliente_id, {
            "cel":        self.inp["cel"].text().strip(),
            "mail":       self.inp["mail"].text().strip(),
            "banco":      self.inp["banco"].text().strip(),
            "cbu":        self.inp["cbu"].text().strip(),
            "honorarios": hon,
            "notas":      self.inp_notas.toPlainText().strip(),
        })
        QMessageBox.information(self, "Guardado", "Datos actualizados correctamente.")

    def _cargar_cuota(self):
        try:
            hon = float(self.inp_hon.text().replace(",", "."))
        except ValueError:
            QMessageBox.warning(self, "Error",
                "Guardá primero el honorario mensual del cliente.")
            return
        if hon <= 0:
            QMessageBox.warning(self, "Error",
                "El honorario mensual es 0. Configuralo antes de cargar la cuota.")
            return

        hoy = date.today()
        mes_nombre = MESES[hoy.month - 1]
        desc = f"Honorarios {mes_nombre} {hoy.year}"

        if QMessageBox.question(
            self, "Cargar cuota",
            f"¿Cargar cuota de  ${hon:,.2f}  ({desc})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            add_movimiento(
                self.tipo, self.cliente_id,
                hoy.isoformat(), desc,
                debe=hon, haber=0.0
            )
            self._reload_cc()

    def _nuevo_mov(self, debe_o_haber: str):
        dlg = DialogMovimiento(self, debe_o_haber)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_data()
            if not d["descripcion"]:
                QMessageBox.warning(self, "Error", "La descripción no puede estar vacía.")
                return
            if d["debe"] == 0 and d["haber"] == 0:
                QMessageBox.warning(self, "Error", "El monto no puede ser 0.")
                return
            add_movimiento(
                self.tipo, self.cliente_id,
                d["fecha"], d["descripcion"],
                d["debe"], d["haber"]
            )
            self._reload_cc()

    def _eliminar_mov(self):
        row = self.table_cc.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Error", "Seleccioná un movimiento para eliminar.")
            return
        mov_id = int(self.table_cc.item(row, 0).text())
        desc   = self.table_cc.item(row, 2).text()
        if QMessageBox.question(
            self, "Eliminar movimiento",
            f"¿Eliminar '{desc}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            del_movimiento(mov_id)
            self._reload_cc()
