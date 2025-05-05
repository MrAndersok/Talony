import os
import sqlite3
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QDateEdit, QMessageBox, QComboBox
)
from PyQt6.QtCore import QDate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from database import Database


class ReportWindow(QWidget):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("Формування звіту")
        self.setGeometry(400, 300, 300, 300)
        self.layout = QVBoxLayout()

        self.layout.addWidget(QLabel("Тип звіту:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["По деактивованих талонах", "По активованих талонах"])
        self.report_type_combo.currentIndexChanged.connect(self.toggle_firm_selection)
        self.layout.addWidget(self.report_type_combo)

        self.firm_combo = QComboBox()
        self.firm_combo.setEnabled(False)
        self.layout.addWidget(QLabel("Оберіть фірму:"))
        self.layout.addWidget(self.firm_combo)
        self.load_firms()

        self.layout.addWidget(QLabel("Початкова дата:"))
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setDate(QDate.currentDate())
        self.layout.addWidget(self.start_date_edit)

        self.layout.addWidget(QLabel("Кінцева дата:"))
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.layout.addWidget(self.end_date_edit)

        self.generate_button = QPushButton("Сформувати звіт")
        self.generate_button.clicked.connect(self.generate_report)
        self.layout.addWidget(self.generate_button)

        self.setLayout(self.layout)

    def toggle_firm_selection(self):
        is_active = self.report_type_combo.currentText() == "По активованих талонах"
        self.firm_combo.setEnabled(is_active)

    def load_firms(self):
        try:
            cursor = self.db.connection.cursor()
            cursor.execute("SELECT name FROM firms ORDER BY name")
            firms = cursor.fetchall()
            self.firm_combo.clear()
            for firm in firms:
                self.firm_combo.addItem(firm["name"])
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити список фірм: {e}")

    def generate_report(self):
        start = self.start_date_edit.date().toString("yyyy-MM-dd")
        end = self.end_date_edit.date().toString("yyyy-MM-dd")
        report_type = self.report_type_combo.currentText()

        try:
            cursor = self.db.connection.cursor()

            if report_type == "По деактивованих талонах":
                cursor.execute('''
                    SELECT f.name AS firm_name, t.fuel_type, t.quantity, t.modified_by, t.date_created
                    FROM tickets t
                    JOIN firms f ON f.id = t.firm_id
                    WHERE t.status = 'inactive' AND t.date_created BETWEEN ? AND ?
                ''', (start, end))
            else:
                firm_name = self.firm_combo.currentText()
                cursor.execute('''
                    SELECT f.name AS firm_name, t.fuel_type, t.quantity, t.modified_by, t.date_activated as date_created
                    FROM tickets t
                    JOIN firms f ON f.id = t.firm_id
                    WHERE t.status = 'active' AND f.name = ? AND t.date_activated BETWEEN ? AND ?
                ''', (firm_name, start, end))

            rows = cursor.fetchall()

            if not rows:
                QMessageBox.information(self, "Звіт", "За вказаний період не знайдено талонів.")
                return

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
            suffix = "active" if report_type == "По активованих талонах" else "inactive"
            filename = f"{folder}/report_{suffix}_{start}_to_{end}.pdf"

            pdfmetrics.registerFont(TTFont("DejaVuSans", "DejaVuSans.ttf"))
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4
            LINE_HEIGHT = 28
            y = height - 40

            c.setFont("DejaVuSans", 12)
            c.drawCentredString(width / 2, y, "Звіт")
            y -= LINE_HEIGHT
            c.drawCentredString(width / 2, y, "про відпуск палива по талонах")
            y -= LINE_HEIGHT
            c.drawCentredString(width / 2, y, f"за період: {start} — {end}")
            y -= LINE_HEIGHT

            start_x = 40
            col_widths = [80, 140] + [60] * len(fuels)
            col_x = [start_x]
            for w in col_widths:
                col_x.append(col_x[-1] + w)

            c.setFont("DejaVuSans", 9)
            c.drawString(col_x[0], y, "№АЗС")
            c.drawString(col_x[1], y, "Назва підприємства")
            for i, fuel in enumerate(fuels):
                c.drawRightString(col_x[2 + i] + 50, y, fuel)
            y -= LINE_HEIGHT

            total_by_fuel = {f: 0 for f in fuels}

            for i, (azs, firms) in enumerate(grouped.items(), 1):
                if y < 70:
                    c.showPage()
                    c.setFont("DejaVuSans", 9)
                    y = height - 50

                c.drawString(col_x[0], y, f"АЗС{i}")
                y -= LINE_HEIGHT
                azs_total = {f: 0 for f in fuels}

                for firm, values in firms.items():
                    if y < 70:
                        c.showPage()
                        c.setFont("DejaVuSans", 9)
                        y = height - 50

                    from textwrap import wrap

                    max_firm_width = col_widths[1] - 5
                    words = firm.split()
                    lines = []
                    line = ""
                    for word in words:
                        test_line = line + " " + word if line else word
                        if c.stringWidth(test_line, "DejaVuSans", 9) < max_firm_width:
                            line = test_line
                        else:
                            lines.append(line)
                            line = word
                    if line:
                        lines.append(line)

                    # Виводимо кожен рядок
                    for idx, part in enumerate(lines):
                        if y < 70:
                            c.showPage()
                            c.setFont("DejaVuSans", 9)
                            y = height - 50

                        c.drawString(col_x[1], y, part)

                        if idx == 0:
                            # Показуємо значення тільки для першого рядка фірми
                            for j, fuel in enumerate(fuels):
                                val = values.get(fuel, 0)
                                if val:
                                    c.drawRightString(col_x[2 + j] + 50, y, str(val))
                                azs_total[fuel] += val
                                total_by_fuel[fuel] += val

                        y -= LINE_HEIGHT

                    # Порожній рядок після фірми
                    c.drawString(col_x[1], y, '')
                    y -= LINE_HEIGHT

                    for j, fuel in enumerate(fuels):
                        val = values.get(fuel, 0)
                        if val:
                            c.drawRightString(col_x[2 + j] + 50, y, str(val))
                        azs_total[fuel] += val
                        total_by_fuel[fuel] += val
                    y -= LINE_HEIGHT
                    c.drawString(col_x[1], y, '')  # порожній рядок
                    y -= LINE_HEIGHT

                c.drawString(col_x[1], y, "Всього по АЗС:")
                for j, fuel in enumerate(fuels):
                    c.drawRightString(col_x[2 + j] + 50, y, str(azs_total[fuel]))
                y -= LINE_HEIGHT * 1.5

            c.drawString(col_x[1], y, "Разом за період:")
            for j, fuel in enumerate(fuels):
                c.drawRightString(col_x[2 + j] + 50, y, str(total_by_fuel[fuel]))
            y -= LINE_HEIGHT * 1.5

            # Статистика: активовано / залишилось
            cursor2 = self.db.connection.cursor()
            if report_type == "По активованих талонах":
                firm_name = self.firm_combo.currentText()
                cursor2.execute("SELECT id FROM firms WHERE name = ?", (firm_name,))
                firm_row = cursor2.fetchone()
                firm_id = firm_row["id"] if firm_row else None

                cursor2.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'active' AND firm_id = ?",
                                (firm_id,))
                total_active = cursor2.fetchone()["count"]

                cursor2.execute("SELECT COUNT(*) as count FROM tickets WHERE status != 'active' AND firm_id = ?",
                                (firm_id,))
                total_left = cursor2.fetchone()["count"]
            else:
                cursor2.execute("SELECT COUNT(*) as count FROM tickets WHERE status = 'active'")
                total_active = cursor2.fetchone()["count"]

                cursor2.execute("SELECT COUNT(*) as count FROM tickets WHERE status != 'active'")
                total_left = cursor2.fetchone()["count"]

            c.setFont("DejaVuSans", 10)
            c.drawString(col_x[1], y, f"Всього активовано талонів: {total_active}")
            y -= LINE_HEIGHT
            c.drawString(col_x[1], y, f"Залишилось талонів: {total_left}")

            # Порахувати літри
            if report_type == "По активованих талонах":
                cursor2.execute("SELECT SUM(quantity) as liters FROM tickets WHERE status = 'active' AND firm_id = ?",
                                (firm_id,))
                liters_active = cursor2.fetchone()["liters"] or 0

                cursor2.execute("SELECT SUM(quantity) as liters FROM tickets WHERE status != 'active' AND firm_id = ?",
                                (firm_id,))
                liters_left = cursor2.fetchone()["liters"] or 0
            else:
                cursor2.execute("SELECT SUM(quantity) as liters FROM tickets WHERE status = 'active'")
                liters_active = cursor2.fetchone()["liters"] or 0

                cursor2.execute("SELECT SUM(quantity) as liters FROM tickets WHERE status != 'active'")
                liters_left = cursor2.fetchone()["liters"] or 0

            y -= LINE_HEIGHT
            c.drawString(col_x[1], y, f"Загальна кількість літрів активованих: {liters_active}")
            y -= LINE_HEIGHT
            c.drawString(col_x[1], y, f"Загальна кількість літрів залишених: {liters_left}")

            c.save()

            QMessageBox.information(self, "Звіт", f"✅ Звіт збережено:\n{filename}")

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося згенерувати звіт: {e}")


