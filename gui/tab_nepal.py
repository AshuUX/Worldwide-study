from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QComboBox)
from .tab_hydrology import HydrologyTab

class NepalTab(HydrologyTab):
    def __init__(self):
        super().__init__()
        self.layout.itemAt(0).widget().setText("Nepal Basin Model")

        # Change basins
        self.basin_sel.clear()
        self.basin_sel.addItems(["Koshi", "Gandaki", "Karnali"])

        # Add compare button
        self.compare_btn = QPushButton("Compare Chile vs Nepal")
        self.layout.addWidget(self.compare_btn)
