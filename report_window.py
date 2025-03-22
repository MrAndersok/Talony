import os
import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QDateEdit, QMessageBox
from PyQt6.QtCore import QDate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from database import Database


class ReportWindow(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db  # зберігаємо об'єкт, а не шлях
        self.setWindowTitle("Формування звіту")
        self.setGeometry(400, 300, 300, 200)
        self.layout = QVBoxLayout()

        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(QDate.currentDate())
        self.layout.addWidget(QLabel("Початкова дата:"))
        self.layout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.layout.addWidget(QLabel("Кінцева дата:"))
        self.layout.addWidget(self.end_date_edit)

        self.generate_button = QPushButton("Сформувати звіт")
        self.generate_button.clicked.connect(self.generate_report)
        self.layout.addWidget(self.generate_button)

        self.setLayout(self.layout)

    def generate_report(self):
        start = self.start_date_edit.date().toString("yyyy-MM-dd")
        end = self.end_date_edit.date().toString("yyyy-MM-dd")

        try:
            cursor = self.db.connection.cursor()
            cursor.execute('''
                SELECT f.name AS firm_name, t.fuel_type, t.quantity, t.modified_by, t.date_created
                FROM tickets t
                JOIN firms f ON f.id = t.firm_id
                WHERE t.status = 'inactive' AND t.date_created BETWEEN ? AND ?
            ''', (start, end))

            rows = cursor.fetchall()

            if not rows:
                QMessageBox.information(self, "Звіт", "За вказаний період не знайдено активованих талонів.")
                return

            # Підготовка даних
            grouped = {}
            fuels = ["ДП", "A-95X", "A-95St.", "A-95Pr.", "Газ"]
            for row in rows:
                azs = row["modified_by"]
                firm = row["firm_name"]
                grouped.setdefault(azs, {})
                grouped[azs].setdefault(firm, {ft: 0 for ft in fuels})
                grouped[azs][firm][row["fuel_type"]] += row["quantity"]

            folder = "generated_reports"
            os.makedirs(folder, exist_ok=True)
            filename = f"{folder}/report_{start}_to_{end}.pdf"

            pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            c.setFont("DejaVuSans", 12)
            y = height - 40

            # Заголовок
            c.drawCentredString(width / 2, y, "Звіт")
            y -= 20
            c.drawCentredString(width / 2, y, "про відпуск палива по талонах")
            y -= 20
            c.drawCentredString(width / 2, y, f"за період: {start} — {end}")
            y -= 30

            # Таблиця
            start_x = 40
            col_widths = [80, 140] + [60] * len(fuels)
            col_x = [start_x]
            for w in col_widths:
                col_x.append(col_x[-1] + w)

            # Заголовок таблиці
            c.setFont("DejaVuSans", 10)
            c.drawString(col_x[0], y, "№АЗС")
            c.drawString(col_x[1], y, "Назва підприємства")
            for i, fuel in enumerate(fuels):
                c.drawString(col_x[2 + i], y, fuel)
            y -= 20

            total_by_fuel = {f: 0 for f in fuels}

            for i, (azs, firms) in enumerate(grouped.items(), 1):
                c.drawString(col_x[0], y, f"АЗС{i}")
                y -= 20
                azs_total = {f: 0 for f in fuels}

                if not firms:
                    c.drawString(col_x[1], y, '" "')
                    y -= 20

                for firm, values in firms.items():
                    c.drawString(col_x[1], y, firm)
                    for j, fuel in enumerate(fuels):
                        val = values.get(fuel, 0)
                        if val:
                            c.drawString(col_x[2 + j], y, str(val))
                        azs_total[fuel] += val
                        total_by_fuel[fuel] += val
                    y -= 20
                    # Додай порожній рядок " "
                    c.drawString(col_x[1], y, '" "')
                    y -= 20

                c.drawString(col_x[1], y, "Всього по АЗС:")
                for j, fuel in enumerate(fuels):
                    c.drawString(col_x[2 + j], y, str(azs_total[fuel]))
                y -= 30

                if y < 100:
                    c.showPage()
                    c.setFont("DejaVuSans", 10)
                    y = height - 50

            # Разом за період
            c.drawString(col_x[1], y, "Разом за період:")
            for j, fuel in enumerate(fuels):
                c.drawString(col_x[2 + j], y, str(total_by_fuel[fuel]))
            c.save()

            QMessageBox.information(self, "Звіт", f"✅ Звіт збережено:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося згенерувати звіт: {e}")
