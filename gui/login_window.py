from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt
from database.crud import verify_login


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизація")
        self.setFixedSize(300, 180)  # Фіксований розмір вікна

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QLabel("Введіть логін:"))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логін...")
        self.layout.addWidget(self.username_input)

        self.layout.addWidget(QLabel("Введіть пароль:"))
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль...")
        # РОБИМО ПАРОЛЬ ПРИХОВАНИМ (ЗІРОЧКАМИ)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        self.btn_login = QPushButton("Увійти в систему")
        self.btn_login.setStyleSheet("background-color: #3498db; color: white; padding: 8px; font-weight: bold;")
        self.btn_login.clicked.connect(self.check_credentials)
        self.layout.addWidget(self.btn_login)

    def check_credentials(self):
        user = self.username_input.text().strip()
        pwd = self.password_input.text().strip()

        if not user or not pwd:
            QMessageBox.warning(self, "Помилка", "Введіть логін та пароль!")
            return

        # Звертаємось до бази даних через нашу функцію
        if verify_login(user, pwd):
            self.accept()  # Закриваємо вікно авторизації з успіхом
        else:
            QMessageBox.critical(self, "Відмова", "Неправильний логін або пароль!")