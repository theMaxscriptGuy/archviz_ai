import sys

from PyQt6.QtWidgets import QApplication

from archviz_app.ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)

    # Light theme (explicit), for consistent appearance across OS defaults.
    app.setStyleSheet(
        """
        QWidget { background: #ffffff; color: #111827; font-size: 13px; }
        QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background: #ffffff;
            color: #111827;
            border: 1px solid #d1d5db;
            border-radius: 6px;
            padding: 6px;
            selection-background-color: #93c5fd;
        }
        QListWidget, QTableWidget {
            background: #ffffff;
            color: #111827;
            border: 1px solid #d1d5db;
            border-radius: 6px;
        }
        QHeaderView::section { background: #f3f4f6; color: #111827; padding: 6px; border: 0px; }
        QPushButton {
            background: #f3f4f6;
            color: #111827;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            padding: 8px 12px;
        }
        QPushButton:hover { background: #e5e7eb; }
        QPushButton:pressed { background: #d1d5db; }
        QPushButton:disabled { color: #6b7280; background: #f9fafb; }
        QTabBar::tab { background: #f3f4f6; color: #111827; padding: 8px 12px; border: 1px solid #d1d5db; border-bottom: none; border-top-left-radius: 8px; border-top-right-radius: 8px; }
        QTabBar::tab:selected { background: #ffffff; }
        QTabWidget::pane { border: 1px solid #d1d5db; border-radius: 8px; }
        """
    )

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
