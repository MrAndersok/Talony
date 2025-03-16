from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QMessageBox
from PyQt6.QtCore import Qt



class DeactivationWindow(QWidget):
    def __init__(self, db, update_main_window_callback):
        super().__init__()
        self.db = db
        self.update_main_window_callback = update_main_window_callback  # Зберігаємо callback
        self.setWindowTitle("Деактивація талонів")
        self.resize(600, 480)

        self.scanned_tickets = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Таблиця для сканованих талонів
        self.scanned_tickets_table = QTableWidget()
        self.scanned_tickets_table.setColumnCount(5)
        self.scanned_tickets_table.setHorizontalHeaderLabels(["Штрих-код", "Тип палива", "Номер талону", "Кількість (л)", "Статус"])
        layout.addWidget(self.scanned_tickets_table)

        # Поле для введення штрих-коду
        self.scanner_input = QLineEdit()
        self.scanner_input.setPlaceholderText("Введіть або відскануйте штрих-код і натисніть Enter")
        self.scanner_input.returnPressed.connect(self.add_scanned_ticket)
        layout.addWidget(self.scanner_input)

        # Кнопка деактивації
        self.deactivate_button = QPushButton("Деактивувати всі")
        self.deactivate_button.clicked.connect(self.deactivate_scanned_tickets)
        layout.addWidget(self.deactivate_button)

        self.setLayout(layout)

    def add_scanned_ticket(self):
        """Додає талон за штрих-кодом до таблиці"""
        scanned_code = self.scanner_input.text().strip()

        if not scanned_code:
            return

        ticket_info = self.db.get_ticket_info_by_code(scanned_code)

        if ticket_info:
            self.scanned_tickets.append(ticket_info)
            self.update_scanned_tickets_table()
            self.scanner_input.clear()
        else:
            QMessageBox.warning(self, "Попередження", "Талон не знайдено або вже деактивовано.")

    def update_scanned_tickets_table(self):
        """Оновлює таблицю зі сканованими талонами"""
        self.scanned_tickets_table.setRowCount(len(self.scanned_tickets))

        for row, ticket in enumerate(self.scanned_tickets):
            ticket_id = ticket["barcode"]
            fuel_type = ticket["fuel_type"]
            ticket_number = ticket["ticket_number"]
            quantity = ticket["quantity"]
            status = "Активний" if ticket["status"] == "active" else "Не активовано"

            self.scanned_tickets_table.setItem(row, 0, self.create_readonly_item(ticket_id))
            self.scanned_tickets_table.setItem(row, 1, self.create_readonly_item(fuel_type))
            self.scanned_tickets_table.setItem(row, 2, self.create_readonly_item(ticket_number))
            self.scanned_tickets_table.setItem(row, 3, self.create_readonly_item(str(quantity)))
            self.scanned_tickets_table.setItem(row, 4, self.create_readonly_item(status))

    def create_readonly_item(self, text):
        """Створює не редаговану клітинку"""
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def deactivate_scanned_tickets(self):
        """Деактивує всі знайдені талони"""
        if not self.scanned_tickets:
            QMessageBox.warning(self, "Увага", "Список талонів порожній.")
            return

        for ticket in self.scanned_tickets:
            self.db.deactivate_ticket_by_barcode(ticket["barcode"])

        QMessageBox.information(self, "Успіх", "Талони успішно деактивовані.")
        self.scanned_tickets.clear()
        self.update_scanned_tickets_table()

        self.update_main_window_callback()
