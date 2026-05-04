"""
M8LSDConfig.py — Configuración del Libro de Sueldos Digital
=============================================================
Persistencia en Data/lsd.db (SQLite).

Tablas:
  empleador_lsd   — Datos del empleador para el LSD (CUIT, tipo empresa, etc.)
  nomina_lsd      — Empleados con sus datos fijos (CUIL, CBU, códigos SICOSS, etc.)
  parametros_arca — Mapeo conceptos del liquidador -> códigos ARCA
  tope_anses      — Tope de base imponible por período (AAAAMM)
  historial_lsd   — Registro de archivos TXT generados

Se accede desde M9LSDExport (lectura) y desde este módulo (ABM completo).
"""

import os
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QTabWidget, QCheckBox, QApplication,
    QDialog, QDialogButtonBox, QFormLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QGuiApplication, QFont

DATA_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Data")
DB_PATH   = os.path.join(DATA_DIR, "lsd.db")
LOGO_PATH = os.path.join(DATA_DIR, "logo1.jpg")

# ── Opciones fijas ────────────────────────────────────────────
TIPO_EMP_OPTS = [
    ("1", "Decreto 814/01 Art.2 Inc.B (Comercio)"),
    ("0", "Administración Pública"),
    ("2", "Servicios Eventuales Inc.B"),
    ("4", "Decreto 814/01 Art.2 Inc.A"),
    ("5", "Servicios Eventuales Inc.A"),
    ("7", "Enseñanza Privada"),
    ("8", "Decreto 1212/03 – AFA Clubes"),
]
FORMA_PAGO_OPTS = [
    ("1", "Efectivo"),
    ("2", "Cheque"),
    ("3", "Acreditación en cuenta"),
    ("4", "Pago externo"),
]

# Conceptos ARCA predeterminados para CCT 130/75 Empleados de Comercio
PARAMETROS_DEFAULT = [
    # (cod_empleador, descripcion, cod_arca, tipo, debcred)
    ("BASICO",    "Sueldo Básico",                   "110000", "REM",  "C"),
    ("ANTIG",     "Antigüedad",                       "160001", "REM",  "C"),
    ("ASIST_R",   "Asistencia y Puntualidad (Rem.)",  "170001", "REM",  "C"),
    ("ASIST_NR",  "Asistencia y Puntualidad (No R.)", "540000", "NR",   "C"),
    ("NO_REM",    "No Remunerativo (Acuerdo)",         "540000", "NR",   "C"),
    ("HEX50",     "Horas Extra 50%",                  "130001", "REM",  "C"),
    ("HEX100",    "Horas Extra 100%",                 "130002", "REM",  "C"),
    ("SAC",       "Sueldo Anual Complementario",      "120001", "REM",  "C"),
    ("JUB",       "Jubilación 11%",                   "810000", "DESC", "D"),
    ("LEY19032",  "Ley 19.032 – PAMI 3%",            "810001", "DESC", "D"),
    ("OSSOCIAL",  "Obra Social 3%",                   "810002", "DESC", "D"),
    ("SEC100",    "S.E.C. Art.100 CCT 130/75 2%",     "810004", "DESC", "D"),
    ("SEC101",    "S.E.C. Art.101 CCT 130/75 2%",     "810004", "DESC", "D"),
    ("SIND",      "Cuota Sindical",                   "810004", "DESC", "D"),
    ("CECLAC",    "Aporte Caja CECLAC",               "820000", "DESC", "D"),
]


# ════════════════════════════════════════════════════════════════
# BASE DE DATOS
# ════════════════════════════════════════════════════════════════

def get_conn() -> sqlite3.Connection:
    os.makedirs(DATA_DIR, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Crea todas las tablas si no existen e inserta parámetros por defecto."""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS empleador_lsd (
                id             INTEGER PRIMARY KEY CHECK (id = 1),
                cuit           TEXT NOT NULL DEFAULT '',
                razon_social   TEXT DEFAULT '',
                tipo_empresa   TEXT DEFAULT '1',
                cod_actividad  TEXT DEFAULT '001',
                cod_modalidad  TEXT DEFAULT '102',
                cod_localidad  TEXT DEFAULT '00',
                ident_envio    TEXT DEFAULT 'SJ'
            );

            CREATE TABLE IF NOT EXISTS nomina_lsd (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                cuil             TEXT NOT NULL UNIQUE,
                apellido_nombre  TEXT DEFAULT '',
                legajo           TEXT DEFAULT '',
                fecha_ingreso    TEXT DEFAULT '',
                cbu              TEXT DEFAULT '',
                forma_pago       TEXT DEFAULT '1',
                cod_obra_social  TEXT DEFAULT '000000',
                cod_situacion    TEXT DEFAULT '01',
                cod_condicion    TEXT DEFAULT '01',
                cod_siniestrado  TEXT DEFAULT '00',
                scvo             INTEGER DEFAULT 1,
                cct              INTEGER DEFAULT 1,
                reduccion        INTEGER DEFAULT 0,
                activo           INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS parametros_arca (
                cod_empleador  TEXT PRIMARY KEY,
                descripcion    TEXT DEFAULT '',
                cod_arca       TEXT DEFAULT '',
                tipo           TEXT DEFAULT 'REM',
                debcred        TEXT DEFAULT 'C'
            );

            CREATE TABLE IF NOT EXISTS tope_anses (
                periodo  TEXT PRIMARY KEY,
                tope     REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS historial_lsd (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                cuil             TEXT,
                periodo          TEXT,
                nro_liquidacion  INTEGER,
                path_txt         TEXT,
                fecha_generacion TEXT
            );
        """)

        # Empleador vacío inicial
        conn.execute(
            "INSERT OR IGNORE INTO empleador_lsd (id) VALUES (1)"
        )

        # Parámetros ARCA por defecto (solo si la tabla está vacía)
        if conn.execute("SELECT COUNT(*) FROM parametros_arca").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO parametros_arca VALUES (?,?,?,?,?)",
                PARAMETROS_DEFAULT
            )


# ── Helpers de lectura ────────────────────────────────────────

def leer_empleador() -> dict:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM empleador_lsd WHERE id=1").fetchone()
    if not row:
        return {}
    keys = ["id", "cuit", "razon_social", "tipo_empresa", "cod_actividad",
            "cod_modalidad", "cod_localidad", "ident_envio"]
    return dict(zip(keys, row))


def leer_nomina(solo_activos: bool = True) -> list[dict]:
    q = "SELECT * FROM nomina_lsd"
    if solo_activos:
        q += " WHERE activo=1"
    q += " ORDER BY apellido_nombre"
    keys = ["id", "cuil", "apellido_nombre", "legajo", "fecha_ingreso",
            "cbu", "forma_pago", "cod_obra_social", "cod_situacion",
            "cod_condicion", "cod_siniestrado", "scvo", "cct",
            "reduccion", "activo"]
    with get_conn() as conn:
        rows = conn.execute(q).fetchall()
    return [dict(zip(keys, r)) for r in rows]


def leer_empleado_por_cuil(cuil: str) -> dict | None:
    keys = ["id", "cuil", "apellido_nombre", "legajo", "fecha_ingreso",
            "cbu", "forma_pago", "cod_obra_social", "cod_situacion",
            "cod_condicion", "cod_siniestrado", "scvo", "cct",
            "reduccion", "activo"]
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM nomina_lsd WHERE cuil=?", (cuil,)
        ).fetchone()
    return dict(zip(keys, row)) if row else None


def leer_parametros() -> list[dict]:
    keys = ["cod_empleador", "descripcion", "cod_arca", "tipo", "debcred"]
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM parametros_arca ORDER BY tipo, cod_empleador"
        ).fetchall()
    return [dict(zip(keys, r)) for r in rows]


def leer_tope(periodo: str) -> float | None:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT tope FROM tope_anses WHERE periodo=?", (periodo,)
        ).fetchone()
    return float(row[0]) if row else None


def guardar_historial(cuil: str, periodo: str, nro_liq: int,
                      path_txt: str, fecha: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO historial_lsd (cuil,periodo,nro_liquidacion,path_txt,fecha_generacion)"
            " VALUES (?,?,?,?,?)",
            (cuil, periodo, nro_liq, path_txt, fecha)
        )


# ════════════════════════════════════════════════════════════════
# HELPERS UI
# ════════════════════════════════════════════════════════════════

def _icon() -> QIcon:
    return QIcon(LOGO_PATH) if os.path.exists(LOGO_PATH) else QIcon()


def _centrar(w: QWidget, ancho: int, alto: int) -> None:
    w.resize(ancho, alto)
    geo = QGuiApplication.primaryScreen().availableGeometry()
    w.move(geo.center().x() - ancho // 2, geo.center().y() - alto // 2)


def _sep() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setStyleSheet("color: #cccccc;")
    return f


# ════════════════════════════════════════════════════════════════
# PESTAÑA EMPLEADOR
# ════════════════════════════════════════════════════════════════

class TabEmpleador(QWidget):
    def __init__(self):
        super().__init__()
        self._build()
        self._cargar()

    def _build(self):
        grp = QGroupBox("Datos del empleador para el LSD")
        form = QFormLayout()

        self.inp_cuit         = QLineEdit(); self.inp_cuit.setPlaceholderText("Sin guiones, 11 dígitos")
        self.inp_razon        = QLineEdit(); self.inp_razon.setPlaceholderText("Razón social o nombre")
        self.cmb_tipo_emp     = QComboBox()
        for val, lbl in TIPO_EMP_OPTS:
            self.cmb_tipo_emp.addItem(f"{val} – {lbl}", val)
        self.inp_cod_act      = QLineEdit(); self.inp_cod_act.setPlaceholderText("3 dígitos. Ej: 001")
        self.inp_cod_mod      = QLineEdit(); self.inp_cod_mod.setPlaceholderText("3 dígitos. Ej: 102")
        self.inp_cod_loc      = QLineEdit(); self.inp_cod_loc.setPlaceholderText("2 dígitos. Ej: 00")
        self.cmb_ident        = QComboBox()
        self.cmb_ident.addItems(["SJ – Liquidación + DJ", "RE – Solo rectifica DJ"])

        form.addRow("CUIT empleador *:", self.inp_cuit)
        form.addRow("Razón social:", self.inp_razon)
        form.addRow("Tipo empresa *:", self.cmb_tipo_emp)
        form.addRow("Cód. Actividad *:", self.inp_cod_act)
        form.addRow("Cód. Modalidad *:", self.inp_cod_mod)
        form.addRow("Cód. Localidad:", self.inp_cod_loc)
        form.addRow("Identificación envío:", self.cmb_ident)

        info = QLabel(
            "Estos datos se usan en el Registro 01 y Registro 04 de cada TXT.\n"
            "Solo necesitás configurarlos una vez."
        )
        info.setStyleSheet("color: #666; font-size: 11px;")
        info.setWordWrap(True)

        grp.setLayout(form)

        btn_guardar = QPushButton("💾  Guardar datos del empleador")
        btn_guardar.setStyleSheet(
            "background:#1a5276; color:white; padding:7px 16px; border-radius:4px;"
        )
        btn_guardar.clicked.connect(self._guardar)

        lay = QVBoxLayout(self)
        lay.addWidget(grp)
        lay.addWidget(info)
        lay.addSpacing(8)
        lay.addWidget(btn_guardar)
        lay.addStretch()
        lay.setContentsMargins(16, 16, 16, 16)

    def _cargar(self):
        d = leer_empleador()
        if not d:
            return
        self.inp_cuit.setText(d.get("cuit", ""))
        self.inp_razon.setText(d.get("razon_social", ""))
        self.inp_cod_act.setText(d.get("cod_actividad", "001"))
        self.inp_cod_mod.setText(d.get("cod_modalidad", "102"))
        self.inp_cod_loc.setText(d.get("cod_localidad", "00"))

        te = d.get("tipo_empresa", "1")
        for i in range(self.cmb_tipo_emp.count()):
            if self.cmb_tipo_emp.itemData(i) == te:
                self.cmb_tipo_emp.setCurrentIndex(i)
                break

        ie = d.get("ident_envio", "SJ")
        self.cmb_ident.setCurrentIndex(0 if ie == "SJ" else 1)

    def _guardar(self):
        cuit = self.inp_cuit.text().strip()
        if not cuit.isdigit() or len(cuit) != 11:
            QMessageBox.warning(self, "Error", "CUIT debe tener 11 dígitos numéricos.")
            return
        tipo_emp = self.cmb_tipo_emp.currentData()
        ident    = "SJ" if self.cmb_ident.currentIndex() == 0 else "RE"
        with get_conn() as conn:
            conn.execute(
                """UPDATE empleador_lsd SET
                   cuit=?, razon_social=?, tipo_empresa=?,
                   cod_actividad=?, cod_modalidad=?, cod_localidad=?,
                   ident_envio=? WHERE id=1""",
                (cuit,
                 self.inp_razon.text().strip(),
                 tipo_emp,
                 self.inp_cod_act.text().strip() or "001",
                 self.inp_cod_mod.text().strip() or "102",
                 self.inp_cod_loc.text().strip() or "00",
                 ident)
            )
        QMessageBox.information(self, "Guardado", "Datos del empleador guardados correctamente.")


# ════════════════════════════════════════════════════════════════
# DIÁLOGO EMPLEADO (alta / edición)
# ════════════════════════════════════════════════════════════════

class DialogEmpleado(QDialog):
    def __init__(self, parent, datos: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Empleado" if datos else "Nuevo empleado")
        self.setWindowIcon(_icon())
        self.resize(480, 520)
        self._datos = datos or {}
        self._build()
        if datos:
            self._cargar(datos)

    def _build(self):
        form = QFormLayout()

        self.inp_cuil     = QLineEdit(); self.inp_cuil.setPlaceholderText("Sin guiones, 11 dígitos")
        self.inp_nombre   = QLineEdit()
        self.inp_legajo   = QLineEdit()
        self.inp_ingreso  = QLineEdit(); self.inp_ingreso.setPlaceholderText("dd/mm/aaaa")
        self.inp_cbu      = QLineEdit(); self.inp_cbu.setPlaceholderText("22 dígitos (solo si pago acreditación)")
        self.cmb_fpago    = QComboBox()
        for val, lbl in FORMA_PAGO_OPTS:
            self.cmb_fpago.addItem(f"{val} – {lbl}", val)
        self.inp_cod_os   = QLineEdit(); self.inp_cod_os.setPlaceholderText("6 dígitos ARCA. Ej: 800803")
        self.inp_cod_sit  = QLineEdit("01"); self.inp_cod_sit.setPlaceholderText("2 dígitos SICOSS")
        self.inp_cod_cond = QLineEdit("01"); self.inp_cod_cond.setPlaceholderText("2 dígitos SICOSS")
        self.inp_cod_sin  = QLineEdit("00"); self.inp_cod_sin.setPlaceholderText("2 dígitos SICOSS")
        self.chk_scvo     = QCheckBox("SCVO (Seguro Colectivo Vida Obligatorio)"); self.chk_scvo.setChecked(True)
        self.chk_cct      = QCheckBox("Trabajador en CCT"); self.chk_cct.setChecked(True)
        self.chk_red      = QCheckBox("Corresponde reducción")
        self.chk_activo   = QCheckBox("Activo en la nómina"); self.chk_activo.setChecked(True)

        form.addRow("CUIL *:", self.inp_cuil)
        form.addRow("Apellido y Nombre *:", self.inp_nombre)
        form.addRow("Legajo:", self.inp_legajo)
        form.addRow("Fecha de ingreso:", self.inp_ingreso)
        form.addRow(_sep(), QLabel())
        form.addRow("Forma de pago:", self.cmb_fpago)
        form.addRow("CBU:", self.inp_cbu)
        form.addRow(_sep(), QLabel())
        form.addRow("Cód. Obra Social:", self.inp_cod_os)
        form.addRow("Cód. Situación:", self.inp_cod_sit)
        form.addRow("Cód. Condición:", self.inp_cod_cond)
        form.addRow("Cód. Siniestrado:", self.inp_cod_sin)
        form.addRow(_sep(), QLabel())
        form.addRow("", self.chk_scvo)
        form.addRow("", self.chk_cct)
        form.addRow("", self.chk_red)
        form.addRow("", self.chk_activo)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._validar_y_aceptar)
        btns.rejected.connect(self.reject)

        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(btns)
        lay.setContentsMargins(20, 16, 20, 16)

    def _cargar(self, d: dict):
        self.inp_cuil.setText(d.get("cuil", ""))
        self.inp_cuil.setReadOnly(True)  # no cambiar CUIL en edición
        self.inp_nombre.setText(d.get("apellido_nombre", ""))
        self.inp_legajo.setText(d.get("legajo", ""))
        self.inp_ingreso.setText(d.get("fecha_ingreso", ""))
        self.inp_cbu.setText(d.get("cbu", ""))
        self.inp_cod_os.setText(d.get("cod_obra_social", ""))
        self.inp_cod_sit.setText(d.get("cod_situacion", "01"))
        self.inp_cod_cond.setText(d.get("cod_condicion", "01"))
        self.inp_cod_sin.setText(d.get("cod_siniestrado", "00"))
        self.chk_scvo.setChecked(bool(d.get("scvo", 1)))
        self.chk_cct.setChecked(bool(d.get("cct", 1)))
        self.chk_red.setChecked(bool(d.get("reduccion", 0)))
        self.chk_activo.setChecked(bool(d.get("activo", 1)))
        fp = d.get("forma_pago", "1")
        for i in range(self.cmb_fpago.count()):
            if self.cmb_fpago.itemData(i) == fp:
                self.cmb_fpago.setCurrentIndex(i)
                break

    def _validar_y_aceptar(self):
        cuil = self.inp_cuil.text().strip()
        if not cuil.isdigit() or len(cuil) != 11:
            QMessageBox.warning(self, "Error", "CUIL debe tener 11 dígitos numéricos."); return
        if not self.inp_nombre.text().strip():
            QMessageBox.warning(self, "Error", "Apellido y Nombre es obligatorio."); return
        fp = self.cmb_fpago.currentData()
        cbu = self.inp_cbu.text().strip()
        if fp == "3" and (len(cbu) != 22 or not cbu.isdigit()):
            QMessageBox.warning(self, "Error",
                "Con forma de pago Acreditación, el CBU debe tener 22 dígitos."); return
        self.accept()

    def get_datos(self) -> dict:
        return {
            "cuil":             self.inp_cuil.text().strip(),
            "apellido_nombre":  self.inp_nombre.text().strip(),
            "legajo":           self.inp_legajo.text().strip(),
            "fecha_ingreso":    self.inp_ingreso.text().strip(),
            "cbu":              self.inp_cbu.text().strip(),
            "forma_pago":       self.cmb_fpago.currentData(),
            "cod_obra_social":  self.inp_cod_os.text().strip() or "000000",
            "cod_situacion":    self.inp_cod_sit.text().strip() or "01",
            "cod_condicion":    self.inp_cod_cond.text().strip() or "01",
            "cod_siniestrado":  self.inp_cod_sin.text().strip() or "00",
            "scvo":             1 if self.chk_scvo.isChecked() else 0,
            "cct":              1 if self.chk_cct.isChecked() else 0,
            "reduccion":        1 if self.chk_red.isChecked() else 0,
            "activo":           1 if self.chk_activo.isChecked() else 0,
        }


# ════════════════════════════════════════════════════════════════
# PESTAÑA NÓMINA
# ════════════════════════════════════════════════════════════════

class TabNomina(QWidget):
    COLS = ["CUIL", "Apellido y Nombre", "Legajo", "Forma Pago",
            "Cód. OS", "Situación", "Condición", "SCVO", "Activo"]

    def __init__(self):
        super().__init__()
        self._build()
        self.load_data()

    def _build(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.doubleClicked.connect(self._editar)

        btn_nuevo  = QPushButton("+ Nuevo empleado")
        btn_editar = QPushButton("✏ Editar")
        btn_baja   = QPushButton("✕ Dar de baja")
        btn_nuevo.setStyleSheet(
            "background:#1a5276; color:white; padding:5px 12px; border-radius:4px;"
        )
        btn_nuevo.clicked.connect(self._nuevo)
        btn_editar.clicked.connect(self._editar)
        btn_baja.clicked.connect(self._dar_baja)

        self.chk_inactivos = QCheckBox("Mostrar inactivos")
        self.chk_inactivos.stateChanged.connect(lambda _: self.load_data())

        btn_row = QHBoxLayout()
        btn_row.addWidget(btn_nuevo)
        btn_row.addWidget(btn_editar)
        btn_row.addWidget(btn_baja)
        btn_row.addStretch()
        btn_row.addWidget(self.chk_inactivos)

        hint = QLabel("  Doble clic para editar")
        hint.setStyleSheet("color: gray; font-size: 11px;")

        lay = QVBoxLayout(self)
        lay.addWidget(self.table)
        lay.addWidget(hint)
        lay.addLayout(btn_row)
        lay.setContentsMargins(12, 12, 12, 12)

    def load_data(self):
        solo_activos = not self.chk_inactivos.isChecked()
        self._rows = leer_nomina(solo_activos=solo_activos)
        self.table.setRowCount(len(self._rows))
        for ri, d in enumerate(self._rows):
            vals = [
                d["cuil"],
                d["apellido_nombre"],
                d["legajo"],
                dict(FORMA_PAGO_OPTS).get(d["forma_pago"], d["forma_pago"]),
                d["cod_obra_social"],
                d["cod_situacion"],
                d["cod_condicion"],
                "✔" if d["scvo"] else "",
                "Activo" if d["activo"] else "Baja",
            ]
            for ci, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if not d["activo"]:
                    item.setForeground(Qt.GlobalColor.gray)
                self.table.setItem(ri, ci, item)

    def _selected_idx(self) -> int:
        row = self.table.currentRow()
        return row if 0 <= row < len(self._rows) else -1

    def _nuevo(self):
        dlg = DialogEmpleado(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            d = dlg.get_datos()
            try:
                with get_conn() as conn:
                    conn.execute(
                        """INSERT INTO nomina_lsd
                           (cuil, apellido_nombre, legajo, fecha_ingreso, cbu,
                            forma_pago, cod_obra_social, cod_situacion,
                            cod_condicion, cod_siniestrado, scvo, cct,
                            reduccion, activo)
                           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                        (d["cuil"], d["apellido_nombre"], d["legajo"],
                         d["fecha_ingreso"], d["cbu"], d["forma_pago"],
                         d["cod_obra_social"], d["cod_situacion"],
                         d["cod_condicion"], d["cod_siniestrado"],
                         d["scvo"], d["cct"], d["reduccion"], d["activo"])
                    )
            except sqlite3.IntegrityError:
                QMessageBox.warning(self, "Duplicado",
                    f"Ya existe un empleado con CUIL {d['cuil']}.")
                return
            self.load_data()

    def _editar(self):
        idx = self._selected_idx()
        if idx < 0:
            QMessageBox.information(self, "Sin selección", "Seleccioná un empleado."); return
        d = self._rows[idx]
        dlg = DialogEmpleado(self, datos=d)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            nd = dlg.get_datos()
            with get_conn() as conn:
                conn.execute(
                    """UPDATE nomina_lsd SET
                       apellido_nombre=?, legajo=?, fecha_ingreso=?, cbu=?,
                       forma_pago=?, cod_obra_social=?, cod_situacion=?,
                       cod_condicion=?, cod_siniestrado=?, scvo=?, cct=?,
                       reduccion=?, activo=? WHERE cuil=?""",
                    (nd["apellido_nombre"], nd["legajo"], nd["fecha_ingreso"],
                     nd["cbu"], nd["forma_pago"], nd["cod_obra_social"],
                     nd["cod_situacion"], nd["cod_condicion"], nd["cod_siniestrado"],
                     nd["scvo"], nd["cct"], nd["reduccion"], nd["activo"],
                     nd["cuil"])
                )
            self.load_data()

    def _dar_baja(self):
        idx = self._selected_idx()
        if idx < 0:
            QMessageBox.information(self, "Sin selección", "Seleccioná un empleado."); return
        d = self._rows[idx]
        if QMessageBox.question(
            self, "Dar de baja",
            f"¿Marcar como inactivo a {d['apellido_nombre']}?\n"
            "Podrás reactivarlo editando el registro.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            with get_conn() as conn:
                conn.execute("UPDATE nomina_lsd SET activo=0 WHERE cuil=?", (d["cuil"],))
            self.load_data()


# ════════════════════════════════════════════════════════════════
# PESTAÑA PARÁMETROS ARCA
# ════════════════════════════════════════════════════════════════

class TabParametros(QWidget):
    COLS = ["Cód. Empleador", "Descripción", "Cód. ARCA", "Tipo", "D/C"]

    def __init__(self):
        super().__init__()
        self._build()
        self.load_data()

    def _build(self):
        info = QLabel(
            "Cada fila define cómo un concepto del liquidador se traduce a un código ARCA.\n"
            "Los códigos de empleador se usan en el Registro 03 del TXT.\n"
            "Los parámetros por defecto corresponden al CCT 130/75 Empleados de Comercio."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #444; font-size: 11px; padding: 4px 0;")

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        btn_edit    = QPushButton("✏ Editar seleccionado")
        btn_reset   = QPushButton("↺ Restablecer por defecto")
        btn_reset.setStyleSheet("color: #c0392b;")
        btn_edit.clicked.connect(self._editar)
        btn_reset.clicked.connect(self._resetear)

        btn_row = QHBoxLayout()
        btn_row.addWidget(btn_edit)
        btn_row.addStretch()
        btn_row.addWidget(btn_reset)

        lay = QVBoxLayout(self)
        lay.addWidget(info)
        lay.addWidget(self.table)
        lay.addLayout(btn_row)
        lay.setContentsMargins(12, 12, 12, 12)

    def load_data(self):
        self._rows = leer_parametros()
        self.table.setRowCount(len(self._rows))
        colores = {"REM": "#e8f5e9", "NR": "#fff8e1", "DESC": "#fce4ec"}
        for ri, d in enumerate(self._rows):
            vals = [d["cod_empleador"], d["descripcion"],
                    d["cod_arca"], d["tipo"], d["debcred"]]
            color = colores.get(d["tipo"], "#ffffff")
            for ci, v in enumerate(vals):
                item = QTableWidgetItem(str(v))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setBackground(Qt.GlobalColor.white)
                from PyQt6.QtGui import QColor
                item.setBackground(QColor(color))
                self.table.setItem(ri, ci, item)

    def _editar(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Sin selección", "Seleccioná una fila."); return
        d = self._rows[row]
        dlg = _DialogParametro(self, d)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            nd = dlg.get_datos()
            with get_conn() as conn:
                conn.execute(
                    "UPDATE parametros_arca SET descripcion=?, cod_arca=?, tipo=?, debcred=?"
                    " WHERE cod_empleador=?",
                    (nd["descripcion"], nd["cod_arca"],
                     nd["tipo"], nd["debcred"], nd["cod_empleador"])
                )
            self.load_data()

    def _resetear(self):
        if QMessageBox.question(
            self, "Restablecer",
            "¿Restablecer todos los parámetros ARCA a los valores por defecto del CCT 130/75?\n"
            "Se perderán los cambios personalizados.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            with get_conn() as conn:
                conn.execute("DELETE FROM parametros_arca")
                conn.executemany(
                    "INSERT INTO parametros_arca VALUES (?,?,?,?,?)",
                    PARAMETROS_DEFAULT
                )
            self.load_data()


class _DialogParametro(QDialog):
    def __init__(self, parent, d: dict):
        super().__init__(parent)
        self.setWindowTitle(f"Editar parámetro: {d['cod_empleador']}")
        self._cod = d["cod_empleador"]
        form = QFormLayout()
        self.inp_desc  = QLineEdit(d["descripcion"])
        self.inp_arca  = QLineEdit(d["cod_arca"])
        self.cmb_tipo  = QComboBox()
        self.cmb_tipo.addItems(["REM", "NR", "DESC"])
        self.cmb_tipo.setCurrentText(d["tipo"])
        self.cmb_dc    = QComboBox()
        self.cmb_dc.addItems(["C", "D"])
        self.cmb_dc.setCurrentText(d["debcred"])
        form.addRow("Descripción:", self.inp_desc)
        form.addRow("Cód. ARCA:", self.inp_arca)
        form.addRow("Tipo:", self.cmb_tipo)
        form.addRow("Déb/Créd:", self.cmb_dc)
        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay = QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(btns)
        lay.setContentsMargins(16, 16, 16, 16)

    def get_datos(self) -> dict:
        return {
            "cod_empleador": self._cod,
            "descripcion":   self.inp_desc.text().strip(),
            "cod_arca":      self.inp_arca.text().strip(),
            "tipo":          self.cmb_tipo.currentText(),
            "debcred":       self.cmb_dc.currentText(),
        }


# ════════════════════════════════════════════════════════════════
# PESTAÑA TOPE ANSeS
# ════════════════════════════════════════════════════════════════

class TabTopeANSeS(QWidget):
    COLS = ["Período (AAAAMM)", "Tope Base Imponible ($)"]

    def __init__(self):
        super().__init__()
        self._build()
        self.load_data()

    def _build(self):
        info = QLabel(
            "El tope ANSeS limita la Base Imponible 1 (aportes previsionales) de cada empleado.\n"
            "Se actualiza con cada paritaria o resolución. Ingresalo mes a mes antes de generar los TXT.\n"
            "Si no existe tope para un período, el sistema usa la remuneración bruta sin límite."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #444; font-size: 11px; padding: 4px 0;")

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        grp_nuevo = QGroupBox("Agregar / actualizar tope")
        g = QHBoxLayout()
        self.inp_periodo = QLineEdit(); self.inp_periodo.setPlaceholderText("AAAAMM  Ej: 202506")
        self.inp_tope    = QLineEdit(); self.inp_tope.setPlaceholderText("Ej: 2541000.99")
        btn_add = QPushButton("Guardar")
        btn_add.setStyleSheet(
            "background:#1a5276; color:white; padding:5px 12px; border-radius:4px;"
        )
        btn_add.clicked.connect(self._guardar_tope)
        g.addWidget(QLabel("Período:")); g.addWidget(self.inp_periodo)
        g.addWidget(QLabel("Tope $:"));  g.addWidget(self.inp_tope)
        g.addWidget(btn_add)
        grp_nuevo.setLayout(g)

        btn_del = QPushButton("🗑 Eliminar seleccionado")
        btn_del.clicked.connect(self._eliminar)

        lay = QVBoxLayout(self)
        lay.addWidget(info)
        lay.addWidget(self.table)
        lay.addWidget(grp_nuevo)
        lay.addWidget(btn_del)
        lay.setContentsMargins(12, 12, 12, 12)

    def load_data(self):
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT periodo, tope FROM tope_anses ORDER BY periodo DESC"
            ).fetchall()
        self.table.setRowCount(len(rows))
        for ri, (per, tope) in enumerate(rows):
            self.table.setItem(ri, 0, QTableWidgetItem(per))
            item = QTableWidgetItem(f"${tope:,.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.table.setItem(ri, 1, item)

    def _guardar_tope(self):
        per  = self.inp_periodo.text().strip()
        tope = self.inp_tope.text().strip().replace(",", ".")
        if len(per) != 6 or not per.isdigit():
            QMessageBox.warning(self, "Error", "Período debe tener 6 dígitos (AAAAMM)."); return
        try:
            tope_f = float(tope)
        except ValueError:
            QMessageBox.warning(self, "Error", "El tope debe ser un número."); return
        with get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO tope_anses VALUES (?,?)", (per, tope_f)
            )
        self.inp_periodo.clear(); self.inp_tope.clear()
        self.load_data()

    def _eliminar(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "Sin selección", "Seleccioná un período."); return
        per = self.table.item(row, 0).text()
        if QMessageBox.question(
            self, "Eliminar", f"¿Eliminar el tope del período {per}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            with get_conn() as conn:
                conn.execute("DELETE FROM tope_anses WHERE periodo=?", (per,))
            self.load_data()


# ════════════════════════════════════════════════════════════════
# PESTAÑA HISTORIAL
# ════════════════════════════════════════════════════════════════

class TabHistorial(QWidget):
    COLS = ["CUIL", "Período", "Nro. Liq.", "Archivo generado", "Fecha generación"]

    def __init__(self):
        super().__init__()
        self._build()
        self.load_data()

    def _build(self):
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLS))
        self.table.setHorizontalHeaderLabels(self.COLS)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        btn_ref = QPushButton("↻ Actualizar")
        btn_ref.clicked.connect(self.load_data)

        lay = QVBoxLayout(self)
        lay.addWidget(self.table)
        lay.addWidget(btn_ref)
        lay.setContentsMargins(12, 12, 12, 12)

    def load_data(self):
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT cuil, periodo, nro_liquidacion, path_txt, fecha_generacion"
                " FROM historial_lsd ORDER BY id DESC LIMIT 200"
            ).fetchall()
        self.table.setRowCount(len(rows))
        for ri, row in enumerate(rows):
            for ci, v in enumerate(row):
                item = QTableWidgetItem(str(v or ""))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(ri, ci, item)


# ════════════════════════════════════════════════════════════════
# VENTANA PRINCIPAL DE CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════

class VentanaLSDConfig(QWidget):
    """Ventana principal de configuración del LSD. Se abre desde M2."""

    def __init__(self, nombre_estudio: str = ""):
        super().__init__()
        init_db()
        self.setWindowTitle("Libro de Sueldos Digital — Configuración")
        self.setWindowIcon(_icon())
        _centrar(self, 860, 640)

        titulo = QLabel("⚙  Configuración del Libro de Sueldos Digital")
        titulo.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #1a5276; padding: 8px 0;"
        )

        tabs = QTabWidget()
        self.tab_emp    = TabEmpleador()
        self.tab_nom    = TabNomina()
        self.tab_param  = TabParametros()
        self.tab_tope   = TabTopeANSeS()
        self.tab_hist   = TabHistorial()

        tabs.addTab(self.tab_emp,   "🏢 Empleador")
        tabs.addTab(self.tab_nom,   "👥 Nómina")
        tabs.addTab(self.tab_param, "🗂 Parámetros ARCA")
        tabs.addTab(self.tab_tope,  "📊 Tope ANSeS")
        tabs.addTab(self.tab_hist,  "🕑 Historial TXT")

        lay = QVBoxLayout(self)
        lay.addWidget(titulo)
        lay.addWidget(tabs)
        lay.setContentsMargins(16, 12, 16, 16)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = VentanaLSDConfig()
    w.show()
    sys.exit(app.exec())
