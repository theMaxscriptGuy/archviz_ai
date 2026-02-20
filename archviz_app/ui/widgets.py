from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
)


class FileListWidget(QWidget):
    """Simple add/remove list of file paths."""

    def __init__(self, title: str, *, parent=None):
        super().__init__(parent)
        self.title = title
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        add_btn = QPushButton("Add…")
        rm_btn = QPushButton("Remove")

        add_btn.clicked.connect(self._add)
        rm_btn.clicked.connect(self._remove)

        header = QHBoxLayout()
        header.addWidget(QLabel(title))
        header.addStretch(1)
        header.addWidget(add_btn)
        header.addWidget(rm_btn)

        layout = QVBoxLayout()
        layout.addLayout(header)
        layout.addWidget(self.list)
        self.setLayout(layout)

    def _add(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self,
            f"Select files ({self.title})",
            "",
            "Documents (*.pdf *.png *.jpg *.jpeg *.webp);;All files (*.*)",
        )
        for f in files:
            self.list.addItem(QListWidgetItem(f))

    def _remove(self) -> None:
        for item in self.list.selectedItems():
            row = self.list.row(item)
            self.list.takeItem(row)

    def paths(self) -> list[str]:
        return [self.list.item(i).text() for i in range(self.list.count())]


class CameraAnglesTable(QWidget):
    def __init__(self, title: str, *, parent=None):
        super().__init__(parent)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Angle name", "Notes"])
        self.table.horizontalHeader().setStretchLastSection(True)

        add_btn = QPushButton("Add angle")
        rm_btn = QPushButton("Remove")
        add_btn.clicked.connect(self.add_row)
        rm_btn.clicked.connect(self.remove_selected)

        header = QHBoxLayout()
        header.addWidget(QLabel(title))
        header.addStretch(1)
        header.addWidget(add_btn)
        header.addWidget(rm_btn)

        layout = QVBoxLayout()
        layout.addLayout(header)
        layout.addWidget(self.table)
        self.setLayout(layout)

    def add_row(self, name: str = "", notes: str = "") -> None:
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.table.setItem(r, 0, QTableWidgetItem(name))
        self.table.setItem(r, 1, QTableWidgetItem(notes))

    def remove_selected(self) -> None:
        rows = sorted({idx.row() for idx in self.table.selectedIndexes()}, reverse=True)
        for r in rows:
            self.table.removeRow(r)

    def values(self) -> list[tuple[str, str]]:
        out: list[tuple[str, str]] = []
        for r in range(self.table.rowCount()):
            name = self.table.item(r, 0).text() if self.table.item(r, 0) else ""
            notes = self.table.item(r, 1).text() if self.table.item(r, 1) else ""
            if name.strip():
                out.append((name.strip(), notes.strip()))
        return out


class LabeledTextArea(QWidget):
    def __init__(self, title: str, *, placeholder: str = "", parent=None):
        super().__init__(parent)
        self.text = QTextEdit()
        self.text.setPlaceholderText(placeholder)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(title))
        layout.addWidget(self.text)
        self.setLayout(layout)

    def value(self) -> str:
        return self.text.toPlainText()


class LabeledLineEdit(QWidget):
    def __init__(self, title: str, *, placeholder: str = "", echo_password: bool = False, parent=None):
        super().__init__(parent)
        self.edit = QLineEdit()
        self.edit.setPlaceholderText(placeholder)
        if echo_password:
            self.edit.setEchoMode(QLineEdit.EchoMode.Password)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(title))
        layout.addWidget(self.edit)
        self.setLayout(layout)

    def value(self) -> str:
        return self.edit.text().strip()

    def set_value(self, v: str) -> None:
        self.edit.setText(v)
