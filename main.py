import sys
from PyQt6.QtWidgets import QApplication
from ui_main import MainWindow  # Імпортуємо головне вікно

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()  # Створюємо екземпляр вікна
    window.show()  # Показуємо вікно
    sys.exit(app.exec())  # Запускаємо додаток











