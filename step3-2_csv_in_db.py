from lib_parse import *
import sqlite3 as sq

'''Заполняет данными таблицу products_in_contracts в БД gz.sqlite3 (file_db) из исходного файла file_input'''

file_input = data_path + 'all.csv'

# Открываем файл и для начала выводим справочную информацию по нему

set_product = set()
set_contract = set()
set_contract_year = set()
set_contract_year_customer = set()
set_contract_year_product_customer = set()

with open(file_input, 'r') as file:
    count = 1
    for row in file:
        # print('Строка', count)
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
        data.append((contract, year, product, customer))

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
                customer TEXT
            )
        ''')

        # Заполняем таблицу из списка кортежей
        cur.executemany(
            'INSERT INTO products_in_contracts (contract, year, find_text, customer) VALUES (?, ?, ?, ?)',
            data)
