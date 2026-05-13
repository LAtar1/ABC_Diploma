from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from core.abc_xyz_engine import InventoryAnalyzer


class AnalyticsTab(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 1. Создаем кнопку запуска
        self.btn_run_analysis = QPushButton("Запустити ABC/XYZ аналіз")
        self.btn_run_analysis.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; 
                color: white; 
                font-size: 14px; 
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        self.btn_run_analysis.clicked.connect(self.run_analysis)  # Привязываем клик к функции
        self.layout.addWidget(self.btn_run_analysis)

        # 2. Создаем таблицу для результатов
        self.table = QTableWidget()
        # Названия колонок (как они будут в интерфейсе)
        self.headers = ["ID", "Назва препарату", "Виручка", "Клас ABC", "CV (%)", "Клас XYZ", "Матриця", "Рекомендація"]
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)

        # Делаем так, чтобы таблица растягивалась на всю ширину окна
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(self.table)

    def run_analysis(self):
        """Функция, которая срабатывает при нажатии на кнопку"""
        try:

            analyzer = InventoryAnalyzer(server='localhost', database='diploma')

            # Запускаем расчет матрицы
            matrix_df = analyzer.run_matrix_analysis()

            if matrix_df is None or matrix_df.empty:
                QMessageBox.warning(self, "Помилка", "Немає даних для аналізу!")
                return

            self.table.setRowCount(0)

            for index, row in matrix_df.iterrows():
                row_position = self.table.rowCount()
                self.table.insertRow(row_position)

                self.table.setItem(row_position, 0, QTableWidgetItem(str(row['ProductID'])))
                self.table.setItem(row_position, 1, QTableWidgetItem(str(row['ProductName'])))
                self.table.setItem(row_position, 2, QTableWidgetItem(f"{row['TotalAmount']:.2f} грн"))
                self.table.setItem(row_position, 3, QTableWidgetItem(str(row['ABC_Class'])))
                self.table.setItem(row_position, 4, QTableWidgetItem(f"{row['CV']:.2f}"))
                self.table.setItem(row_position, 5, QTableWidgetItem(str(row['XYZ_Class'])))
                self.table.setItem(row_position, 6, QTableWidgetItem(str(row['Category_Matrix'])))
                self.table.setItem(row_position, 7, QTableWidgetItem(str(row['Recommendation'])))

            QMessageBox.information(self, "Успіх", "Матричний аналіз успішно завершено!")

        except Exception as e:
            QMessageBox.critical(self, "Помилка бази даних", f"Сталася помилка при розрахунку:\n{str(e)}")