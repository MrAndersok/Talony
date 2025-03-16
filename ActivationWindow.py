from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox



class ActivationWindow(QWidget):
    def __init__(self, tickets, db, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Активація/Деактивація талонів")
        self.resize(600, 400)
        self.db = db
        self.tickets = tickets  # Список талонів для активації/деактивації
        self.selected_tickets = []  # Список вибраних талонів

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Створюємо таблицю для відображення талонів
        self.table_widget = QTableWidget(self)
        self.table_widget.setRowCount(len(self.tickets))
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(
            ["Вибір", "Номер талону", "Тип палива", "Кількість", "Дата активації"])

        # Заповнюємо таблицю даними
        for row, ticket in enumerate(self.tickets):
            # Створюємо елементи для кожного стовпця
            select_item = QTableWidgetItem()  # Чекбокс для вибору
            select_item.setFlags(select_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)  # Додаємо чекбокс
            select_item.setCheckState(Qt.CheckState.Unchecked)

            ticket_id_item = QTableWidgetItem(str(ticket['id']))  # Номер талону
            fuel_type_item = QTableWidgetItem(ticket['fuel_type'])  # Тип палива
            amount_item = QTableWidgetItem(str(ticket['amount']))  # Кількість
            activation_date_item = QTableWidgetItem(ticket['activation_date'])  # Дата активації

            # Додаємо елементи в таблицю
            self.table_widget.setItem(row, 0, select_item)
            self.table_widget.setItem(row, 1, ticket_id_item)
            self.table_widget.setItem(row, 2, fuel_type_item)
            self.table_widget.setItem(row, 3, amount_item)
            self.table_widget.setItem(row, 4, activation_date_item)

        layout.addWidget(self.table_widget)

        # Кнопки для активації та деактивації
        self.activate_button = QPushButton("Активувати талони")
        self.deactivate_button = QPushButton("Деактивувати талони")
        layout.addWidget(self.activate_button)
        layout.addWidget(self.deactivate_button)

        # Підключаємо кнопки до функцій
        self.activate_button.clicked.connect(self.activate_tickets)
        self.deactivate_button.clicked.connect(self.deactivate_tickets)

    def activate_tickets(self):
        """Активує всі вибрані талони"""
        self.selected_tickets = self.get_selected_tickets()

        if not self.selected_tickets:
            QMessageBox.warning(self, "Помилка", "Будь ласка, виберіть хоча б один талон для активації.")
            return

        for ticket_id in self.selected_tickets:
            self.db.activate_ticket(ticket_id)

        QMessageBox.information(self, "Успіх", f"{len(self.selected_tickets)} талонів активовано.")
        self.close()  # Закриваємо вікно після активації

    def deactivate_tickets(self):
        """Деактивує всі вибрані талони"""
        self.selected_tickets = self.get_selected_tickets()

        if not self.selected_tickets:
            QMessageBox.warning(self, "Помилка", "Будь ласка, виберіть хоча б один талон для деактивації.")
            return

        for ticket_id in self.selected_tickets:
            self.db.deactivate_ticket(ticket_id)

        QMessageBox.information(self, "Успіх", f"{len(self.selected_tickets)} талонів деактивовано.")
        self.close()  # Закриваємо вікно після деактивації

    def get_selected_tickets(self):
        """Повертає список вибраних талонів для активації/деактивації"""
        selected_ids = []
        for row in range(self.table_widget.rowCount()):
            item = self.table_widget.item(row, 0)  # Чекбокс для вибору
            if item.checkState() == Qt.CheckState.Checked:
                ticket_id = int(self.table_widget.item(row, 1).text())
                selected_ids.append(ticket_id)
        return selected_ids
