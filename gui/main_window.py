from PyQt6.QtWidgets import QMainWindow, QTabWidget
from gui.tabs.tab_analytics import AnalyticsTab
from gui.tabs.tab_products import ProductsTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Система оптимізації фармацевтичних запасів (ABC/XYZ)")
        self.resize(1100, 700)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_analytics = AnalyticsTab()
        self.tab_crud = ProductsTab()

        self.tabs.addTab(self.tab_analytics, "ABC/XYZ аналіз")
        self.tabs.addTab(self.tab_crud, "Управління товарами (CRUD)")

        self.setStyleSheet("""
            QMainWindow { background-color: #f5f6fa; }
            QTabWidget::pane { border: 1px solid #dcdde1; border-radius: 4px; }
            QTabBar::tab { background: #e1e2e6; padding: 10px 20px; margin-right: 2px; }
            QTabBar::tab:selected { background: #ffffff; border-bottom-color: #ffffff; }
        """)