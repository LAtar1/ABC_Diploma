import sys
from PyQt6.QtWidgets import QApplication, QDialog
from gui.main_window import MainWindow
from gui.login_window import LoginWindow
from database.crud import create_user, get_engine
from sqlalchemy import text


def setup_admin_if_needed():
    """Створює першого адміністратора, якщо база користувачів порожня"""
    engine = get_engine()
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM Dim_Users")).scalar()
        if count == 0:
            # Якщо немає користувачів, створюємо логін: admin, пароль: 1234
            create_user("admin", "1234", "Адміністратор")
            print("Створено базового користувача: Логін - admin, Пароль - 1234")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. Перевіряємо, чи є хоча б один юзер (якщо ні - створюємо)
    setup_admin_if_needed()

    # 2. Запускаємо вікно авторизації
    login_dialog = LoginWindow()

    # 3. Якщо авторизація пройшла успішно (dialog.accept())
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        # Якщо натиснули "Хрестик" на вікні логіну
        sys.exit(0)