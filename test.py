from database import Database

def print_all_tickets():
    db = Database()
    tickets = db.get_all_tickets()

    if tickets:
        print(f"Знайдено {len(tickets)} талонів:")
        for i, ticket in enumerate(tickets, start=1):
            print(f"[{i}] Номер талону: {ticket['ticket_number']}, Тип палива: {ticket['fuel_type']}, "
                  f"Кількість: {ticket['quantity']}л, Статус: {ticket['status']}, "
                  f"Штрих-код: {ticket['barcode']}, Дата створення: {ticket['date_created']}")
    else:
        print("❌ Талони не знайдено.")

if __name__ == "__main__":
    print_all_tickets()
