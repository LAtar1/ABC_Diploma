import random
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QLineEdit, QMessageBox, QGroupBox, QFormLayout)
from PyQt6.QtCore import Qt
from database.crud import get_all_products, add_product, process_sale, restock_product


class ProductsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.top_forms_layout = QHBoxLayout()

        add_group = QGroupBox("1. Новий препарат")
        add_layout = QFormLayout()
        add_group.setLayout(add_layout)
        add_group.setMaximumWidth(320)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Назва...")
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Ціна...")
        self.btn_add = QPushButton("Створити картку")
        self.btn_add.setStyleSheet(
            "background-color: #3498db; color: white; padding: 6px; font-weight: bold; border-radius: 3px;")
        self.btn_add.clicked.connect(self.add_new_product)

        add_layout.addRow("Назва:", self.name_input)
        add_layout.addRow("Ціна:", self.price_input)
        add_layout.addRow("", self.btn_add)
        self.top_forms_layout.addWidget(add_group)

        restock_group = QGroupBox("2. Надходження на склад")
        restock_layout = QFormLayout()
        restock_group.setLayout(restock_layout)
        restock_group.setMaximumWidth(300)

        self.restock_id_input = QLineEdit()
        self.restock_id_input.setPlaceholderText("ID товару")
        self.restock_qty_input = QLineEdit()
        self.restock_qty_input.setPlaceholderText("Кількість шт.")
        self.btn_restock = QPushButton("Додати на склад")
        self.btn_restock.setStyleSheet(
            "background-color: #27ae60; color: white; padding: 6px; font-weight: bold; border-radius: 3px;")
        self.btn_restock.clicked.connect(self.handle_restock)

        restock_layout.addRow("ID:", self.restock_id_input)
        restock_layout.addRow("К-ть:", self.restock_qty_input)
        restock_layout.addRow("", self.btn_restock)
        self.top_forms_layout.addWidget(restock_group)

        sale_group = QGroupBox("3. Оформлення продажу")
        sale_layout = QFormLayout()
        sale_group.setLayout(sale_layout)
        sale_group.setMaximumWidth(300)

        self.sale_id_input = QLineEdit()
        self.sale_id_input.setPlaceholderText("ID товару")
        self.sale_qty_input = QLineEdit()
        self.sale_qty_input.setPlaceholderText("Кількість шт.")
        self.btn_sell = QPushButton("Продати зі складу")
        self.btn_sell.setStyleSheet(
            "background-color: #e67e22; color: white; padding: 6px; font-weight: bold; border-radius: 3px;")
        self.btn_sell.clicked.connect(self.handle_sale)

        sale_layout.addRow("ID:", self.sale_id_input)
        sale_layout.addRow("К-ть:", self.sale_qty_input)
        sale_layout.addRow("", self.btn_sell)
        self.top_forms_layout.addWidget(sale_group)

        self.top_forms_layout.addStretch()
        self.layout.addLayout(self.top_forms_layout)

        self.table = QTableWidget()
        self.headers = ["ID", "SKU", "Назва препарату", "Категорія", "Базова ціна", "Залишок (шт)"]
        self.table.setColumnCount(len(self.headers))
        self.table.setHorizontalHeaderLabels(self.headers)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("alternate-background-color: #f4f6f7; background-color: #ffffff;")

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.layout.addWidget(self.table)
        self.load_data()

    def load_data(self):
        df = get_all_products()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)

            stock = int(row['TotalStock'])
            stock_item = QTableWidgetItem(str(stock))
            if stock <= 0:
                stock_item.setForeground(Qt.GlobalColor.red)
            else:
                stock_item.setForeground(Qt.GlobalColor.darkGreen)

            self.table.setItem(row_pos, 0, QTableWidgetItem(str(row['ProductID'])))
            self.table.setItem(row_pos, 1, QTableWidgetItem(str(row['SKU'])))
            self.table.setItem(row_pos, 2, QTableWidgetItem(str(row['ProductName'])))
            self.table.setItem(row_pos, 3, QTableWidgetItem(str(row['CategoryName'])))
            self.table.setItem(row_pos, 4, QTableWidgetItem(f"{row['BasePrice']:.2f}"))
            self.table.setItem(row_pos, 5, stock_item)

    def add_new_product(self):
        name = self.name_input.text().strip()
        price_str = self.price_input.text().strip()

        if not name or not price_str:
            QMessageBox.warning(self, "Помилка", "Заповніть назву та ціну!")
            return
        try:
            price = float(price_str.replace(',', '.'))
            add_product(f"SKU-{random.randint(1000, 9999)}", name, 1, 1, price)
            self.load_data()
            self.name_input.clear()
            self.price_input.clear()
            QMessageBox.information(self, "Успіх", f"Товар '{name}' створено!")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))

    def handle_restock(self):
        p_id_str = self.restock_id_input.text().strip()
        qty_str = self.restock_qty_input.text().strip()

        if not p_id_str.isdigit() or not qty_str.isdigit():
            QMessageBox.warning(self, "Помилка введення", "ID та кількість повинні бути цілими додатними числами!")
            return

        p_id, qty = int(p_id_str), int(qty_str)

        if qty <= 0:
            QMessageBox.warning(self, "Помилка введення", "Кількість має бути більшою за нуль!")
            return

        valid_ids = [int(self.table.item(i, 0).text()) for i in range(self.table.rowCount())]
        if p_id not in valid_ids:
            QMessageBox.warning(self, "Помилка", f"Товар з ID {p_id} не знайдено у довіднику!")
            return

        try:
            restock_product(p_id, 1, qty)
            self.load_data()
            self.restock_id_input.clear()
            self.restock_qty_input.clear()
            QMessageBox.information(self, "Успіх", f"На склад додано {qty} шт. товару ID {p_id}")
        except Exception as e:
            QMessageBox.critical(self, "Помилка БД", f"Не вдалося оновити базу:\n{str(e)}")

    def handle_sale(self):
        p_id_str = self.sale_id_input.text().strip()
        qty_str = self.sale_qty_input.text().strip()

        if not p_id_str.isdigit() or not qty_str.isdigit():
            QMessageBox.warning(self, "Помилка введення", "ID та кількість повинні бути цілими додатними числами!")
            return

        p_id, qty = int(p_id_str), int(qty_str)

        if qty <= 0:
            QMessageBox.warning(self, "Помилка введення", "Кількість продажу має бути більшою за нуль!")
            return

        valid_ids = [int(self.table.item(i, 0).text()) for i in range(self.table.rowCount())]
        if p_id not in valid_ids:
            QMessageBox.warning(self, "Помилка", f"Товар з ID {p_id} не знайдено у довіднику!")
            return

        try:
            process_sale(product_id=p_id, pharmacy_id=1, quantity=qty, price=150.0)
            self.load_data()
            self.sale_id_input.clear()
            self.sale_qty_input.clear()
            QMessageBox.information(self, "Успіх", f"Продано {qty} шт. товару ID {p_id}")
        except Exception as e:
            error_msg = str(e)
            if "Недостатньо товару" in error_msg:
                QMessageBox.warning(self, "Відмова операції",
                                    f"На складі недостатньо товару для продажу {qty} одиниць!")
            else:
                QMessageBox.critical(self, "Помилка транзакції", "Сталася невідома системна помилка.")