import sys
from PyQt6.QtWidgets import QApplication
from auth_window import AuthWindow
from ui_main import MainWindow
from DeactivationWindow import DeactivationWindow
from database import Database

main_window = None  # 🔥 Глобальне посилання — щоб Qt не знищив вікно

def start_main_app(user):
    """Запускає відповідне вікно в залежності від ролі"""
    global main_window  # використовуємо глобальну змінну

    print(f"[DEBUG] Отримано користувача: {dict(user)}")

    db = Database()  # Ініціалізуємо БД

    if user["role"] == "admin":
        print("[DEBUG] Відкриваємо головне вікно для адміністратора")
        main_window = MainWindow(user)
    else:
        print("[DEBUG] Відкриваємо вікно деактивації для АЗС")
        main_window = DeactivationWindow(db, user, lambda: None)  # Передаємо пусту функцію

    main_window.show()


if __name__ == "__main__":
    print("[DEBUG] Запуск програми. Відкриття вікна авторизації...")

    app = QApplication(sys.argv)
    auth_window = AuthWindow(start_main_app)
    auth_window.show()

    sys.exit(app.exec())
