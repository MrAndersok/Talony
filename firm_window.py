from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox, QLineEdit, QInputDialog
from PyQt6.QtCore import Qt



class FirmWindow(QWidget):
    def __init__(self, firm_name, db, update_main_window_callback):
        super().__init__()
        self.firm_name = firm_name
        self.db = db
        self.update_main_window_callback = update_main_window_callback
        self.setWindowTitle(f"Талони для фірми {self.firm_name}")
        self.resize(800, 500)

        self.scanned_tickets = []  # Список для збереження сканованих талонів
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)

        # Назва фірми
        self.firm_label = QLabel(f"Талони для фірми: {self.firm_name}", self)
        self.layout.addWidget(self.firm_label)

        # Таблиця активних талонів (з накладною і кількістю)
        self.active_tickets_table = QTableWidget(self)
        self.layout.addWidget(self.active_tickets_table)

        # Завантаження активних талонів
        self.load_tickets()

        # Кнопка активації
        self.activate_button = QPushButton("Активувати всі талони", self)
        self.activate_button.clicked.connect(self.activate_scanned_tickets)
        self.layout.addWidget(self.activate_button)

        # Таблиця для сканованих талонів
        self.scanned_tickets_table = QTableWidget(self)
        self.scanned_tickets_table.setHorizontalHeaderLabels(["Штрих-код", "Тип палива", "Номер талону", "Накладна", "Кількість (л)", "Статус"])
        self.layout.addWidget(self.scanned_tickets_table)

        # Поле для вводу штрих-коду
        self.scanner_input = QLineEdit(self)
        self.scanner_input.setPlaceholderText("Введіть або відскануйте штрих-код тут і натисніть Enter")
        self.scanner_input.returnPressed.connect(self.add_scanned_ticket)  # Відправка при Enter
        self.layout.addWidget(self.scanner_input)

    def load_tickets(self):
        """Завантажує активні талони для фірми"""
        try:
            tickets = self.db.get_tickets_by_firm(self.firm_name)
            print(f"Отримані талони з БД для {self.firm_name}: {tickets}")

            self.active_tickets_table.setRowCount(len(tickets))
            self.active_tickets_table.setColumnCount(5)  # Додаємо колонку для кількості
            self.active_tickets_table.setHorizontalHeaderLabels(
                ["Номер талону", "Тип палива", "Накладна", "Кількість (л)", "Статус"])

            for row, ticket in enumerate(tickets):
                ticket_number, fuel_type, invoice_number, quantity, status = ticket

                self.active_tickets_table.setItem(row, 0, self.create_readonly_item(ticket_number))
                self.active_tickets_table.setItem(row, 1, self.create_readonly_item(fuel_type))
                self.active_tickets_table.setItem(row, 2, self.create_readonly_item(
                    invoice_number if invoice_number else "Немає"))
                self.active_tickets_table.setItem(row, 3, self.create_readonly_item(str(quantity)))

                # Статус
                status_text = "Активний" if status == 'active' else "Не активовано"
                status_item = self.create_readonly_item(status_text)

                # Кольори статусу
                if status == 'active':
                    status_item.setBackground(Qt.GlobalColor.green)  # Зелений для активного
                    status_item.setForeground(Qt.GlobalColor.white)  # Білий текст
                else:
                    status_item.setBackground(Qt.GlobalColor.red)  # Червоний для неактивного
                    status_item.setForeground(Qt.GlobalColor.white)  # Білий текст

                self.active_tickets_table.setItem(row, 4, status_item)

        except Exception as e:
            print(f"Помилка при завантаженні талонів: {e}")
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити талони для фірми. Помилка: {e}")

    def create_readonly_item(self, text):
        """Створює не редаговану клітинку"""
        item = QTableWidgetItem(str(text))
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        return item

    def add_scanned_ticket(self):
        """Додає сканований (введений) талон в таблицю"""
        try:
            scanned_code = self.scanner_input.text().strip()
            print(f"Введено штрих-код: {scanned_code}")

            if scanned_code:
                ticket_info = self.db.get_ticket_info_by_code(scanned_code)

                if ticket_info:
                    print(f"Знайдено талон: {dict(ticket_info)}")  # <-- Додай цей рядок!
                    self.scanned_tickets.append(ticket_info)
                    self.update_scanned_tickets_table()
                    self.scanner_input.clear()  # Очищаємо поле після додавання
                else:
                    QMessageBox.warning(self, "Попередження", "Талон не знайдено.")
            else:
                QMessageBox.warning(self, "Помилка", "Поле штрих-коду порожнє.")
        except Exception as e:
            print(f"Помилка при додаванні талону: {e}")
            QMessageBox.critical(self, "Помилка", f"Сталася помилка при додаванні талону. Помилка: {e}")

    def update_scanned_tickets_table(self):
        """Оновлює таблицю з відсканованими талонами"""
        self.scanned_tickets_table.setColumnCount(6)  # 6 колонок!
        self.scanned_tickets_table.setHorizontalHeaderLabels([
            "Штрих-код", "Тип палива", "Номер талону", "Кількість (л)", "Накладна", "Статус"
        ])
        self.scanned_tickets_table.setRowCount(len(self.scanned_tickets))

        for row, ticket in enumerate(self.scanned_tickets):
            ticket_id = ticket["barcode"]
            fuel_type = ticket["fuel_type"]
            ticket_number = ticket["ticket_number"]
            quantity = ticket["quantity"]  # Кількість літрів
            invoice_number = ticket["invoice_number"] if ticket["invoice_number"] else "Немає"  # Перевірка на None
            status = "Активний" if ticket["status"] == 'active' else "Не активовано"

            self.scanned_tickets_table.setItem(row, 0, self.create_readonly_item(ticket_id))
            self.scanned_tickets_table.setItem(row, 1, self.create_readonly_item(fuel_type))
            self.scanned_tickets_table.setItem(row, 2, self.create_readonly_item(ticket_number))
            self.scanned_tickets_table.setItem(row, 3, self.create_readonly_item(str(quantity)))  # Кількість
            self.scanned_tickets_table.setItem(row, 4, self.create_readonly_item(invoice_number))  # Накладна
            self.scanned_tickets_table.setItem(row, 5, self.create_readonly_item(status))  # Статус

    def activate_scanned_tickets(self):
        """Активує всі скановані талони і додає номер накладної"""
        try:
            if not self.scanned_tickets:
                QMessageBox.warning(self, "Помилка", "Будь ласка, відскануйте хоча б один талон.")
                return

            # Відкрити діалог для введення номера накладної
            invoice_number, ok = QInputDialog.getText(self, "Номер накладної", "Введіть номер накладної для цих талонів:")
            if not ok or not invoice_number.strip():
                QMessageBox.warning(self, "Попередження", "Номер накладної не введений. Активацію скасовано.")
                return

            # Отримати firm_id
            firm_id = self.db.get_firm_id_by_name(self.firm_name)

            # Активувати всі талони
            for ticket in self.scanned_tickets:
                ticket_code = ticket["barcode"]
                self.db.activate_ticket_with_invoice(ticket_code, invoice_number.strip(), firm_id)

            # Оновити активні талони
            self.load_tickets()

            # Очистити скановані
            self.scanned_tickets.clear()
            self.update_scanned_tickets_table()

            self.update_main_window_callback()

            QMessageBox.information(self, "Успіх", "Всі талони активовані і прив'язані до накладної.")
        except Exception as e:
            print(f"Помилка при активації талонів: {e}")
            QMessageBox.critical(self, "Помилка", f"Сталася помилка при активації талонів. Помилка: {e}")
