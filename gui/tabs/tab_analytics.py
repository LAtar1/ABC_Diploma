from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox,
                             QHBoxLayout, QFileDialog)
from core.abc_xyz_engine import InventoryAnalyzer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas


class AnalyticsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.current_matrix_df = None

        self.top_layout = QHBoxLayout()

        self.btn_run = QPushButton("Запустити ABC/XYZ аналіз")
        self.btn_run.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; color: white; padding: 12px; 
                font-size: 14px; font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        self.btn_run.clicked.connect(self.run_analysis)
        self.top_layout.addWidget(self.btn_run)

        self.btn_export = QPushButton("Експорт в Excel")
        self.btn_export.setEnabled(False)
        self.btn_export.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d; color: white; padding: 12px; 
                font-size: 14px; font-weight: bold; border-radius: 4px;
            }
            QPushButton:hover { background-color: #95a5a6; }
        """)
        self.btn_export.clicked.connect(self.export_to_excel)
        self.top_layout.addWidget(self.btn_export)

        self.main_layout.addLayout(self.top_layout)

        self.content_layout = QHBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Назва", "Дохід", "ABC", "CV (%)", "XYZ", "Матриця", "Порада"])
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            "alternate-background-color: #f4f6f7; background-color: #ffffff; border: 1px solid #dcdde1;")

        # ДОДАЄМО ПІДКАЗКИ ДЛЯ ШАПКИ ТАБЛИЦІ
        self.table.horizontalHeaderItem(2).setToolTip("Загальна виручка, яку приніс препарат")
        self.table.horizontalHeaderItem(3).setToolTip(
            "Клас ABC:\nA - дає 80% доходу\nB - дає 15% доходу\nC - дає 5% доходу")
        self.table.horizontalHeaderItem(4).setToolTip(
            "Коефіцієнт варіації (CV):\nПоказує наскільки нестабільним є попит.\nЧим менший відсоток, тим стабільніші продажі.")
        self.table.horizontalHeaderItem(5).setToolTip(
            "Клас XYZ:\nX - стабільний попит\nY - попит коливається\nZ - непередбачуваний попит")
        self.table.horizontalHeaderItem(6).setToolTip(
            "Перетин класів ABC та XYZ.\nНаведіть курсор на комірку нижче для детальної розшифровки.")

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)

        self.content_layout.addWidget(self.table, 5)

        self.figure, self.ax = plt.subplots(figsize=(4, 4))
        self.figure.patch.set_facecolor('#f5f6fa')
        self.canvas = FigureCanvas(self.figure)
        self.content_layout.addWidget(self.canvas, 3)

        self.main_layout.addLayout(self.content_layout)

    def draw_pareto(self, df):
        self.ax.clear()
        y = df['CumPerc'].values
        x = range(len(y))

        self.ax.plot(x, y, color="#2980b9", marker="o", linestyle="-", linewidth=2)
        self.ax.fill_between(x, y, color="#3498db", alpha=0.3)
        self.ax.axhline(y=80, color='#e74c3c', linestyle='--', label='Зона А (80%)')
        self.ax.axhline(y=95, color='#27ae60', linestyle='--', label='Зона В (95%)')
        self.ax.set_title("Крива Парето", fontsize=12, fontweight='bold')
        self.ax.set_ylabel("% Доходу")
        self.ax.set_xlabel("SKU")
        self.ax.grid(True, linestyle=':', alpha=0.7)
        self.figure.tight_layout()
        self.canvas.draw()

    def run_analysis(self):
        try:
            # Заміни 'PharmacyDB' на реальне ім'я своєї бази, якщо воно інше
            analyzer = InventoryAnalyzer(server='localhost', database='diploma')
            matrix_df = analyzer.run_matrix_analysis()

            # СЛОВНИК З ДЕТАЛЬНИМИ ПІДКАЗКАМИ ДЛЯ КОЖНОЇ ГРУПИ
            tooltips_dict = {
                "AX": "Група AX: Найвища цінність і стабільний попит.\nДія: Забезпечити постійну наявність, можна автоматизувати закупівлі.",
                "AY": "Група AY: Висока цінність, але попит коливається.\nДія: Створити страховий запас, уважно слідкувати за трендами та сезонами.",
                "AZ": "Група AZ: Висока цінність, непередбачуваний попит.\nДія: Суворий ручний контроль! Замовляти обережно, щоб не заморозити багато коштів.",
                "BX": "Група BX: Середня цінність, стабільний попит.\nДія: Регулярні закупівлі за графіком.",
                "BY": "Група BY: Середня цінність, змінний попит.\nДія: Тримати помірний страховий запас.",
                "BZ": "Група BZ: Середня цінність, хаотичний попит.\nДія: Закуповувати невеликими партіями або під замовлення.",
                "CX": "Група CX: Низька цінність, стабільний попит.\nДія: Закуповувати рідко, але великими партіями (для економії на доставці).",
                "CY": "Група CY: Низька цінність, змінний попит.\nДія: Мінімальний запас на складі, уникати затоварення.",
                "CZ": "Група CZ: Низька цінність, непередбачуваний попит (Неліквід).\nДія: Кандидати на виведення з асортименту, купувати тільки під замовлення."
            }

            if matrix_df is not None:
                self.current_matrix_df = matrix_df
                self.table.setRowCount(0)

                for _, row in matrix_df.iterrows():
                    pos = self.table.rowCount()
                    self.table.insertRow(pos)

                    self.table.setItem(pos, 0, QTableWidgetItem(str(row['ProductID'])))
                    self.table.setItem(pos, 1, QTableWidgetItem(str(row['ProductName'])))
                    self.table.setItem(pos, 2, QTableWidgetItem(f"{row['TotalAmount']:.0f}"))
                    self.table.setItem(pos, 3, QTableWidgetItem(row['ABC_Class']))
                    self.table.setItem(pos, 4, QTableWidgetItem(f"{row['CV']:.1f}"))
                    self.table.setItem(pos, 5, QTableWidgetItem(row['XYZ_Class']))

                    # Отримуємо текст підказки зі словника (якщо немає - беремо пусту строку)
                    matrix_val = row['Category_Matrix']
                    hint_text = tooltips_dict.get(matrix_val, "Рекомендація відсутня")

                    # Створюємо комірки для Матриці та Поради і вішаємо на них підказку
                    item_matrix = QTableWidgetItem(matrix_val)
                    item_matrix.setToolTip(hint_text)

                    item_rec = QTableWidgetItem(row['Recommendation'])
                    item_rec.setToolTip(hint_text)

                    self.table.setItem(pos, 6, item_matrix)
                    self.table.setItem(pos, 7, item_rec)

                self.draw_pareto(matrix_df)

                self.btn_export.setEnabled(True)
                self.btn_export.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db; color: white; padding: 12px; 
                        font-size: 14px; font-weight: bold; border-radius: 4px;
                    }
                    QPushButton:hover { background-color: #2980b9; }
                """)

                QMessageBox.information(self, "Успіх",
                                        "Аналіз виконано! Наведіть курсор на таблицю, щоб побачити підказки.")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def export_to_excel(self):
        """Логіка збереження результатів та побудови графіка у файлі Excel"""
        if self.current_matrix_df is None: return

        file_path, _ = QFileDialog.getSaveFileName(self, "Зберегти звіт", "ABC_XYZ_Report.xlsx", "Excel Files (*.xlsx)")
        if file_path:
            try:
                export_df = self.current_matrix_df.copy()
                export_df.columns = ["ID", "Назва", "Дохід (грн)", "Кумулятивний %", "ABC", "CV", "XYZ", "Матриця",
                                     "Рекомендація"]

                import pandas as pd
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    export_df.to_excel(writer, index=False, sheet_name="Аналіз")
                    workbook = writer.book
                    worksheet = writer.sheets["Аналіз"]
                    worksheet.set_column('B:B', 25)
                    worksheet.set_column('I:I', 35)

                    chart = workbook.add_chart({'type': 'line'})
                    max_row = len(export_df)
                    chart.add_series({
                        'name': 'Кумулятивний % доходу',
                        'categories': ['Аналіз', 1, 1, max_row, 1],
                        'values': ['Аналіз', 1, 3, max_row, 3],
                        'line': {'color': '#2980b9', 'width': 2.25},
                        'marker': {'type': 'circle', 'size': 5, 'fill': {'color': '#e74c3c'}}
                    })
                    chart.set_title({'name': 'Крива Парето'})
                    chart.set_x_axis({'name': 'Препарати'})
                    chart.set_y_axis({'name': '% Доходу', 'max': 100})
                    chart.set_legend({'position': 'none'})
                    worksheet.insert_chart('K2', chart, {'x_scale': 1.5, 'y_scale': 1.5})

                QMessageBox.information(self, "Успіх", "Звіт з графіком успішно збережено!")
            except Exception as e:
                QMessageBox.critical(self, "Помилка експорту", str(e))