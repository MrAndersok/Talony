from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFormLayout, QDialog, QComboBox
)
from database import Database


class AuthWindow(QWidget):
    def __init__(self, main_app_callback):
        super().__init__()
        print("[DEBUG] Відкрито вікно авторизації")
        self.setWindowTitle("Авторизація")
        self.setGeometry(500, 300, 400, 200)
        self.db = Database()
        self.main_app_callback = main_app_callback  # Викликається після успішного логіну
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логін")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.login_button = QPushButton("Увійти")
        self.register_button = QPushButton("Зареєструватися")

        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.open_registration_window)

        layout.addWidget(QLabel("Логін:"))
        layout.addWidget(self.username_input)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.register_button)

        self.setLayout(layout)

    def login(self):
        """Перевіряє логін і відкриває головне вікно"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        print(f"[DEBUG] Спроба входу: {username}")

        user = self.db.get_user(username, password)
        if user:
            print(f"[DEBUG] Вхід успішний: {username}, роль: {user['role']}")
            QMessageBox.information(self, "Успіх", f"Вхід виконано! Роль: {user['role']}")
            self.close()
            self.main_app_callback(user)
        else:
            print(f"[DEBUG] Невдалий вхід: {username}")
            QMessageBox.warning(self, "Помилка", "Неправильний логін або пароль!")

    def open_registration_window(self):
        """Відкриває вікно реєстрації"""
        print("[DEBUG] Відкриття вікна реєстрації")
        self.registration_window = RegistrationWindow(self)
        self.registration_window.show()


class RegistrationWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        print("[DEBUG] Відкрито вікно реєстрації")
        self.setWindowTitle("Реєстрація користувача")
        self.setGeometry(550, 350, 400, 250)
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.fullname_input = QLineEdit()
        self.fullname_input.setPlaceholderText("Повне ім'я")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Логін")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.role_combo = QComboBox()
        self.role_combo.addItems(["admin", "azs"])

        self.approval_code_input = QLineEdit()
        self.approval_code_input.setPlaceholderText("Код підтвердження (від адміністратора)")

        self.register_button = QPushButton("Зареєструватися")
        self.register_button.clicked.connect(self.register_user)

        layout.addRow("Повне ім'я:", self.fullname_input)
        layout.addRow("Логін:", self.username_input)
        layout.addRow("Пароль:", self.password_input)
        layout.addRow("Роль:", self.role_combo)
        layout.addRow("Код підтвердження:", self.approval_code_input)
        layout.addRow(self.register_button)

        self.setLayout(layout)

    def register_user(self):
        """Реєструє нового користувача в базі даних"""
        fullname = self.fullname_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_combo.currentText()
        approval_code = self.approval_code_input.text().strip()

        ADMIN_CODE = "12345"  # Код для підтвердження реєстрації адміністратором

        print(f"[DEBUG] Спроба реєстрації: {username}, роль: {role}")

        if not fullname or not username or not password or not approval_code:
            print("[DEBUG] Помилка: Не всі поля заповнені")
            QMessageBox.warning(self, "Помилка", "Всі поля мають бути заповнені!")
            return

        if approval_code != ADMIN_CODE:
            print("[DEBUG] Невірний код підтвердження")
            QMessageBox.warning(self, "Помилка", "Невірний код підтвердження!")
            return

        approved_by = "Супер Адмін"

        if self.db.add_user(fullname, username, password, role, approved_by):
            print(f"[DEBUG] Користувач {username} успішно зареєстрований")
            QMessageBox.information(self, "Успіх", "Користувач успішно зареєстрований!")
            self.close()
        else:
            print(f"[DEBUG] Не вдалося зареєструвати {username} (логін вже існує?)")
            QMessageBox.warning(self, "Помилка", "Помилка при реєстрації. Можливо, логін вже існує!")
