from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox, QDateEdit, QMessageBox
from PyQt6.QtCore import QDate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.graphics.barcode import code128
from reportlab.lib.colors import black, gray
from database import Database

# ✅ Шрифти через resource_path
pdfmetrics.registerFont(TTFont('TimesNewRoman', ('times.ttf')))
pdfmetrics.registerFont(TTFont('TimesNewRomanBold', ('timesbd.ttf')))
pdfmetrics.registerFont(TTFont('TimesNewRomanItalic', ('timesi.ttf')))
pdfmetrics.registerFont(TTFont('TimesNewRomanBoldItalic', ('timesbi.ttf')))
pdfmetrics.registerFont(TTFont('ArialCyr', ('Arial Cyr.ttf')))
pdfmetrics.registerFont(TTFont('ODESSA', ('ODESSA.ttf')))
pdfmetrics.registerFont(TTFont('KarinaBlackItalic', ('Karina Black Italic.ttf')))
pdfmetrics.registerFont(TTFont('GazetaTitul', ('Gazeta Titul Bold.ttf')))


class TalonGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.db = Database()  # Підключення до бази
        self.setWindowTitle("Генератор талонів")
        self.setGeometry(600, 300, 400, 250)
        self.layout = QVBoxLayout()
        self.init_ui()
        self.setLayout(self.layout)

    def init_ui(self):
        self.fuel_label = QLabel("Тип палива:")
        self.layout.addWidget(self.fuel_label)
        self.fuel_combo = QComboBox()
        self.fuel_combo.addItems(["A-95X", "A-95St.", "A-95Pr.", "Газ", "ДП"])
        self.layout.addWidget(self.fuel_combo)

        self.nominal_label = QLabel("Номінал (л):")
        self.layout.addWidget(self.nominal_label)
        self.nominal_combo = QComboBox()
        self.nominal_combo.addItems(["5", "10", "20", "50", "100"])
        self.layout.addWidget(self.nominal_combo)

        self.date_label = QLabel("Дійсний до:")
        self.layout.addWidget(self.date_label)
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.setDate(QDate.currentDate())
        self.layout.addWidget(self.date_edit)

        self.count_label = QLabel("Кількість талонів:")
        self.layout.addWidget(self.count_label)
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 1000)
        self.layout.addWidget(self.count_spin)

        self.start_number_label = QLabel("Початковий номер талону:")
        self.layout.addWidget(self.start_number_label)
        self.start_number_spin = QSpinBox()
        self.start_number_spin.setRange(1, 100000)
        self.layout.addWidget(self.start_number_spin)

        self.generate_button = QPushButton("Згенерувати талони")
        self.generate_button.clicked.connect(self.generate_talons)
        self.layout.addWidget(self.generate_button)

    def generate_talons(self):
        try:
            fuel = self.fuel_combo.currentText()
            nominal = int(self.nominal_combo.currentText())
            valid_until = self.date_edit.date().toString("dd.MM.yyyy")
            count = self.count_spin.value()
            start_number = self.start_number_spin.value()

            filename = (f"talons_output/talony_{fuel}_{nominal}L_{start_number}_{count}.pdf")
            c = canvas.Canvas(filename, pagesize=A4)
            width, height = A4

            cols, rows = 4, 4
            cell_width = width / cols
            cell_height = height / rows

            current_number = start_number
            numbers_list = []
            barcodes_list = []

            # ---------- Лицьова сторона ----------
            for i in range(count):
                col = i % cols
                row = (i // cols) % rows

                x = col * cell_width
                y = height - (row + 1) * cell_height
                center_x = x + cell_width / 2

                number_str = f"{current_number:06d}"
                barcode_value = str(self.db.get_next_barcode()).zfill(12)

                numbers_list.append(number_str)
                barcodes_list.append(barcode_value)

                c.setFont("TimesNewRomanBold", 16)
                c.drawCentredString(center_x, y + cell_height - 15, "Україна")

                c.setFont("TimesNewRoman", 18)
                c.setFillColor(black)
                c.drawCentredString(center_x - 32, y + cell_height - 35, "НАФТО")
                c.setFont("TimesNewRomanBoldItalic", 16)
                c.setFillColor(gray)
                c.drawCentredString(center_x + 33, y + cell_height - 35, "ІНВЕСТ")
                c.setFillColor(black)

                c.setFont("ODESSA", 10)
                c.drawCentredString(center_x, y + cell_height - 50, "2025")

                c.drawImage(("img.png"), center_x - 17, y + cell_height - 80, width=35, height=18, mask='auto')

                c.setFont("KarinaBlackItalic", 28)
                c.drawCentredString(center_x, y + cell_height - 105, fuel)

                c.setFont("TimesNewRomanBold", 7)
                c.drawCentredString(center_x, y + cell_height - 118, "тел. (03858) 32-500")

                c.setFont("TimesNewRomanBoldItalic", 35)
                c.drawCentredString(center_x, y + cell_height - 150, f"*{nominal}л*")

                c.setFont("TimesNewRomanBoldItalic", 9)
                c.drawCentredString(center_x, y + cell_height - 163, f"({self.number_to_words(nominal)})")

                c.setFont("TimesNewRoman", 16)
                c.drawCentredString(center_x, y + cell_height - 185, f"№ {number_str}")

                c.setFont("ArialCyr", 9)
                c.drawCentredString(center_x, y + cell_height - 200, "Обмін заборонено")

                c.setLineWidth(0.5)
                c.rect(x, y, cell_width, cell_height)

                if (i + 1) % (cols * rows) == 0 and i + 1 < count:
                    c.showPage()

                current_number += 1

                self.db.add_generated_ticket(
                    ticket_number=number_str,
                    fuel_type=fuel,
                    quantity=nominal,
                    status='inactive',
                    barcode=barcode_value,
                    date_created=QDate.currentDate().toString("yyyy-MM-dd")
                )

            # ---------- Тильна сторона ----------
            pages = (count + cols * rows - 1) // (cols * rows)
            barcodes_paged = [barcodes_list[i * cols * rows:(i + 1) * cols * rows] for i in range(pages)]

            def mirror_rows(data, cols):
                rows_list = [data[i:i + cols] for i in range(0, len(data), cols)]
                return [item for row in rows_list for item in row[::-1]]

            for page_barcodes in barcodes_paged:
                while len(page_barcodes) < cols * rows:
                    page_barcodes.append("")

                mirrored_barcodes = mirror_rows(page_barcodes, cols)
                c.showPage()

                for idx, barcode_value in enumerate(mirrored_barcodes):
                    col = idx % cols
                    row = (idx // cols) % rows
                    x = col * cell_width
                    y = height - (row + 1) * cell_height
                    center_x = x + cell_width / 2

                    if barcode_value:
                        barcode_image = code128.Code128(barcode_value, barHeight=20 * mm, barWidth=0.5)
                        barcode_image.drawOn(c, center_x - (barcode_image.width / 2), y + cell_height / 2 - 10)
                        c.setFont("TimesNewRomanBold", 12)
                        c.drawCentredString(center_x, y + 10, f"дійсний до {valid_until}")

                    c.setLineWidth(0.5)
                    c.rect(x, y, cell_width, cell_height)

            c.save()
            QMessageBox.information(self, "Успіх", f"Талони збережено у файл:\n{filename}")

        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Сталася помилка: {e}")

    @staticmethod
    def number_to_words(n):
        return {5: "п’ять", 10: "десять", 20: "двадцять", 50: "п’ятдесят", 100: "сто"}.get(n, str(n))
import reportlab.graphics.barcode.code93

