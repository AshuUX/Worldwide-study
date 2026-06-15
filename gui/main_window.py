from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QToolButton, QDialog, QFormLayout, QLineEdit, QSpinBox, QPushButton)
from PyQt6.QtGui import QIcon
from .tab_data import DataSetupTab
from .tab_hydrology import HydrologyTab
from .tab_insurance import InsuranceTab
from .tab_nepal import NepalTab
from .styles import DARK_STYLESHEET
import os

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        layout = QFormLayout(self)

        self.cds_key = QLineEdit()
        layout.addRow("CDS API Key:", self.cds_key)

        self.data_dir = QLineEdit("data")
        layout.addRow("Data Directory:", self.data_dir)

        self.mc_samples = QSpinBox()
        self.mc_samples.setRange(500, 10000)
        self.mc_samples.setValue(2000)
        layout.addRow("MC Samples:", self.mc_samples)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HydroInsure — Chile Hydropower Parametric Insurance")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(DARK_STYLESHEET)
        self.setWindowIcon(QIcon("assets/icon.ico"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        # Header with Settings
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.settings_btn = QToolButton()
        self.settings_btn.setText("⚙")
        self.settings_btn.clicked.connect(self.open_settings)
        header_layout.addWidget(self.settings_btn)
        self.main_layout.addLayout(header_layout)

        self.tabs = QTabWidget()
        self.tab_data = DataSetupTab()
        self.tab_hydro = HydrologyTab()
        self.tab_insurance = InsuranceTab()
        self.tab_nepal = NepalTab()

        self.tabs.addTab(self.tab_data, "Data Setup")
        self.tabs.addTab(self.tab_hydro, "Hydrology")
        self.tabs.addTab(self.tab_insurance, "Insurance")
        self.tabs.addTab(self.tab_nepal, "Nepal")

        self.main_layout.addWidget(self.tabs)

        # First launch check
        if not os.path.exists("data/clean/maule_master.csv"):
            self.tabs.setCurrentIndex(0)
            self.tab_data.status_footer.setText("Setup required — please fetch data first")

    def open_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec():
            # In real app, save to config file
            pass
