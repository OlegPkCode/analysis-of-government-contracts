import sqlite3 as sq
import csv

answer = input('Будет произведено перезаполнение даных таблицы по продуктам. Вы уверены? Если да, наберите "Yes"   ')

if answer == 'Yes':
    with sq.connect('/home/olejonos/pni.db') as con:
        cur = con.cursor()

        cur.execute('DROP TABLE IF EXISTS positions')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                sname TEXT,
                namea TEXT,
                name_dop TEXT,
                qty REAL,
                unit TEXT,
                price REAL,
                total REAL,
                contract TEXT,
                year INTEGER,
                customer TEXT,
                ftext TEXT,
                namesrs TEXT
            )
        ''')

        with open('/home/olejonos/list_pos.csv', 'r') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                cur.execute(
                    'INSERT INTO positions (namea, name_dop, qty, unit, price, total, contract, year, customer, ftext, namesrs) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    [row['name'].lower(), row['name_dop'], row['qty'].replace(',', '.'), row['unit'],
                     row['price'].replace(',', '.'), row['total'].replace(',', '.'), row['contract'],
                     row['year'], row['customer'], row['ftext'], row['name']])
