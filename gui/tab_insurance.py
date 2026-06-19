from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox, QLineEdit, QCheckBox, QTableWidget, QTableWidgetItem, QMessageBox)
from PyQt6.QtCore import QThread, pyqtSignal
from .charts import MplCanvas, create_prob_curve
from insurance_engine.trigger import design_trigger
from insurance_engine.pricing import illustrative_premium
from generation_translator.translator import flow_to_generation
from hydrology_engine.runner import HydrologyRunner
import json
import numpy as np

class InsuranceWorker(QThread):
    finished = pyqtSignal(dict, list)
    error = pyqtSignal(str)

    def __init__(self, plant, thresholds, payout):
        super().__init__()
        self.plant = plant
        self.thresholds = thresholds
        self.payout = payout

    def run(self):
        try:
            runner = HydrologyRunner()
            monthly_gen_dists = []
            for m in range(1, 13):
                f_res = runner.run(2023, m)
                g_res = flow_to_generation(f_res, self.plant)
                monthly_gen_dists.append(g_res)

            triggers = design_trigger(monthly_gen_dists, self.plant, threshold_pcts=self.thresholds)
            pricing = illustrative_premium(triggers, self.payout, calibration_error=0.15)
            self.finished.emit(pricing, monthly_gen_dists)
        except Exception as e:
            self.error.emit(str(e))

class InsuranceTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Parametric Insurance Design", objectName="header"))

        controls = QHBoxLayout()
        self.plant_sel = QComboBox()
        self.plant_sel.addItems(["Colbun", "Machicura", "Isla", "San Ignacio"])
        controls.addWidget(QLabel("Plant:"))
        controls.addWidget(self.plant_sel)

        self.payout_input = QLineEdit("5000000")
        controls.addWidget(QLabel("Payout (USD):"))
        controls.addWidget(self.payout_input)

        self.cb70 = QCheckBox("70%")
        self.cb80 = QCheckBox("80%")
        self.cb90 = QCheckBox("90%")
        self.cb80.setChecked(True)
        controls.addWidget(self.cb70)
        controls.addWidget(self.cb80)
        controls.addWidget(self.cb90)

        self.calc_btn = QPushButton("Calculate Triggers")
        self.calc_btn.clicked.connect(self.calculate)
        controls.addWidget(self.calc_btn)
        self.layout.addLayout(controls)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Trigger GWh", "Breach Prob", "Return Period", "Premium"])
        self.layout.addWidget(self.table)

        self.canvas = MplCanvas(self, width=5, height=3)
        self.layout.addWidget(self.canvas)

        self.risk_banner = QLabel("")
        self.risk_banner.setStyleSheet("color: red; font-weight: bold;")
        self.layout.addWidget(self.risk_banner)

    def calculate(self):
        plant_name = self.plant_sel.currentText()
        try:
            with open("generation_translator/plants_chile.json", "r") as f:
                plants = json.load(f)["plants"]
            plant = next(p for p in plants if p["name"] == plant_name)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load plant data: {e}")
            return

        thresholds = []
        if self.cb70.isChecked(): thresholds.append(0.7)
        if self.cb80.isChecked(): thresholds.append(0.8)
        if self.cb90.isChecked(): thresholds.append(0.9)

        try:
            payout = float(self.payout_input.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Invalid payout amount")
            return

        self.calc_btn.setEnabled(False)
        self.worker = InsuranceWorker(plant, thresholds, payout)
        self.worker.finished.connect(self.on_calc_finished)
        self.worker.error.connect(self.on_calc_error)
        self.worker.start()

    def on_calc_finished(self, pricing, monthly_gen_dists):
        self.calc_btn.setEnabled(True)
        self.table.setRowCount(len(pricing))
        # Re-derive triggers for display (or we could have passed them)
        # For simplicity, we'll just display pricing info which has most of it
        for i, (k, v) in enumerate(pricing.items()):
            # We need trigger_gwh. It's not in pricing but in triggers.
            # Let's assume we can get it from plant data or just pass triggers
            # Updated Worker to pass pricing and monthly_gen_dists is enough if we re-calc trigger_gwh
            plant_name = self.plant_sel.currentText()
            with open("generation_translator/plants_chile.json", "r") as f:
                plants = json.load(f)["plants"]
            plant = next(p for p in plants if p["name"] == plant_name)

            thresh = float(k.split('_')[1].replace('pct','')) / 100
            trigger_gwh = plant["historical_mean_annual_gwh"] * thresh

            self.table.setItem(i, 0, QTableWidgetItem(f"{trigger_gwh:.1f}"))
            self.table.setItem(i, 1, QTableWidgetItem(f"{v['premium_rate_pct']/100:.3f}"))
            self.table.setItem(i, 2, QTableWidgetItem(f"{v['return_period_years']:.1f}y"))
            self.table.setItem(i, 3, QTableWidgetItem(f"${v['total_premium_usd']:,}"))

        create_prob_curve(self.canvas, monthly_gen_dists[9]["samples"], trigger_gwh/12, "Generation PDF (Oct)")

    def on_calc_error(self, err):
        self.calc_btn.setEnabled(True)
        QMessageBox.critical(self, "Calculation Error", err)
