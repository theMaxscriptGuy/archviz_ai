from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Optional, TypeVar

from PyQt6.QtCore import QObject, QThread, pyqtSignal


T = TypeVar("T")


class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)


class Worker(QThread):
    def __init__(self, fn: Callable[[], object]):
        super().__init__()
        self.fn = fn
        self.signals = WorkerSignals()

    def run(self) -> None:
        try:
            result = self.fn()
            self.signals.finished.emit(result)
        except Exception as e:  # noqa: BLE001
            self.signals.error.emit(str(e))
