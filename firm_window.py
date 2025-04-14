from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QMessageBox, QLineEdit, QInputDialog
)
from PyQt6.QtCore import Qt


class FirmWindow(QWidget):
    def __init__(self, firm_name, db, update_main_window_callback, user):
        super().__init__()
        self.firm_name = firm_name
        self.db = db
        self.user = user  # ← ДОДАНО
        self.update_main_window_callback = update_main_window_callback
        self.setWindowTitle(f"Талони для фірми {self.firm_name}")
        self.resize(900, 500)

        self.scanned_tickets = []
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        self.firm_label = QLabel(f"Талони для фірми: {self.firm_name}", self)
        self.layout.addWidget(self.firm_label)

        self.active_tickets_table = QTableWidget(self)
        self.layout.addWidget(self.active_tickets_table)

        self.load_tickets()

        self.activate_button = QPushButton("Активувати всі талони", self)
        self.activate_button.clicked.connect(self.activate_scanned_tickets)
        self.layout.addWidget(self.activate_button)

        self.scanned_tickets_table = QTableWidget(self)
        self.scanned_tickets_table.setHorizontalHeaderLabels(
            ["Штрих-код", "Тип палива", "Номер талону", "Накладна", "Кількість (л)", "Статус"]
        )
        self.layout.addWidget(self.scanned_tickets_table)
        self.total_liters_label = QLabel("Загальна кількість літрів: 0", self)
        self.layout.addWidget(self.total_liters_label)

        self.scanner_input = QLineEdit(self)
        self.scanner_input.setPlaceholderText("Введіть або відскануйте штрих-код і натисніть Enter")
        self.scanner_input.returnPressed.connect(self.add_scanned_ticket)
        self.layout.addWidget(self.scanner_input)

    def load_tickets(self):
        try:
            tickets = self.db.get_tickets_by_firm(self.firm_name)
            self.active_tickets_table.setRowCount(len(tickets))
            self.active_tickets_table.setColumnCount(8)
            self.active_tickets_table.setHorizontalHeaderLabels([
                "Номер талону", "Тип палива", "Накладна", "Кількість (л)",
                "Статус", "Дата активації", "Дата деактивації", "Ким змінено"
            ])

            print("[DEBUG] Список талонів після get_tickets_by_firm:", tickets)

            for row, ticket in enumerate(tickets):
                ticket_number = ticket["ticket_number"]
                fuel_type = self.convert_fuel_type(ticket["fuel_type"])
                invoice_number = ticket["invoice_number"] if ticket["invoice_number"] else "Немає"
                quantity = str(ticket["quantity"])
                status = "Активний" if ticket["status"] == "active" else "Деактивований"

                date_activated = ticket["date_activated"] if ticket["date_activated"] else "—"
                # ✅ Показує дату деактивації тільки для неактивних талонів
                date_deactivated = ticket["date_activated"] if ticket["status"] == "inactive" else "—"
                modified_by = ticket["modified_by"] if ticket["modified_by"] else "Невідомо"

                self.active_tickets_table.setItem(row, 0, self.create_readonly_item(ticket_number))
                self.active_tickets_table.setItem(row, 1, self.create_readonly_item(fuel_type))
                self.active_tickets_table.setItem(row, 2, self.create_readonly_item(invoice_number))
                self.active_tickets_table.setItem(row, 3, self.create_readonly_item(quantity))
                self.active_tickets_table.setItem(row, 4, self.create_readonly_item(status))
                self.active_tickets_table.setItem(row, 5, self.create_readonly_item(date_activated))
                self.active_tickets_table.setItem(row, 6, self.create_readonly_item(date_deactivated))
                self.active_tickets_table.setItem(row, 7, self.create_readonly_item(modified_by))

        except Exception as e:
            print(f"[ERROR] Помилка при завантаженні талонів: {e}")
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити талони для фірми. Помилка: {e}")

    def create_readonly_item(self, text):
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def convert_fuel_type(self, fuel_type):
        fuel_map = {
            "A-95X": "A-95X",
            "A-95Standart": "A-95St.",
            "A-95Premium": "A-95Pr.",
            "Газ": "Газ"
        }
        return fuel_map.get(fuel_type, fuel_type)

    def add_scanned_ticket(self):
        try:
            scanned_code = self.scanner_input.text().strip()
            if scanned_code:
                ticket_info = self.db.get_ticket_info_by_code(scanned_code)
                if ticket_info:
                    self.scanned_tickets.append(ticket_info)
                    self.update_scanned_tickets_table()
                    self.scanner_input.clear()
                else:
                    QMessageBox.warning(self, "Попередження", "Талон не знайдено.")
            else:
                QMessageBox.warning(self, "Помилка", "Поле штрих-коду порожнє.")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Сталася помилка при додаванні талону. Помилка: {e}")

    def update_scanned_tickets_table(self):
        self.scanned_tickets_table.setColumnCount(6)
        self.scanned_tickets_table.setRowCount(len(self.scanned_tickets))
        self.scanned_tickets_table.setHorizontalHeaderLabels([
            "Штрих-код", "Тип палива", "Номер талону", "Кількість (л)", "Накладна", "Статус"
        ])
        for row, ticket in enumerate(self.scanned_tickets):
            self.scanned_tickets_table.setItem(row, 0, QTableWidgetItem(ticket["barcode"]))
            self.scanned_tickets_table.setItem(row, 1, QTableWidgetItem(ticket["fuel_type"]))
            self.scanned_tickets_table.setItem(row, 2, QTableWidgetItem(ticket["ticket_number"]))
            self.scanned_tickets_table.setItem(row, 3, QTableWidgetItem(str(ticket["quantity"])))
            invoice_number = ticket["invoice_number"] if ticket["invoice_number"] else "—"
            self.scanned_tickets_table.setItem(row, 4, QTableWidgetItem(invoice_number))
            status = "Активний" if ticket["status"] == "active" else "Не активовано"
            self.scanned_tickets_table.setItem(row, 5, QTableWidgetItem(status))

        total_liters = sum(ticket["quantity"] for ticket in self.scanned_tickets)
        self.total_liters_label.setText(f"Загальна кількість літрів: {total_liters}")

    def activate_scanned_tickets(self):
        try:
            if not self.scanned_tickets:
                QMessageBox.warning(self, "Помилка", "Будь ласка, відскануйте хоча б один талон.")
                return

            invoice_number, ok = QInputDialog.getText(self, "Номер накладної", "Введіть номер накладної:")
            if not ok or not invoice_number.strip():
                QMessageBox.warning(self, "Попередження", "Номер накладної не введений.")
                return

            firm_id = self.db.get_firm_id_by_name(self.firm_name)

            for ticket in self.scanned_tickets:
                self.db.activate_ticket_with_invoice(
                    barcode=ticket["barcode"],
                    invoice_number=invoice_number.strip(),
                    firm_id=firm_id,
                    modified_by=self.user["fullname"]  # ← ДОДАНО!
                )

            self.load_tickets()
            self.scanned_tickets.clear()
            self.update_scanned_tickets_table()
            self.update_main_window_callback()

            QMessageBox.information(self, "Успіх", "Талони активовані.")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Сталася помилка при активації. {e}")
