from __future__ import annotations

import datetime as dt
from pathlib import Path

from PyQt6.QtWidgets import (
    QHBoxLayout,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from archviz_app.core.job_builder import build_render_job
from archviz_app.services.gemini_client import GeminiClient
from archviz_app.services.render_service import RenderService
from archviz_app.ui.exterior_tab import ExteriorTab
from archviz_app.ui.interior_tab import InteriorTab
from archviz_app.ui.widgets import LabeledLineEdit, LabeledTextArea
from archviz_app.utils.qt_async import Worker


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ArchViz Desktop Tool")
        self.resize(1100, 800)

        self.project_name = LabeledLineEdit("Project name", placeholder="e.g., Lakeview Villa")
        self.model_name = LabeledLineEdit(
            "Gemini model name",
            placeholder="gemini-2.5-flash-image-preview",
        )
        self.model_name.set_value("gemini-1.5-flash")

        self.api_key = LabeledLineEdit("Gemini API key", placeholder="Paste API key…", echo_password=True)
        self.endpoint = LabeledLineEdit(
            "Gemini REST endpoint (advanced)",
            placeholder="Leave blank for default",
        )

        self.style_notes = LabeledTextArea(
            "Global consistency notes (style bible)",
            placeholder="Example: Modern minimalist, warm lighting, consistent walnut + black accents…",
        )

        self.tabs = QTabWidget()
        self.exterior_tab = ExteriorTab()
        self.interior_tab = InteriorTab()
        self.tabs.addTab(self.exterior_tab, "Exterior")
        self.tabs.addTab(self.interior_tab, "Interior")

        self.generate_btn = QPushButton("Generate renders")
        self.generate_btn.clicked.connect(self.on_generate)

        self.list_models_btn = QPushButton("List available models")
        self.list_models_btn.clicked.connect(self.on_list_models)

        self.log = QTextEdit()
        self.log.setReadOnly(True)

        top = QHBoxLayout()
        top.addWidget(self.project_name)
        top.addWidget(self.model_name)

        keys = QHBoxLayout()
        keys.addWidget(self.api_key)
        keys.addWidget(self.endpoint)

        layout = QVBoxLayout()
        layout.addLayout(top)
        layout.addLayout(keys)
        layout.addWidget(self.style_notes)
        layout.addWidget(self.tabs)
        btn_row = QHBoxLayout()
        btn_row.addWidget(self.generate_btn)
        btn_row.addWidget(self.list_models_btn)
        btn_row.addStretch(1)

        layout.addLayout(btn_row)
        layout.addWidget(self.log)
        self.setLayout(layout)

        self._worker: Worker | None = None

    def _append_log(self, msg: str) -> None:
        self.log.append(msg)

    def on_generate(self) -> None:
        api_key = self.api_key.value()
        if not api_key:
            QMessageBox.warning(self, "Missing API key", "Please paste your Gemini API key.")
            return

        ext = self.exterior_tab.data()
        rooms = self.interior_tab.data()

        job = build_render_job(
            project_name=self.project_name.value(),
            style_notes=self.style_notes.value(),
            model_name=self.model_name.value(),
            exterior_plan_files=ext["plan_files"],
            exterior_finishes=ext["finishes"],
            exterior_angles=ext["angles"],
            rooms=rooms,
        )

        ts = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_dir = Path(__file__).resolve().parents[2] / "output" / ts

        client = GeminiClient(api_key=api_key, endpoint=self.endpoint.value() or None)
        service = RenderService(gemini=client, output_dir=out_dir)

        self.generate_btn.setEnabled(False)
        self._append_log(f"Starting render job… output -> {out_dir}")

        def run():
            return service.render_all(job)

        self._worker = Worker(run)
        self._worker.signals.finished.connect(self._on_done)
        self._worker.signals.error.connect(self._on_error)
        self._worker.start()

    def on_list_models(self) -> None:
        api_key = self.api_key.value()
        if not api_key:
            QMessageBox.warning(self, "Missing API key", "Please paste your Gemini API key first.")
            return

        client = GeminiClient(api_key=api_key, endpoint=self.endpoint.value() or None)
        self._append_log("Fetching available models…")

        def run():
            return client.list_models_rest()

        self.list_models_btn.setEnabled(False)
        self._worker = Worker(run)
        self._worker.signals.finished.connect(self._on_models)
        self._worker.signals.error.connect(self._on_error)
        self._worker.start()

    def _on_models(self, data) -> None:
        self.list_models_btn.setEnabled(True)
        models = data.get("models") or []
        self._append_log(f"Found {len(models)} model(s). Showing up to 25:")
        for m in models[:25]:
            name = m.get("name", "")
            display = m.get("displayName", "")
            self._append_log(f"- {name} ({display})")
        QMessageBox.information(self, "Models", f"Found {len(models)} model(s). See log for list.")

    def _on_done(self, result) -> None:
        self.generate_btn.setEnabled(True)
        files = getattr(result, "written_files", [])
        self._append_log(f"Done. Wrote {len(files)} file(s).")
        if len(files) == 0:
            self._append_log(
                "No images were returned by the model. "
                "This usually means the selected Gemini model does not support image output for this endpoint/key. "
                "Click 'List available models' and choose a different model. "
                "Also check the *_debug.json files in the output folder for the raw API response."
            )
        if files:
            self._append_log("Sample outputs:")
            for p in files[:5]:
                self._append_log(f"- {p}")
        QMessageBox.information(self, "Done", f"Render complete. Wrote {len(files)} image(s).")

    def _on_error(self, msg: str) -> None:
        self.generate_btn.setEnabled(True)
        self._append_log(f"ERROR: {msg}")
        QMessageBox.critical(self, "Error", msg)
