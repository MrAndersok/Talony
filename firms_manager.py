from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QMessageBox, QHBoxLayout
)
from database import Database

class FirmsManager(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()

    def init_ui(self):
        """Налаштування інтерфейсу"""
        self.setWindowTitle("Управління фірмами")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Таблиця фірм
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Назва"])
        self.table.setColumnHidden(0, True)  # Ховаємо ID
        layout.addWidget(self.table)

        # Поле введення нової фірми
        self.input_firm = QLineEdit()
        self.input_firm.setPlaceholderText("Введіть назву фірми")

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Додати фірму")
        self.btn_delete = QPushButton("Видалити фірму")

        btn_layout.addWidget(self.input_firm)
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)

        layout.addLayout(btn_layout)

        # Прив'язка кнопок до методів
        self.btn_add.clicked.connect(self.add_firm)
        self.btn_delete.clicked.connect(self.delete_firm)

        self.setLayout(layout)

        # Завантаження фірм у таблицю
        self.load_firms()

    def load_firms(self):
        """Завантажує список фірм у таблицю"""
        self.table.setRowCount(0)  # Очищуємо таблицю
        firms = self.db.get_firms()

        for row_idx, (firm_id, name) in enumerate(firms):
            self.table.insertRow(row_idx)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(firm_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(name))

    def add_firm(self):
        """Додає нову фірму"""
        name = self.input_firm.text().strip()
        if not name:
            QMessageBox.warning(self, "Помилка", "Назва фірми не може бути порожньою!")
            return

        try:
            self.db.add_firm(name)
            self.input_firm.clear()
            self.load_firms()  # Оновити таблицю
        except ValueError as e:
            QMessageBox.warning(self, "Помилка", str(e))

    def delete_firm(self):
        """Видаляє вибрану фірму"""
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Помилка", "Оберіть фірму для видалення!")
            return

        firm_id = int(self.table.item(selected_row, 0).text())  # Отримуємо ID
        firm_name = self.table.item(selected_row, 1).text()

        reply = QMessageBox.question(
            self, "Підтвердження",
            f"Ви впевнені, що хочете видалити фірму '{firm_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db.delete_firm(firm_id)
                self.load_firms()  # Оновити таблицю
            except ValueError as e:
                QMessageBox.warning(self, "Помилка", str(e))

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = FirmsManager()
    window.show()
    sys.exit(app.exec())
