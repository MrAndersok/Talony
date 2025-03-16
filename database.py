import sqlite3


class Database:
    def __init__(self, db_name="tickets.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.connection.row_factory = sqlite3.Row  # Доступ до полів за іменами
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """Створення таблиць, якщо не існують"""
        try:
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS firms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            ''')

            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                firm_id INTEGER,
                ticket_number TEXT NOT NULL,
                fuel_type TEXT NOT NULL,
                quantity INTEGER NOT NULL CHECK (quantity >= 0),
                status TEXT NOT NULL CHECK (status IN ('active', 'inactive')),
                activation_date TEXT,
                barcode TEXT UNIQUE,
                date_created TEXT,
                date_activated TEXT,
                invoice_number TEXT,
                FOREIGN KEY (firm_id) REFERENCES firms(id) ON DELETE CASCADE
            );
            ''')

            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Помилка при створенні таблиць: {e}")

    def add_firm(self, name):
        """Додає нову фірму"""
        try:
            self.cursor.execute("INSERT INTO firms (name) VALUES (?)", (name,))
            self.connection.commit()
        except sqlite3.IntegrityError:
            print(f"Фірма '{name}' вже існує")
        except sqlite3.Error as e:
            print(f"Помилка при додаванні фірми: {e}")

    def delete_firm(self, name):
        """Видалення фірми"""
        try:
            self.cursor.execute("DELETE FROM firms WHERE name = ?", (name,))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Помилка при видаленні фірми '{name}': {e}")

    def get_firms(self):
        """Список фірм"""
        try:
            self.cursor.execute("SELECT id, name FROM firms")
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Помилка при отриманні фірм: {e}")
            return []

    def get_firm_id_by_name(self, name):
        """Отримати ID фірми"""
        try:
            self.cursor.execute("SELECT id FROM firms WHERE name = ?", (name,))
            result = self.cursor.fetchone()
            return result["id"] if result else None
        except sqlite3.Error as e:
            print(f"Помилка при отриманні ID фірми: {e}")
            return None

    def get_tickets_by_firm(self, firm_name):
        """Отримати талони фірми"""
        try:
            self.cursor.execute('''
                SELECT t.ticket_number, t.fuel_type, t.invoice_number, t.quantity, t.status
                FROM tickets t
                JOIN firms f ON t.firm_id = f.id
                WHERE f.name = ?
            ''', (firm_name,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Помилка при отриманні талонів фірми '{firm_name}': {e}")
            return []

    def add_generated_ticket(self, ticket_number, fuel_type, quantity, status, barcode, date_created):
        """Додає згенерований талон"""
        try:
            self.cursor.execute('''
                INSERT INTO tickets (firm_id, ticket_number, fuel_type, quantity, status, activation_date, barcode, date_created)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (None, ticket_number, fuel_type, quantity, status, None, barcode, date_created))
            self.connection.commit()
        except sqlite3.IntegrityError:
            print(f"Талон з номером '{ticket_number}' вже існує")
        except sqlite3.Error as e:
            print(f"Помилка при додаванні талона: {e}")

    def get_ticket_info_by_code(self, barcode):
        """Інформація про талон по штрих-коду"""
        try:
            self.cursor.execute("SELECT * FROM tickets WHERE barcode = ?", (barcode,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Помилка при пошуку талона: {e}")
            return None

    def activate_ticket_with_invoice(self, barcode, invoice_number, firm_id):
        """Активація талона з накладною"""
        try:
            self.cursor.execute('''
                UPDATE tickets
                SET status = 'active',
                    invoice_number = ?,
                    firm_id = ?
                WHERE barcode = ?
            ''', (invoice_number, firm_id, barcode))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Помилка при активації талона: {e}")

    def get_next_barcode(self):
        """Отримати наступний унікальний штрих-код"""
        try:
            self.cursor.execute("SELECT MAX(CAST(barcode AS INTEGER)) as max_barcode FROM tickets")
            result = self.cursor.fetchone()
            return (result["max_barcode"] + 1) if result and result["max_barcode"] is not None else 1
        except sqlite3.Error as e:
            print(f"Помилка при отриманні останнього штрих-коду: {e}")
            return 1

    def activate_ticket(self, ticket_id):
        """Активація талона"""
        try:
            self.cursor.execute(
                "UPDATE tickets SET status = 'active', date_activated = CURRENT_DATE WHERE id = ?",
                (ticket_id,)
            )
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Помилка при активації талона {ticket_id}: {e}")

    def deactivate_ticket(self, ticket_id):
        """Деактивація талона"""
        try:
            self.cursor.execute(
                "UPDATE tickets SET status = 'inactive', date_activated = NULL WHERE id = ?",
                (ticket_id,)
            )
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Помилка при деактивації талона {ticket_id}: {e}")

    def get_all_tickets(self):
        """Усі талони"""
        try:
            self.cursor.execute('''
                SELECT ticket_number, fuel_type, quantity, status, barcode, date_created
                FROM tickets
                ORDER BY id DESC
            ''')
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Помилка при отриманні всіх талонів: {e}")
            return []

    def activate_ticket_by_barcode(self, barcode):
        """Активація за штрих-кодом"""
        try:
            self.cursor.execute("UPDATE tickets SET status = 'active' WHERE barcode = ?", (barcode,))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Помилка при активації талона {barcode}: {e}")

    def get_fuel_summary_by_firm(self):
        """Повертає суму літрів палива по кожній фірмі тільки для активних талонів"""
        try:
            self.cursor.execute("""
                SELECT 
                    f.name AS firm_name,
                    SUM(CASE WHEN t.fuel_type = 'ДП' AND t.status = 'active' THEN t.quantity ELSE 0 END) AS diesel,
                    SUM(CASE WHEN t.fuel_type = 'A-92' AND t.status = 'active' THEN t.quantity ELSE 0 END) AS a92,
                    SUM(CASE WHEN t.fuel_type = 'A-95' AND t.status = 'active' THEN t.quantity ELSE 0 END) AS a95
                FROM firms f
                LEFT JOIN tickets t ON f.id = t.firm_id
                GROUP BY f.id
            """)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Помилка при отриманні сум пального: {e}")
            return []

    def get_active_tickets_by_firm(self, firm_id):
        self.cursor.execute("""
            SELECT fuel_type, quantity FROM tickets
            WHERE firm_id = ? AND status = 'active'
        """, (firm_id,))
        return self.cursor.fetchall()

    def deactivate_ticket_by_barcode(self, barcode):
        """Деактивує талон за штрих-кодом"""
        try:
            self.cursor.execute("""
                UPDATE tickets SET status = 'inactive', date_activated = NULL WHERE barcode = ?
            """, (barcode,))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Помилка при деактивації талона {barcode}: {e}")

    def close(self):
        """Закрити базу"""
        self.connection.close()
