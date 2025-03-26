from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QInputDialog, \
    QMessageBox, QLabel
from database import Database
from firm_window import FirmWindow
from add_tickets_window import TalonGenerator
from DeactivationWindow import DeactivationWindow
from report_window import ReportWindow

class MainWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = dict(user)
        print(f"[DEBUG] Ініціалізація MainWindow для {self.user['username']} (роль: {self.user['role']})")
        self.setWindowTitle("Управління талонами")
        self.resize(800, 500)
        self.db = Database()
        self.selected_tickets = []

        self.init_ui()

    def init_ui(self):
        print("[DEBUG] Створення елементів інтерфейсу")
        self.layout = QVBoxLayout(self)

        self.table_widget = QTableWidget(self)
        self.table_widget.cellDoubleClicked.connect(self.open_firm_window)
        self.layout.addWidget(self.table_widget)

        self.deactivate_button = QPushButton("Деактивувати талони")
        self.add_talons_button = QPushButton("Додати талони")
        self.add_talons_button.clicked.connect(self.open_talon_generator)

        self.layout.addWidget(self.deactivate_button)
        self.layout.addWidget(self.add_talons_button)

        self.add_firm_button = QPushButton("Додати фірму")
        self.delete_firm_button = QPushButton("Видалити фірму")

        self.layout.addWidget(self.add_firm_button)
        self.layout.addWidget(self.delete_firm_button)

        self.add_firm_button.clicked.connect(self.show_add_firm_dialog)
        self.delete_firm_button.clicked.connect(self.show_delete_firm_dialog)
        self.deactivate_button.clicked.connect(self.open_deactivation_window)

        self.report_button = QPushButton("Сформувати звіт")
        self.report_button.clicked.connect(self.open_report_window)
        self.layout.addWidget(self.report_button)

        print("[DEBUG] Завантаження даних фірм...")
        self.load_firms()

    def open_deactivation_window(self):
        print("[DEBUG] Відкриття вікна деактивації талонів")
        try:
            print(f"[DEBUG] self.user = {self.user}")
            self.deactivation_window = DeactivationWindow(self.db, self.user, self.load_firms)
            self.deactivation_window.show()
        except Exception as e:
            print(f"[ERROR] Неможливо відкрити DeactivationWindow: {e}")

    def open_talon_generator(self):
        print("[DEBUG] Відкриття генератора PDF талонів")
        self.generator_window = TalonGenerator()
        self.generator_window.show()

    def load_firms(self):
        try:
            firms = self.db.get_firms()
            print(f"[DEBUG] Отримані фірми: {firms}")

            if not firms:
                firms = [(None, None)]

            self.table_widget.setRowCount(len(firms))
            self.table_widget.setColumnCount(6)
            self.table_widget.setHorizontalHeaderLabels(["Фірма", "ДП", "A-95X", "A-95Standart", "A-95Premium", "Газ"])

            print("[DEBUG] Налаштування таблиці...")

            for row, firm in enumerate(firms):
                firm_id = firm["id"]
                firm_name = firm["name"]
                tickets = self.db.get_active_tickets_by_firm(firm_id)

                dp_sum = sum(t["quantity"] for t in tickets if t["fuel_type"] == "ДП")
                x95_sum = sum(t["quantity"] for t in tickets if t["fuel_type"] == "A-95X")
                s95_sum = sum(t["quantity"] for t in tickets if t["fuel_type"] == "A-95St.")
                p95_sum = sum(t["quantity"] for t in tickets if t["fuel_type"] == "A-95Pr.")
                gas_sum = sum(t["quantity"] for t in tickets if t["fuel_type"] == "Газ")

                print(f"[DEBUG] Фірма: {firm_name}, ДП: {dp_sum}, A-95X: {x95_sum}, A-Standart: {s95_sum}, A-Premium: {p95_sum}, Газ: {gas_sum}")

                self.table_widget.setItem(row, 0, self.create_readonly_item(firm_name))
                self.table_widget.setItem(row, 1, self.create_readonly_item(str(dp_sum)))
                self.table_widget.setItem(row, 2, self.create_readonly_item(str(x95_sum)))
                self.table_widget.setItem(row, 3, self.create_readonly_item(str(s95_sum)))
                self.table_widget.setItem(row, 4, self.create_readonly_item(str(p95_sum)))
                self.table_widget.setItem(row, 5, self.create_readonly_item(str(gas_sum)))

            print("[DEBUG] Завершення завантаження таблиці")

        except Exception as e:
            print(f"[ERROR] Помилка при завантаженні фірм: {e}")

    def create_readonly_item(self, text):
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def show_add_firm_dialog(self):
        try:
            text, ok = QInputDialog.getText(self, "Додати фірму", "Введіть назву фірми:")
            if ok and text.strip():
                print(f"[DEBUG] Додавання нової фірми: {text.strip()}")
                self.db.add_firm(text.strip())
                self.load_firms()
        except Exception as e:
            print(f"[DEBUG] ПОМИЛКА: {e}")
            self.show_error_message("Помилка при додаванні фірми", str(e))

    def open_firm_window(self, row, column):
        try:
            firm_name = self.table_widget.item(row, 0).text()
            if firm_name:
                print(f"[DEBUG] Відкриття вікна фірми: {firm_name}")
                self.firm_window = FirmWindow(firm_name, self.db, self.load_firms, self.user)
                self.firm_window.show()
        except Exception as e:
            print(f"[DEBUG] ПОМИЛКА: {e}")
            self.show_error_message("Помилка при відкритті вікна фірми", str(e))

    def show_delete_firm_dialog(self):
        try:
            text, ok = QInputDialog.getText(self, "Видалити фірму", "Введіть назву фірми для видалення:")
            if ok and text.strip():
                reply = QMessageBox.question(
                    self, "Підтвердження", f"Ви впевнені, що хочете видалити фірму '{text.strip()}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    print(f"[DEBUG] Видалення фірми: {text.strip()}")
                    self.db.delete_firm(text.strip())
                    self.load_firms()
        except Exception as e:
            print(f"[DEBUG] ПОМИЛКА: {e}")
            self.show_error_message("Помилка при видаленні фірми", str(e))

    def open_report_window(self):
        self.report_window = ReportWindow(self.db)
        self.report_window.show()

    def show_error_message(self, title, message):
        print(f"[DEBUG] ПОМИЛКА: {title} - {message}")
        QMessageBox.critical(self, title, message)
