"""
MHonorarios.py
──────────────
Panel global de honorarios: todos los pagos de todos los clientes,
filtrable por tipo y período.
"""

import os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QGroupBox, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QColor, QGuiApplication

from MClienteDetalle import get_conn, init_db, DB_PATH, LOGO_PATH, MESES

import sys


def _nombre_cliente(tipo: str, cliente_id: int) -> str:
    """Busca el nombre del cliente en su tabla correspondiente."""
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
    try:
        if tipo == "mono":
            db = os.path.join(data_dir, "datos_monot.db")
            with sqlite3.connect(db) as conn:
                row = conn.execute(
                    "SELECT nombre FROM monotributistas WHERE id=?", (cliente_id,)
                ).fetchone()
        else:
            # Nombre de tabla genérico (sin nombre personal hardcodeado)
            db = os.path.join(data_dir, "datos_resp.db")
            with sqlite3.connect(db) as conn:
                row = conn.execute(
                    "SELECT razon_social FROM responsables_inscriptos WHERE id=?",
                    (cliente_id,)
                ).fetchone()
        return row[0] if row else f"#{cliente_id}"
    except Exception:
        return f"#{cliente_id}"


class PanelHonorarios(QWidget):
    def __init__(self):
        super().__init__()
        init_db()
        self.setWindowTitle("Honorarios Cobrados")

        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(1000, 680)
        self.move(screen.center().x() - 500, screen.center().y() - 340)

        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))

        main = QVBoxLayout(self)
        main.setContentsMargins(16, 16, 16, 16)

        # ── Filtros ───────────────────────────────────────────
        grp_f = QGroupBox("Filtros")
        f_row = QHBoxLayout()

        f_row.addWidget(QLabel("Tipo:"))
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(["Todos", "Monotributistas", "Responsables Inscriptos"])
        self.combo_tipo.currentIndexChanged.connect(self._cargar)
        f_row.addWidget(self.combo_tipo)

        f_row.addWidget(QLabel("Año:"))
        self.combo_anio = QComboBox()
        self.combo_anio.addItems(["Todos"] + [str(y) for y in range(2023, 2031)])
        self.combo_anio.currentIndexChanged.connect(self._cargar)
        f_row.addWidget(self.combo_anio)

        f_row.addWidget(QLabel("Mes:"))
        self.combo_mes = QComboBox()
        self.combo_mes.addItems(["Todos"] + MESES)
        self.combo_mes.currentIndexChanged.connect(self._cargar)
        f_row.addWidget(self.combo_mes)

        f_row.addWidget(QLabel("Buscar cliente:"))
        self.inp_buscar = QLineEdit()
        self.inp_buscar.setPlaceholderText("Nombre...")
        self.inp_buscar.textChanged.connect(self._cargar)
        f_row.addWidget(self.inp_buscar)

        btn_refresh = QPushButton("↻ Actualizar")
        btn_refresh.clicked.connect(self._cargar)
        f_row.addWidget(btn_refresh)

        grp_f.setLayout(f_row)
        main.addWidget(grp_f)

        # ── Tabla ─────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["Tipo", "Cliente", "Fecha", "Descripción", "Debe", "Haber", "Saldo acum."]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        main.addWidget(self.table)

        # ── Totales ───────────────────────────────────────────
        tot_row = QHBoxLayout()
        self.lbl_total_debe  = QLabel("Total cargado: $0.00")
        self.lbl_total_haber = QLabel("Total cobrado: $0.00")
        self.lbl_saldo_gral  = QLabel("Saldo pendiente: $0.00")
        for lbl in (self.lbl_total_debe, self.lbl_total_haber, self.lbl_saldo_gral):
            lbl.setStyleSheet("font-weight:bold; font-size:13px; padding: 4px 16px;")
            tot_row.addWidget(lbl)
        tot_row.addStretch()
        main.addLayout(tot_row)

        self._cargar()

    def _cargar(self):
        tipo_sel = self.combo_tipo.currentText()
        anio_sel = self.combo_anio.currentText()
        mes_sel  = self.combo_mes.currentText()
        buscar   = self.inp_buscar.text().strip().lower()

        with get_conn() as conn:
            rows = conn.execute(
                "SELECT tipo, cliente_id, fecha, descripcion, debe, haber "
                "FROM cuenta_corriente ORDER BY fecha, id"
            ).fetchall()

        if tipo_sel == "Monotributistas":
            rows = [r for r in rows if r[0] == "mono"]
        elif tipo_sel == "Responsables Inscriptos":
            rows = [r for r in rows if r[0] == "resp"]

        if anio_sel != "Todos":
            rows = [r for r in rows if r[2].startswith(anio_sel)]
        if mes_sel != "Todos":
            mes_num = str(MESES.index(mes_sel) + 1).zfill(2)
            rows = [r for r in rows if len(r[2]) >= 7 and r[2][5:7] == mes_num]

        filas_final = []
        cache_nombres = {}
        for tipo, cid, fecha, desc, debe, haber in rows:
            key = (tipo, cid)
            if key not in cache_nombres:
                cache_nombres[key] = _nombre_cliente(tipo, cid)
            nombre = cache_nombres[key]
            if buscar and buscar not in nombre.lower():
                continue
            filas_final.append((tipo, nombre, fecha, desc, debe, haber))

        saldos = {}
        filas_con_saldo = []
        for tipo, nombre, fecha, desc, debe, haber in filas_final:
            k = (tipo, nombre)
            saldos[k] = saldos.get(k, 0.0) + debe - haber
            filas_con_saldo.append((tipo, nombre, fecha, desc, debe, haber, saldos[k]))

        self.table.setRowCount(len(filas_con_saldo))
        total_debe = total_haber = 0.0

        for r_i, (tipo, nombre, fecha, desc, debe, haber, saldo) in enumerate(filas_con_saldo):
            tipo_txt = "Mono" if tipo == "mono" else "RI"
            vals = [
                tipo_txt, nombre, fecha, desc,
                f"${debe:,.2f}" if debe else "",
                f"${haber:,.2f}" if haber else "",
                f"${saldo:,.2f}"
            ]
            for c_i, v in enumerate(vals):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if c_i == 4 and debe:
                    item.setBackground(QColor("#fdecea"))
                if c_i == 5 and haber:
                    item.setBackground(QColor("#eafaf1"))
                if c_i == 6:
                    item.setBackground(
                        QColor("#fdecea") if saldo > 0 else QColor("#eafaf1")
                    )
                self.table.setItem(r_i, c_i, item)
            total_debe  += debe
            total_haber += haber

        saldo_gral = total_debe - total_haber
        self.lbl_total_debe.setText(f"Total cargado:   ${total_debe:,.2f}")
        self.lbl_total_haber.setText(f"Total cobrado:   ${total_haber:,.2f}")
        color = "#922b21" if saldo_gral > 0 else "#1e8449"
        self.lbl_saldo_gral.setText(f"Saldo pendiente: ${saldo_gral:,.2f}")
        self.lbl_saldo_gral.setStyleSheet(
            f"font-weight:bold; font-size:13px; padding:4px 16px; color:{color};"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = PanelHonorarios()
    w.show()
    sys.exit(app.exec())
