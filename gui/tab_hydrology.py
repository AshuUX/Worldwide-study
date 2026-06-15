from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QSlider, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from .charts import MplCanvas, create_bar_chart, create_fan_chart
from hydrology_engine.runner import HydrologyRunner
import pandas as pd
import numpy as np

class ModelWorker(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, year, month, basin):
        super().__init__()
        self.year = year
        self.month = month
        self.basin = basin

    def run(self):
        try:
            # We need to handle PYTHONPATH or relative imports correctly here
            runner = HydrologyRunner()
            result = runner.run(self.year, self.month)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class HydrologyTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Hydrology Swarm Model", objectName="header"))

        controls = QHBoxLayout()
        self.basin_sel = QComboBox()
        self.basin_sel.addItems(["Maule", "Biobío", "Aysén"])
        controls.addWidget(QLabel("Basin:"))
        controls.addWidget(self.basin_sel)

        self.year_slider = QSlider(Qt.Orientation.Horizontal)
        self.year_slider.setRange(1960, 2024)
        self.year_slider.setValue(2021)
        self.year_label = QLabel("2021")
        self.year_slider.valueChanged.connect(lambda v: self.year_label.setText(str(v)))
        controls.addWidget(QLabel("Year:"))
        controls.addWidget(self.year_slider)
        controls.addWidget(self.year_label)

        self.month_sel = QComboBox()
        self.month_sel.addItems(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])
        self.month_sel.setCurrentIndex(9) # Oct
        controls.addWidget(QLabel("Month:"))
        controls.addWidget(self.month_sel)

        self.run_btn = QPushButton("Run Swarm Model")
        self.run_btn.clicked.connect(self.run_model)
        controls.addWidget(self.run_btn)

        self.layout.addLayout(controls)

        # Charts
        chart_layout = QHBoxLayout()
        self.bar_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.fan_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        chart_layout.addWidget(self.bar_canvas)
        chart_layout.addWidget(self.fan_canvas)
        self.layout.addLayout(chart_layout)

        self.results_label = QLabel("Run model to see results")
        self.layout.addWidget(self.results_label)

    def run_model(self):
        year = self.year_slider.value()
        month = self.month_sel.currentIndex() + 1
        basin = self.basin_sel.currentText().lower()

        self.run_btn.setEnabled(False)
        self.results_label.setText("Running model...")

        self.worker = ModelWorker(year, month, basin)
        self.worker.finished.connect(self.on_model_finished)
        self.worker.error.connect(self.on_model_error)
        self.worker.start()

    def on_model_finished(self, result):
        self.run_btn.setEnabled(True)
        self.results_label.setText(f"P10: {result['p10']:.1f} | P50: {result['p50']:.1f} | P90: {result['p90']:.1f} m³/s")

        # In a real app, we'd extract agent contributions from result.
        # For now, let's mock the bar chart data.
        labels = ['Snowmelt', 'Glacier', 'Precip']
        values = [result['p50']*0.6, result['p50']*0.1, result['p50']*0.3]
        create_bar_chart(self.bar_canvas, labels, values, "Contribution Breakdown")

        # Fan chart for the year (simplified)
        months = list(range(1, 13))
        p50s = [result['p50'] * (1 + 0.2*np.sin(m)) for m in months] # Mock seasonal
        create_fan_chart(self.fan_canvas, months, [v*0.7 for v in p50s], p50s, [v*1.3 for v in p50s], f"Fan Chart {self.year_slider.value()}")

    def on_model_error(self, err_msg):
        self.run_btn.setEnabled(True)
        QMessageBox.critical(self, "Model Error", err_msg)
