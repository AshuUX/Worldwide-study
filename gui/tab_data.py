from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QProgressBar, QLabel, QTextEdit)
from PyQt6.QtCore import QThread, pyqtSignal
import os
import sys
import io
import contextlib

# Import pipeline modules
from data_pipeline import fetch_noaa, fetch_era5, fetch_dga, fetch_cne, fetch_ceaza, clean, validate

class Worker(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, func, name):
        super().__init__()
        self.func = func
        self.name = name

    def run(self):
        # Redirect stdout to capture logs from the functions
        f = io.StringIO()
        try:
            with contextlib.redirect_stdout(f):
                self.func()
            self.log.emit(f.getvalue())
            self.finished.emit(True, self.name)
        except Exception as e:
            self.log.emit(f.getvalue())
            self.log.emit(f"Error in {self.name}: {str(e)}")
            self.finished.emit(False, self.name)

class DataSetupTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Data Acquisition", objectName="header"))

        self.sources = [
            ("NOAA Indices", fetch_noaa.main),
            ("ERA5 Data", fetch_era5.main),
            ("DGA Discharge", fetch_dga.main),
            ("CNE Generation", fetch_cne.main),
            ("Snowpack Data", fetch_ceaza.main)
        ]

        self.status_labels = {}
        self.progress_bars = {}
        self.buttons = {}

        for name, func in self.sources:
            h_layout = QHBoxLayout()
            btn = QPushButton(f"Fetch {name}")
            btn.clicked.connect(lambda checked, f=func, n=name: self.run_fetch(f, n))
            self.buttons[name] = btn
            h_layout.addWidget(btn)

            pbar = QProgressBar()
            self.progress_bars[name] = pbar
            h_layout.addWidget(pbar)

            status = QLabel("⚪")
            self.status_labels[name] = status
            h_layout.addWidget(status)

            self.layout.addLayout(h_layout)

        self.master_btn = QPushButton("Run Full Data Pipeline")
        self.master_btn.clicked.connect(self.run_full_pipeline)
        self.layout.addWidget(self.master_btn)

        self.report_box = QTextEdit()
        self.report_box.setReadOnly(True)
        self.layout.addWidget(self.report_box)

        self.status_footer = QLabel("Ready")
        self.layout.addWidget(self.status_footer)

    def run_fetch(self, func, name):
        if name in self.status_labels:
            self.status_labels[name].setText("⏳")
            self.progress_bars[name].setRange(0, 0)

        worker = Worker(func, name)
        worker.log.connect(self.append_log)
        worker.finished.connect(self.on_fetch_finished)
        worker.start()
        if not hasattr(self, 'workers'): self.workers = []
        self.workers.append(worker)

    def on_fetch_finished(self, success, name):
        if name in self.progress_bars:
            self.progress_bars[name].setRange(0, 100)
            self.progress_bars[name].setValue(100 if success else 0)
            self.status_labels[name].setText("✅" if success else "❌")

        if name == "Pipeline":
            self.status_footer.setText("Pipeline Complete" if success else "Pipeline Failed")

    def append_log(self, text):
        self.report_box.append(text.strip())

    def run_full_pipeline(self):
        def pipeline():
            clean.main()
            validate.main()
        self.run_fetch(pipeline, "Pipeline")
