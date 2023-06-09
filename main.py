import _sqlite3
import re
from argparse import ArgumentParser

customer_id: str = ''
item_name: str = ''
item_counts: int = 0
item_price: int = 0
check_order_args: bool = False
update_order_args: bool = False
delete_order_args: bool = False
reset_transactions_args: bool = False
checkout_order_args: bool = False
new_item_name: str = ''
new_item_price: int = 0
new_item_counts: int = 0


def parse_user_inputs():
    global customer_id
    global item_name
    global item_price
    global item_counts
    global check_order_args
    global update_order_args
    global delete_order_args
    global reset_transactions_args
    global checkout_order_args

    parser = ArgumentParser(description='Manage supermarket orders.')

    parser.add_argument('--customer-id',
                        help='The ID of the customer. Must start with a letter or underscore, and can only contain '
                             'letters, digits, and underscores')
    parser.add_argument('--item-name', help='The name of the item')
    parser.add_argument('--item-counts', type=int, help='The count of the item')
    parser.add_argument('--item-price', type=int, help='The price of the item')
    parser.add_argument('--check-order', action='store_true', help='Check all orders.')
    parser.add_argument('--update-order', action='store_true', help='Update order. Please provided relevant data.')
    parser.add_argument('--delete-order', action='store_true', help='Delete one row of order data in the database.')
    parser.add_argument('--reset-transactions', action='store_true', help='Reset all transactions in the database.')
    parser.add_argument('--checkout-order', action='store_true', help='Checkout order.')

    args = parser.parse_args()

    customer_id = args.customer_id
    item_name = str(args.item_name).lower()
    item_counts = args.item_counts
    item_price = args.item_price
    check_order_args = args.check_order
    update_order_args = args.update_order
    delete_order_args = args.delete_order
    reset_transactions_args = args.reset_transactions
    checkout_order_args = args.checkout_order


def process_input_args():
    if customer_id:
        if not is_valid_sql_identifier(customer_id):
            print('Your customer id should be letters, digits, and underscores only. (ex: nama123)')
            return

        try:
            if not is_table_exists(customer_id):
                create_table()
        except _sqlite3.Error as e:
            print(f'An error occurred: {e.args[0]}')
            return

        if item_name and item_price and item_counts:
            process_add_item()
        elif update_order_args is not False:
            process_update_order_inputs()
        elif check_order_args is not False:
            process_check_order()
        elif delete_order_args is not False:
            process_delete_order()
        elif reset_transactions_args is not False:
            process_reset_transactions()
        elif checkout_order_args is not False:
            process_checkout_order()
        else:
            print(f"Customer {customer_id}, silahkan masukkan command dengan valid.")
    else:
        print(f"Masukkan customer ID anda.")


def is_valid_sql_identifier(s):
    return re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', s) is not None


def create_table():
    conn = _sqlite3.connect('supermarket.db')
    c = conn.cursor()
    table_name = customer_id

    c.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            item_name TEXT,
            item_counts INTEGER,
            item_price INTEGER,
            item_total_price INTEGER,
            total_discount REAL,
            total_discounted_price REAL
        )
    ''')

    conn.commit()
    conn.close()


def add_item():
    conn = _sqlite3.connect('supermarket.db')
    c = conn.cursor()
    table_name = customer_id

    item_total_price = item_counts * item_price
    total_discount = 0
    total_discounted_price = item_total_price - total_discount

    c.execute(f'''
    INSERT INTO {table_name} (item_name, item_counts, item_price, item_total_price, total_discount, total_discounted_price)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (item_name, item_counts, item_price, item_total_price, total_discount, total_discounted_price))

    conn.commit()
    conn.close()


def update_order():
    global new_item_price
    global new_item_counts
    global new_item_name

    conn = _sqlite3.connect('supermarket.db')
    c = conn.cursor()
    table_name = customer_id

    try:
        query = f"UPDATE {table_name} SET item_name = ?"
        data = [new_item_name]

        if new_item_price:
            query += ", item_price = ?"
            data.append(new_item_price)
        if new_item_counts:
            query += ", item_counts = ?"
            data.append(new_item_counts)

        query += " WHERE item_name = ?"
        data.append(item_name)  # Original item_name, not the new_item_name

        c.execute(query, data)
        conn.commit()
        c.close()

        print('Proses update item selesai.')
    except _sqlite3.Error as e:
        print(f'An error occurred: {e.args[0]}')
        return


def reset_transactions():
    conn = _sqlite3.connect('supermarket.db')
    c = conn.cursor()
    table_name = customer_id

    try:
        c.execute(f"DELETE FROM {table_name}")
        conn.commit()
        conn.close()
        print(f'Transaksi customer {table_name} berhasil direset.')

    except _sqlite3.Error as e:
        print(f'An error occurred: {e.args[0]}')
        return


def is_table_exists(table_name):
    try:
        conn = _sqlite3.connect('supermarket.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        result = cursor.fetchone()
        cursor.close()
        return result is not None
    except _sqlite3.Error as e:
        print(f"An error occurred: {e.args[0]}")
        return False


def process_add_item():
    try:
        add_item()
        print('Pesananmu sudah kami simpan di database.')
    except _sqlite3.Error as e:
        print(f'An error occurred: {e.args[0]}')
        return


def process_update_order_inputs():
    global new_item_name
    global new_item_price
    global new_item_counts

    new_item_name_input = input('Masukkan nama item baru: ').lower()
    new_item_price_input = input("Update juga harga item? (Y/N): ").lower()
    new_item_counts_input = input("Update juga jumlah item? (Y/N): ").lower()

    if new_item_name_input is not None:
        new_item_name = new_item_name_input
    else:
        print('Masukkan nama item yang ingin diupdate.')
        return

    if new_item_price_input != 'n':
        new_item_price = int(input('Silahkan masukkan HARGA item yang ingin diupdate: '))
    if new_item_counts_input != 'n':
        new_item_counts = int(input('Silahkan masukkan JUMLAH item yang ingin diupdate: '))
    update_order()


def process_check_order():
    conn = _sqlite3.connect('supermarket.db')
    c = conn.cursor()
    table_name = customer_id

    try:
        check_existing_row()

        c.execute(f'SELECT * FROM {table_name}')

        # Fetch all rows
        rows = c.fetchall()

        # Display data
        for row in rows:
            print(f'[Id | {row[0]}] [Nama | {row[1]}] [Jumlah | {row[2]}] [Harga | {row[3]}] '
                  f'[Total | {row[4]}] [Diskon | {row[5]}] [Total setelah diskon | {row[6]}]')
    except _sqlite3.Error as e:
        print(f'An error occurred: {e.args[0]}')
    finally:
        conn.close()


def process_delete_order():
    conn = _sqlite3.connect('supermarket.db')
    c = conn.cursor()
    table_name = customer_id

    try:
        check_existing_row()

        c.execute(f"DELETE FROM {table_name} WHERE item_name = ?", [item_name])
        conn.commit()
        conn.close()
        print(f'Item {item_name} berhasil dihapus.')

    except _sqlite3.Error as e:
        print(f'An error occurred: {e.args[0]}')
        return


def process_reset_transactions():
    reset_transactions_confirmations = input('Apakah kamu yakin ingin mereset transaksi? (Y/N): ').lower()

    if reset_transactions_confirmations == 'y':
        reset_transactions()
    else:
        print('Transaksi tidak jadi direset.')
        return


def process_checkout_order():
    conn = _sqlite3.connect('supermarket.db')
    c = conn.cursor()
    table_name = customer_id

    try:
        check_existing_row()

        c.execute(f'SELECT SUM(item_total_price) FROM {table_name}')
        total_price = c.fetchone()[0]

        if total_price > 500000:
            discount = 0.07
        elif total_price > 300000:
            discount = 0.06
        elif total_price > 200000:
            discount = 0.05
        else:
            discount = 0

        total_price_after_discount = total_price - (total_price * discount)
        print(f'Total harga: {total_price}')
        print(f'Diskon: {discount * 100}%')
        print(f'Total harga setelah diskon: {total_price_after_discount}')

    except _sqlite3.Error as e:
        print(f'An error occurred: {e.args[0]}')
        return

    finally:
        conn.close()


def check_existing_row():
    conn = _sqlite3.connect('supermarket.db')
    c = conn.cursor()
    table_name = customer_id

    # Check if table exists and has records
    c.execute(f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    row = c.fetchone()

    if row is None or row[0] != 1:
        print(f'Customer {table_name} tidak memiliki data di database.')
        return
    else:
        c.execute(f'SELECT count(*) FROM {table_name}')
        if c.fetchone()[0] == 0:
            print(f'Data customer {table_name} tidak memiliki record data.')
            return


def main():
    parse_user_inputs()
    process_input_args()


main()
