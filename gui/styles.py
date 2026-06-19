DARK_STYLESHEET = """
QMainWindow {
    background-color: #121212;
}
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 10pt;
}
QTabWidget::pane {
    border: 1px solid #333;
    top: -1px;
}
QTabBar::tab {
    background: #252525;
    border: 1px solid #333;
    padding: 10px 20px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #333;
    border-bottom-color: #1e1e1e;
}
QPushButton {
    background-color: #333;
    border: 1px solid #555;
    padding: 8px 15px;
    border-radius: 4px;
}
QPushButton:hover {
    background-color: #444;
}
QPushButton:pressed {
    background-color: #555;
}
QLineEdit, QComboBox, QSpinBox {
    background-color: #252525;
    border: 1px solid #444;
    padding: 5px;
    border-radius: 3px;
}
QProgressBar {
    border: 1px solid #444;
    border-radius: 5px;
    text-align: center;
}
QProgressBar::chunk {
    background-color: #007acc;
    width: 20px;
}
QScrollArea {
    border: none;
}
QLabel#header {
    font-size: 18pt;
    font-weight: bold;
    color: #ffffff;
}
"""
