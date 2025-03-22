from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from database import Database


class LoginWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        print("[DEBUG] Відкрито вікно входу в систему")
        self.main_window = main_window  # Зберігаємо посилання на головне вікно
        self.db = Database()  # Підключення до бази
        self.setWindowTitle("Вхід у систему")
        self.setGeometry(600, 300, 300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label_username = QLabel("Логін:")
        layout.addWidget(self.label_username)

        self.input_username = QLineEdit()
        layout.addWidget(self.input_username)

        self.label_password = QLabel("Пароль:")
        layout.addWidget(self.label_password)

        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)  # Приховуємо введений пароль
        layout.addWidget(self.input_password)

        self.button_login = QPushButton("Увійти")
        self.button_login.clicked.connect(self.login)
        layout.addWidget(self.button_login)

        self.button_register = QPushButton("Зареєструвати нового користувача")
        self.button_register.clicked.connect(self.register_user)
        layout.addWidget(self.button_register)

        self.setLayout(layout)

    def login(self):
        """Перевірка введених даних та відкриття головного вікна"""
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()

        print(f"[DEBUG] Спроба входу: {username}")

        if not username or not password:
            print("[DEBUG] Помилка: Порожній логін або пароль")
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть логін і пароль!")
            return

        if self.db.validate_user(username, password):
            print(f"[DEBUG] Вхід успішний: {username}")
            QMessageBox.information(self, "Успіх", f"Ласкаво просимо, {username}!")
            self.main_window.show()  # Відкриваємо головне вікно
            self.close()  # Закриваємо вікно логування
        else:
            print(f"[DEBUG] Помилка входу: {username} (невірні дані)")
            QMessageBox.critical(self, "Помилка", "Неправильний логін або пароль!")

    def register_user(self):
        """Реєстрація нового користувача"""
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()

        print(f"[DEBUG] Спроба реєстрації: {username}")

        if not username or not password:
            print("[DEBUG] Помилка: Порожній логін або пароль при реєстрації")
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть логін і пароль!")
            return

        if self.db.add_user(username, password):
            print(f"[DEBUG] Користувач {username} успішно зареєстрований")
            QMessageBox.information(self, "Успіх", "Користувач успішно зареєстрований!")
        else:
            print(f"[DEBUG] Помилка реєстрації: {username} (логін вже існує?)")
            QMessageBox.critical(self, "Помилка", "Користувач із таким логіном вже існує!")
