'''Выгружает спарсенные данные из таблицы positions в csv файл дальнейшей очистки и анализа'''

import sqlite3 as sq
from lib_gz import file_db, data_path
import csv


# with sq.connect(file_db) as con:
with sq.connect('aa.sqlite3') as con:
    cur = con.cursor()

    # Получаем название файла
    sql = 'SELECT DISTINCT find_text FROM positions'
    file_output = data_path + cur.execute(sql).fetchall()[0][0] + '.csv'

    # Получаем результаты парсинга
    sql = 'SELECT DISTINCT name, name_dop, qty, unit, price, total, contract, year, customer, find_text FROM positions'

    with open(file_output, 'w') as file:
        writer = csv.writer(file, delimiter=';')
        # Записываем наименования столбцов
        file.write('name;name_dop;qty;unit;price;total;contract;year;customer;find_text' + '\n')
        for i in cur.execute(sql).fetchall():
            writer.writerow(i)
