'''
Заходит в папку <data_path> текущего проекта, берет все файлы *.csv и конкотинирует их в файл all.csv

Заполняет этими данными таблицу products_in_contracts в БД gz.sqlite3 (file_db)

'''

import os
from lib_gz import *
import sqlite3 as sq

# Заходит в папку <data_path> текущего проекта, берет все файлы *.csv и конкотинирует их в файл all.csv

file_output = data_path + 'all.csv'

with open(file_output,'w') as f:
    for adress, dirs, files in os.walk(data_path):
        for file in files:
            full_path = os.path.join(adress, file)
            if full_path[-4:] == '.csv':
                f.write(open(full_path).read())


# Заполняет данными таблицу products_in_contracts в БД gz.sqlite3 (file_db) из исходного файла file_output

# Открываем файл и для начала выводим справочную информацию по нему
set_product = set()
set_contract = set()
set_contract_year = set()
set_contract_year_customer = set()
set_contract_year_product_customer = set()

with open(file_output, 'r') as file:
    count = 1
    for row in file:
        count += 1
        contract, year, product, customer = row[:-1].split(';')
        set_product.add(product)
        set_contract.add(contract)
        set_contract_year.add(contract + ';' + year)
        set_contract_year_customer.add(contract + ';' + year + ';' + customer)
        set_contract_year_product_customer.add(contract + ';' + year + ';' + product + ';' + customer)

print('Количество продуктов:', len(set_product))
print('Количество контрактов:', len(set_contract))
print('Контракт/год:', len(set_contract_year))
print('Контракт/год/заказчик:', len(set_contract_year_customer))
print('Контракт/год/продукт/заказчик:', len(set_contract_year_product_customer))

answer = input(
    'Будет произведено перезаполнение даных таблицы products_in_contracts. Вы уверены? Если да, наберите "Yes": ')
if answer == 'Yes':

    # Заполняем список кортежей данными из множества
    data = []
    for row in set_contract_year_product_customer:
        contract, year, product, customer = row.split(';')
        data.append((contract, year, product, customer, 1))

    with sq.connect(file_db) as con:
        cur = con.cursor()

        cur.execute('DROP table if exists products_in_contracts')
        con.commit()

        # Создаем таблицу
        cur.execute('''
            CREATE TABLE products_in_contracts (
                contract TEXT,
                year INTEGER,
                find_text TEXT,
                customer TEXT,
                in_work INTEGER
            )
        ''')

        # Заполняем таблицу из списка кортежей
        cur.executemany(
            'INSERT INTO products_in_contracts (contract, year, find_text, customer, in_work) VALUES (?, ?, ?, ?, ?)',
            data)
