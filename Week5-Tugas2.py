# ============================================================
# Nama  : Lalu Ahmad Purwadi
# NIM   : F1D02310115
# Kelas : C
# Tugas : T3-Week5 — Task Manager (QMainWindow, Dialog & QSS)
# ============================================================

import sys, json, os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QDialog, QFormLayout, QLineEdit, QComboBox, QDateEdit,
    QPushButton, QLabel, QToolBar, QMessageBox, QFileDialog, QDialogButtonBox,
    QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QAction, QColor, QBrush, QFont, QKeySequence, QPalette

# ── QSS ──────────────────────────────────────────────────────────────────────
QSS = """
QMainWindow, QWidget { background:#F4F6F9; color:#1A1A1A;
    font-family:'Segoe UI',Arial,sans-serif; font-size:13px; }
QMenuBar { background:#2D3748; color:#fff; padding:2px 4px; }
QMenuBar::item { background:transparent; padding:6px 14px; border-radius:4px; }
QMenuBar::item:selected, QMenuBar::item:pressed { background:#4A5568; }
QMenu { background:#2D3748; color:#fff; border:1px solid #4A5568;
    border-radius:6px; padding:4px; }
QMenu::item { padding:7px 28px 7px 16px; border-radius:4px; }
QMenu::item:selected { background:#4A90D9; }
QMenu::separator { height:1px; background:#4A5568; margin:4px 8px; }
QToolBar { background:#EAECF0; border-bottom:1px solid #D0D5DD; padding:6px 8px; spacing:6px; }
QToolBar::separator { width:1px; background:#C0C8D4; margin:4px 6px; }
QPushButton#btn_add    { background:#28A745; color:#fff; border:none; border-radius:6px; padding:7px 16px; font-weight:bold; }
QPushButton#btn_add:hover { background:#218838; }
QPushButton#btn_edit   { background:#4A90D9; color:#fff; border:none; border-radius:6px; padding:7px 16px; font-weight:bold; }
QPushButton#btn_edit:hover { background:#2E7FC1; }
QPushButton#btn_edit:disabled, QPushButton#btn_delete:disabled { background:#B0BEC5; color:#ECEFF1; }
QPushButton#btn_delete { background:#DC3545; color:#fff; border:none; border-radius:6px; padding:7px 16px; font-weight:bold; }
QPushButton#btn_delete:hover { background:#C82333; }
QComboBox { background:white; border:1px solid #CED4DA; border-radius:6px; padding:6px 10px; min-width:100px; }
QComboBox::drop-down { border:none; width:22px; }
QComboBox QAbstractItemView { background:white; color:#1A1A1A; selection-background-color:#4A90D9; }
QLineEdit#search_box { background:white; border:1px solid #CED4DA; border-radius:6px; padding:6px 10px; min-width:160px; }
QTableWidget { background:#fff; gridline-color:#E2E8F0; border:1px solid #D0D5DD;
    selection-background-color:#BEE3F8; selection-color:#1A1A1A; }
QTableWidget::item { padding:8px 12px; border-bottom:1px solid #EDF2F7; }
QHeaderView::section { background:#2D3748; color:#fff; font-weight:bold;
    padding:10px 12px; border:none; border-right:1px solid #4A5568; }
QStatusBar { background:#EAECF0; border-top:1px solid #D0D5DD; font-size:12px; padding:2px 8px; }
QDialog { background:#fff; color:#1A1A1A; }
QDialog QLineEdit, QDialog QComboBox, QDialog QDateEdit {
    background:white; border:1px solid #CED4DA; border-radius:5px;
    padding:7px 10px; min-width:220px; }
QDialog QLineEdit:focus, QDialog QComboBox:focus, QDialog QDateEdit:focus { border:1.5px solid #4A90D9; }
QDialogButtonBox QPushButton { min-width:80px; padding:7px 18px; border-radius:5px; font-weight:bold; }
QScrollBar:vertical { background:#F4F6F9; width:10px; border-radius:5px; }
QScrollBar::handle:vertical { background:#B0BEC5; border-radius:5px; min-height:30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
"""

# Warna baris & badge per prioritas
ROW_BG   = {"High": "#FFF5F5", "Medium": "#FFFBF0", "Low": "#F0FFF4"}
BADGE_BG = {"High": "#DC3545", "Medium": "#FFC107", "Low": "#28A745"}
BADGE_FG = {"High": "#FFFFFF", "Medium": "#1A1A1A", "Low": "#FFFFFF"}


# ── Dialog Tambah / Edit Task ─────────────────────────────────────────────────
class TaskDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Tambah Task" if data is None else "Edit Task")
        self.setMinimumWidth(360)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 16)

        lbl = QLabel("Tambah Task Baru" if data is None else "Edit Task")
        lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        layout.addWidget(lbl)

        form = QFormLayout()
        self.f_judul    = QLineEdit(placeholderText="Masukkan judul task...")
        self.f_prioritas = QComboBox(); self.f_prioritas.addItems(["High", "Medium", "Low"])
        self.f_status   = QComboBox();  self.f_status.addItems(["Todo", "In Progress", "Done"])
        self.f_due      = QDateEdit(QDate.currentDate(), calendarPopup=True, displayFormat="yyyy-MM-dd")
        for label, widget in [("Judul Task:", self.f_judul), ("Prioritas:", self.f_prioritas),
                               ("Status:", self.f_status), ("Due Date:", self.f_due)]:
            form.addRow(label, widget)
        layout.addLayout(form)

        if data:
            self.f_judul.setText(data.get("judul", ""))
            self.f_prioritas.setCurrentText(data.get("prioritas", "Medium"))
            self.f_status.setCurrentText(data.get("status", "Todo"))
            self.f_due.setDate(QDate.fromString(data.get("due_date", ""), "yyyy-MM-dd"))

        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self._accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def _accept(self):
        if not self.f_judul.text().strip():
            QMessageBox.warning(self, "Peringatan", "Judul task tidak boleh kosong!")
            return
        self.accept()

    def get_data(self):
        return {"judul": self.f_judul.text().strip(), "prioritas": self.f_prioritas.currentText(),
                "status": self.f_status.currentText(), "due_date": self.f_due.date().toString("yyyy-MM-dd")}


# ── Main Window ───────────────────────────────────────────────────────────────
class TaskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.resize(960, 580)
        self.tasks      = []
        self.data_file  = "tasks.json"
        self._filter    = "Semua"
        self._search    = ""

        self._build_menu()
        self._build_toolbar()
        self._build_table()
        self._build_statusbar()
        self.setStyleSheet(QSS)
        self._load_data()
        self._refresh()

    # ── Menu ─────────────────────────────────────────────────────────────────
    def _build_menu(self):
        mb = self.menuBar()
        # File menu
        m = mb.addMenu("File")
        self._action(m, "Muat dari JSON", "Ctrl+O", self._menu_load)
        self._action(m, "Simpan ke JSON",  "Ctrl+S", self._save)
        m.addSeparator()
        self._action(m, "Keluar", "Ctrl+Q", self.close)
        # Task menu
        m = mb.addMenu("Task")
        self._action(m, "Tambah Task", "Ctrl+N", self._add)
        self._action(m, "Edit Task",   "Ctrl+E", self._edit)
        m.addSeparator()
        self._action(m, "Hapus Task",  "Delete", self._delete)
        # Help menu
        m = mb.addMenu("Help")
        self._action(m, "Tentang", None, lambda: QMessageBox.about(
            self, "Tentang", "<b>Task Manager v1.0</b><br>PySide6<br><br>"
            "<i>Nama: Lalu Ahmad Purwadi | NIM: F1D02310115 | Kelas: C</i>"))

    def _action(self, menu, text, shortcut, slot):
        a = QAction(text, self)
        if shortcut: a.setShortcut(QKeySequence(shortcut))
        a.triggered.connect(slot)
        menu.addAction(a)

    # ── Toolbar ──────────────────────────────────────────────────────────────
    def _build_toolbar(self):
        tb = QToolBar(movable=False)
        tb.setIconSize(QSize(16, 16))
        self.addToolBar(tb)

        self.btn_add    = self._tb_btn(tb, "btn_add",    "+ Add Task", self._add)
        self.btn_edit   = self._tb_btn(tb, "btn_edit",   "✏  Edit",   self._edit,   False)
        self.btn_delete = self._tb_btn(tb, "btn_delete", "🗑  Delete", self._delete, False)
        tb.addSeparator()

        tb.addWidget(QLabel("  Filter: "))
        self.combo_filter = QComboBox()
        self.combo_filter.addItems(["Semua", "High", "Medium", "Low", "Todo", "In Progress", "Done"])
        self.combo_filter.currentTextChanged.connect(lambda t: self._set_filter(t))
        tb.addWidget(self.combo_filter)

        self.search_box = QLineEdit(objectName="search_box", placeholderText="🔍  Cari task...")
        self.search_box.textChanged.connect(lambda t: self._set_search(t))
        tb.addWidget(self.search_box)

    def _tb_btn(self, tb, name, text, slot, enabled=True):
        btn = QPushButton(text, objectName=name)
        btn.clicked.connect(slot)
        btn.setEnabled(enabled)
        tb.addWidget(btn)
        return btn

    # ── Table ────────────────────────────────────────────────────────────────
    def _build_table(self):
        self.table = QTableWidget(columnCount=5)
        self.table.setHorizontalHeaderLabels(["No", "Judul Task", "Prioritas", "Status", "Due Date"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        hh = self.table.horizontalHeader()
        for col, mode, w in [(0, QHeaderView.ResizeMode.Fixed, 60),
                              (1, QHeaderView.ResizeMode.Stretch, None),
                              (2, QHeaderView.ResizeMode.Fixed, 110),
                              (3, QHeaderView.ResizeMode.Fixed, 120),
                              (4, QHeaderView.ResizeMode.Fixed, 120)]:
            hh.setSectionResizeMode(col, mode)
            if w: self.table.setColumnWidth(col, w)
        self.table.itemSelectionChanged.connect(self._on_select)
        self.table.doubleClicked.connect(self._edit)
        self.setCentralWidget(self.table)

    # ── StatusBar ────────────────────────────────────────────────────────────
    def _build_statusbar(self):
        self.lbl_stat  = QLabel()
        self.lbl_file  = QLabel(self.data_file)
        self.lbl_file.setStyleSheet("color:#666;")
        self.statusBar().addWidget(self.lbl_stat, 1)
        self.statusBar().addPermanentWidget(self.lbl_file)

    # ── Data ─────────────────────────────────────────────────────────────────
    def _load_data(self):
        if os.path.exists(self.data_file):
            try:
                self.tasks = json.load(open(self.data_file, encoding="utf-8"))
            except Exception:
                self.tasks = []
        else:
            self.tasks = [
                {"judul": "Buat laporan praktikum", "prioritas": "High",   "status": "In Progress", "due_date": "2026-04-01"},
                {"judul": "Review materi PySide6",  "prioritas": "Medium", "status": "Todo",        "due_date": "2026-04-05"},
                {"judul": "Push code ke GitHub",    "prioritas": "Low",    "status": "Done",        "due_date": "2026-03-30"},
            ]

    def _save(self):
        try:
            json.dump(self.tasks, open(self.data_file, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
            self.statusBar().showMessage("✅  Data berhasil disimpan.", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal menyimpan: {e}")

    def _menu_load(self):
        path, _ = QFileDialog.getOpenFileName(self, "Muat File JSON", "", "JSON Files (*.json)")
        if path:
            try:
                self.tasks = json.load(open(path, encoding="utf-8"))
                self.data_file = os.path.basename(path)
                self.lbl_file.setText(self.data_file)
                self._refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal memuat: {e}")

    # ── Refresh Table ─────────────────────────────────────────────────────────
    def _filtered(self):
        for i, t in enumerate(self.tasks):
            f = self._filter
            if f != "Semua":
                if f in ("High","Medium","Low") and t["prioritas"] != f: continue
                if f in ("Todo","In Progress","Done") and t["status"] != f: continue
            if self._search and self._search.lower() not in t["judul"].lower(): continue
            yield i, t

    @staticmethod
    def _make_cell(text, bg_hex, fg_hex="#1A1A1A", align=None, bold=False):
        it = QTableWidgetItem(text)
        it.setBackground(QBrush(QColor(bg_hex)))
        it.setForeground(QBrush(QColor(fg_hex)))
        if align: it.setTextAlignment(align)
        if bold:  it.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        return it

    def _refresh(self):
        rows = list(self._filtered())
        self.table.setRowCount(len(rows))
        for row, (orig, task) in enumerate(rows):
            p      = task["prioritas"]
            row_bg = ROW_BG.get(p, "#FFFFFF")

            no = self._make_cell(str(row+1), row_bg, align=Qt.AlignmentFlag.AlignCenter)
            no.setData(Qt.ItemDataRole.UserRole, orig)
            self.table.setItem(row, 0, no)
            self.table.setItem(row, 1, self._make_cell(task["judul"], row_bg))
            self.table.setItem(row, 2, self._make_cell(p, BADGE_BG[p], BADGE_FG[p],
                                                       Qt.AlignmentFlag.AlignCenter, bold=True))
            self.table.setItem(row, 3, self._make_cell(
                "Done ✓" if task["status"] == "Done" else task["status"], row_bg))
            self.table.setItem(row, 4, self._make_cell(task["due_date"], row_bg))
            self.table.setRowHeight(row, 44)

        total = len(self.tasks)
        done  = sum(1 for t in self.tasks if t["status"] == "Done")
        prog  = sum(1 for t in self.tasks if t["status"] == "In Progress")
        todo  = sum(1 for t in self.tasks if t["status"] == "Todo")
        self.lbl_stat.setText(f"Total: {total} tasks | Done: {done} | In Progress: {prog} | Todo: {todo}")
        self._on_select()

    # ── CRUD ──────────────────────────────────────────────────────────────────
    def _add(self):
        dlg = TaskDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.tasks.append(dlg.get_data()); self._refresh(); self._save()

    def _edit(self):
        row = self.table.currentRow()
        if row < 0: return QMessageBox.information(self, "Info", "Pilih task yang ingin diedit.")
        idx = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        dlg = TaskDialog(self, self.tasks[idx])
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self.tasks[idx] = dlg.get_data(); self._refresh(); self._save()

    def _delete(self):
        row = self.table.currentRow()
        if row < 0: return QMessageBox.information(self, "Info", "Pilih task yang ingin dihapus.")
        idx  = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name = self.tasks[idx]["judul"]
        if QMessageBox.question(self, "Konfirmasi Hapus", f'Yakin hapus task:\n"{name}"?',
           QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            self.tasks.pop(idx); self._refresh(); self._save()

    def _set_filter(self, t): self._filter = t; self._refresh()
    def _set_search(self, t): self._search = t; self._refresh()
    def _on_select(self):
        ok = self.table.currentRow() >= 0
        self.btn_edit.setEnabled(ok); self.btn_delete.setEnabled(ok)

    # ── Close ─────────────────────────────────────────────────────────────────
    def closeEvent(self, e):
        r = QMessageBox.question(self, "Keluar", "Simpan data sebelum keluar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        if r == QMessageBox.StandardButton.Yes:   self._save(); e.accept()
        elif r == QMessageBox.StandardButton.No:  e.accept()
        else:                                      e.ignore()


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    p = app.palette()
    for role, color in [(QPalette.ColorRole.WindowText, "#111"), (QPalette.ColorRole.Text, "#111"),
                        (QPalette.ColorRole.Window, "#F4F6F9"), (QPalette.ColorRole.Base, "#FFF")]:
        p.setColor(role, QColor(color))
    app.setPalette(p)
    w = TaskManager(); w.show()
    sys.exit(app.exec())