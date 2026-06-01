import sys
from PyQt6.QtWidgets import QApplication, QDialog
from gui.main_window import MainWindow
from gui.login_window import LoginWindow
from database.crud import create_user, get_engine
from sqlalchemy import text


def setup_admin_if_needed():
    engine = get_engine()
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM Dim_Users")).scalar()
        if count == 0:
            create_user("admin", "1234", "Адміністратор")
            print("Створено базового користувача: Логін - admin, Пароль - 1234")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    setup_admin_if_needed()
    login_dialog = LoginWindow()

    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)