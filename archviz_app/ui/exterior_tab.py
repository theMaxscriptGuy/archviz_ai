from __future__ import annotations

from PyQt6.QtWidgets import QVBoxLayout, QWidget

from archviz_app.ui.widgets import CameraAnglesTable, FileListWidget, LabeledTextArea


class ExteriorTab(QWidget):
    def __init__(self, *, parent=None):
        super().__init__(parent)

        self.plan_files = FileListWidget("Exterior plan / reference files")
        self.finishes = LabeledTextArea(
            "Exterior finishes (paint/material notes)",
            placeholder="Example: White stucco walls, dark grey stone plinth, black metal frames…",
        )
        self.angles = CameraAnglesTable("Exterior camera angles")
        self.angles.add_row("Front 45°", "Eye-level, 24mm")

        layout = QVBoxLayout()
        layout.addWidget(self.plan_files)
        layout.addWidget(self.finishes)
        layout.addWidget(self.angles)
        self.setLayout(layout)

    def data(self) -> dict:
        return {
            "plan_files": self.plan_files.paths(),
            "finishes": self.finishes.value(),
            "angles": self.angles.values(),
        }
