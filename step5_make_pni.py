'''Создает таблицу pni в БД на основе файла pni.ods'''
import sqlite3 as sq
from lib_gz import *
import csv

file_output = data_path + 'pni.csv'

# Конвертируем ods файл в data_path в формат csv
convert_ods_to_csv(file_output)

# # Перезаполняем таблицу pni
# with sq.connect(file_db) as con:
#     cur = con.cursor()
#
#     cur.execute('DROP table if exists pni')
#     con.commit()
#
#     cur.execute('''
#         CREATE TABLE IF NOT EXISTS pni (
#             find_text TEXT,
#             short_name TEXT,
#             name TEXT,
#             name_dop TEXT,
#             qty REAL,
#             unit TEXT,
#             price REAL,
#             total REAL,
#             contract TEXT,
#             year INTEGER,
#             customer TEXT
#         )
#     ''')
#
#     # Заполняем список data данными кортежей из сконвертированного файла pni.ods
#     data = []
#     with open(file_output, 'r') as file:
#         reader = csv.DictReader(file, delimiter=';')
#         for i in reader:
#             data.append((i['find_text'], i['short_name'], i['name'], i['name_dop'], i['qty'], i['unit'], i['price'],
#                          i['total'], i['contract'], i['year'], i['customer']))
#
#     # Заполняем таблицу pni из списка data
#     cur.executemany(
#         'INSERT INTO pni (find_text, short_name, name, name_dop, qty, unit, price, total, contract, year, customer) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
#         data)
