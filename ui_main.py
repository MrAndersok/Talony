from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QInputDialog, \
    QMessageBox, QHeaderView
from database import Database
from firm_window import FirmWindow
from add_tickets_window import TalonGenerator  # Імпорт генератора PDF талонів
from DeactivationWindow import DeactivationWindow



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управління талонами")
        self.resize(600, 400)
        self.db = Database()

        self.selected_tickets = []  # Список для збереження ID талонів, які були вибрані

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.table_widget = QTableWidget(self)
        self.table_widget.cellDoubleClicked.connect(self.open_firm_window)
        self.layout.addWidget(self.table_widget)
        self.deactivate_button = QPushButton("Деактивувати талони")
        self.add_talons_button = QPushButton("Додати талони")  # Нова кнопка
        self.add_talons_button.clicked.connect(self.open_talon_generator)  # Підключення до функції відкриття генератора
        self.layout.addWidget(self.deactivate_button)
        self.layout.addWidget(self.add_talons_button)  # Додаємо кнопку в layout

        self.add_firm_button = QPushButton("Додати фірму")
        self.delete_firm_button = QPushButton("Видалити фірму")

        self.layout.addWidget(self.add_firm_button)
        self.layout.addWidget(self.delete_firm_button)

        # Підключаємо кнопки до функцій
        self.add_firm_button.clicked.connect(self.show_add_firm_dialog)
        self.delete_firm_button.clicked.connect(self.show_delete_firm_dialog)
        self.deactivate_button.clicked.connect(self.deactivate_tickets)

        self.load_firms()
        self.deactivate_button.clicked.connect(self.open_deactivation_window)

    def open_deactivation_window(self):
            self.deactivation_window = DeactivationWindow(self.db, self.load_firms)
            self.deactivation_window.show()

    def open_talon_generator(self):
        """Відкриває вікно генератора PDF талонів"""
        self.generator_window = TalonGenerator()
        self.generator_window.show()

    def load_firms(self):
        try:
            firms = self.db.get_firms()
            print(f"Отримані фірми: {firms}")

            if not firms:  # Якщо список порожній
                firms = [(None, None)]  # Тільки id та назва

            self.table_widget.setRowCount(len(firms))
            self.table_widget.setColumnCount(4)
            self.table_widget.setHorizontalHeaderLabels(["Фірма", "ДП", "92", "95"])

            # Розтягуємо стовпці
            self.table_widget.horizontalHeader().setStretchLastSection(True)
            for i in range(4):
                self.table_widget.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)

            for row, firm in enumerate(firms):
                firm_id = firm["id"]
                firm_name = firm["name"]

                # Отримуємо всі активні талони цієї фірми
                tickets = self.db.get_active_tickets_by_firm(firm_id)

                dp_sum = sum(ticket["quantity"] for ticket in tickets if ticket["fuel_type"] == "ДП")
                fuel92_sum = sum(ticket["quantity"] for ticket in tickets if ticket["fuel_type"] == "А-92")
                fuel95_sum = sum(ticket["quantity"] for ticket in tickets if ticket["fuel_type"] == "А-95")

                print(f"Фірма: {firm_name}, ДП: {dp_sum}, А-92: {fuel92_sum}, А-95: {fuel95_sum}")  # Debug

                # Створення клітинок
                firm_name_item = QTableWidgetItem(firm_name)
                dp_item = QTableWidgetItem(str(dp_sum))
                fuel92_item = QTableWidgetItem(str(fuel92_sum))
                fuel95_item = QTableWidgetItem(str(fuel95_sum))

                # Забороняємо редагування
                firm_name_item.setFlags(firm_name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                dp_item.setFlags(dp_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                fuel92_item.setFlags(fuel92_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                fuel95_item.setFlags(fuel95_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

                # Вставляємо у таблицю
                self.table_widget.setItem(row, 0, firm_name_item)
                self.table_widget.setItem(row, 1, dp_item)
                self.table_widget.setItem(row, 2, fuel92_item)
                self.table_widget.setItem(row, 3, fuel95_item)

        except Exception as e:
            self.show_error_message("Помилка при завантаженні фірм", str(e))

    def show_add_firm_dialog(self):
        try:
            text, ok = QInputDialog.getText(self, "Додати фірму", "Введіть назву фірми:")
            if ok and text.strip():
                self.db.add_firm(text.strip())
                self.load_firms()
        except Exception as e:
            self.show_error_message("Помилка при додаванні фірми", str(e))

    def open_firm_window(self, row, column):
        try:
            firm_name = self.table_widget.item(row, 0).text()
            if firm_name:
                self.firm_window = FirmWindow(firm_name, self.db, self.load_firms)
                self.firm_window.show()
        except Exception as e:
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
                    self.db.delete_firm(text.strip())
                    self.load_firms()
        except Exception as e:
            self.show_error_message("Помилка при видаленні фірми", str(e))

    def activate_tickets(self):
        try:
            if not self.selected_tickets:
                QMessageBox.warning(self, "Помилка", "Будь ласка, виберіть хоча б один талон для активації.")
                return
            for ticket_id in self.selected_tickets:
                self.db.activate_ticket(ticket_id)
            QMessageBox.information(self, "Успіх", f"{len(self.selected_tickets)} талонів активовано.")
            self.selected_tickets.clear()
            self.load_firms()
        except Exception as e:
            self.show_error_message("Помилка при активації талонів", str(e))

    def deactivate_tickets(self):
        try:
            if not self.selected_tickets:
                QMessageBox.warning(self, "Помилка", "Будь ласка, виберіть хоча б один талон для деактивації.")
                return
            for ticket_id in self.selected_tickets:
                self.db.deactivate_ticket(ticket_id)
            QMessageBox.information(self, "Успіх", f"{len(self.selected_tickets)} талонів деактивовано.")
            self.selected_tickets.clear()
            self.load_firms()
        except Exception as e:
            self.show_error_message("Помилка при деактивації талонів", str(e))

    def show_error_message(self, title, message):
        QMessageBox.critical(self, title, message)
