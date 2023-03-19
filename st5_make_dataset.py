'''Выгружает спарсенные данные из таблицы positions в csv файл дальнейшей очистки и анализа'''

import sqlite3 as sq
from lib_gz import file_db, data_path
import csv

file_output = data_path + 'dataset_positions.csv'

with sq.connect(file_db) as con:
    cur = con.cursor()
    sql = 'SELECT DISTINCT name, name_dop, qty, unit, price, total, contract, year, customer, find_text FROM positions'

    with open(file_output, 'w') as file:
        writer = csv.writer(file, delimiter=';')
        # Записываем наименования столбцов
        file.write('name;name_dop;qty;unit;price;total;contract;year;customer;find_text' + '\n')
        for i in cur.execute(sql).fetchall():
            writer.writerow(i)
