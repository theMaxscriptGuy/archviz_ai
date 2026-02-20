from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from archviz_app.ui.widgets import CameraAnglesTable, FileListWidget, LabeledTextArea


class RoomEditor(QWidget):
    def __init__(self, *, parent=None):
        super().__init__(parent)
        self.files = FileListWidget("Room plan / reference files")
        self.finishes = LabeledTextArea(
            "Room finishes (colors/materials)",
            placeholder="Example: Walnut floor, off-white walls, brass accents…",
        )
        self.angles = CameraAnglesTable("Room camera angles")

        layout = QVBoxLayout()
        layout.addWidget(self.files)
        layout.addWidget(self.finishes)
        layout.addWidget(self.angles)
        self.setLayout(layout)

    def data(self) -> dict:
        return {
            "files": self.files.paths(),
            "finishes": self.finishes.value(),
            "angles": self.angles.values(),
        }


class InteriorTab(QWidget):
    def __init__(self, *, parent=None):
        super().__init__(parent)

        self.room_list = QListWidget()
        self.room_list.currentItemChanged.connect(self._on_room_selected)

        add_btn = QPushButton("Add room")
        rm_btn = QPushButton("Remove room")
        add_btn.clicked.connect(self.add_room)
        rm_btn.clicked.connect(self.remove_room)

        left_header = QHBoxLayout()
        left_header.addWidget(add_btn)
        left_header.addWidget(rm_btn)
        left_header.addStretch(1)

        left = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addLayout(left_header)
        left_layout.addWidget(self.room_list)
        left.setLayout(left_layout)

        self.editor = RoomEditor()

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(self.editor)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

        self._rooms_state: dict[str, dict] = {}

        # Start with one room
        self.add_room(default_name="Living Room")

    def add_room(self, *, default_name: str | None = None) -> None:
        name = default_name or f"Room {self.room_list.count() + 1}"
        item = QListWidgetItem(name)
        self.room_list.addItem(item)
        self._rooms_state[name] = {"files": [], "finishes": "", "angles": []}
        self.room_list.setCurrentItem(item)

    def remove_room(self) -> None:
        item = self.room_list.currentItem()
        if not item:
            return
        name = item.text()
        row = self.room_list.row(item)
        self.room_list.takeItem(row)
        self._rooms_state.pop(name, None)
        if self.room_list.count() > 0:
            self.room_list.setCurrentRow(0)

    def _save_current(self) -> None:
        item = self.room_list.currentItem()
        if not item:
            return
        name = item.text()
        self._rooms_state[name] = self.editor.data()

    def _on_room_selected(self, current: QListWidgetItem | None, previous: QListWidgetItem | None) -> None:
        if previous:
            self._save_current()
        if not current:
            return
        data = self._rooms_state.get(current.text(), {"files": [], "finishes": "", "angles": []})
        # Rebuild editor by setting widget internals
        self.editor.files.list.clear()
        for p in data.get("files", []):
            self.editor.files.list.addItem(QListWidgetItem(p))

        self.editor.finishes.text.setPlainText(data.get("finishes", ""))

        self.editor.angles.table.setRowCount(0)
        for n, d in data.get("angles", []):
            self.editor.angles.add_row(n, d)

    def data(self) -> list[dict]:
        # Save current before exporting
        self._save_current()
        rooms: list[dict] = []
        for i in range(self.room_list.count()):
            name = self.room_list.item(i).text()
            state = self._rooms_state.get(name, {"files": [], "finishes": "", "angles": []})
            rooms.append({"name": name, **state})
        return rooms
