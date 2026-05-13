from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система оптимізації фармацевтичних запасів (ABC/XYZ)")
        self.resize(1000, 700)  # Розмір вікна

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab1 = QWidget()
        self.tab2 = QWidget()

        self.tabs.addTab(self.tab1, "ABC/XYZ Аналіз")
        self.tabs.addTab(self.tab2, "Управління товарами (CRUD)")

        self.setStyleSheet("""
            QMainWindow { background-color: #f5f6fa; }
            QTabWidget::pane { border: 1px solid #dcdde1; border-radius: 4px; }
            QTabBar::tab { background: #e1e2e6; padding: 10px 20px; margin-right: 2px; }
            QTabBar::tab:selected { background: #ffffff; border-bottom-color: #ffffff; }
        """)