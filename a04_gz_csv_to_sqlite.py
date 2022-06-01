import sqlite3 as sq
import csv

answer = input('Будет произведено перезаполнение даных таблицы ПНИ. Вы уверены? Если да, наберите "Yes"   ')

if answer == 'Yes':
    with sq.connect('/home/olejonos/pni.db') as con:
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS pni (
                sname TEXT,
                name TEXT,
                name_dop TEXT,
                qty REAL,
                unit TEXT,
                price REAL,
                total REAL,
                contract TEXT,
                year INTEGER,
                customer TEXT
            )                
        ''')

        # cur.execute('DELETE FROM pni')

        with open('/home/olejonos/pni.csv', 'r') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                qty = row['qty'].replace(',', '.')
                price = row['price'].replace(',', '.')
                total = row['total'].replace(',', '.')
                cur.execute(
                    'INSERT INTO pni (name, name_dop, qty, unit, price, total, contract, year, customer) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    [row['name'], row['name_dop'], qty, row['unit'], price, total, row['contract'],
                     row['year'], row['customer']])

