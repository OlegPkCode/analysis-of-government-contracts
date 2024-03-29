'''
Период выборки указывается между start_date и end_date
Скрипт парсит данные по указанным наименованиям позиций в файле file_input
Формат файла file_input:
Наименование позиции (запишется в file_output); Далее чепрез символ ';' записывается семантическое ядро данной позиции
Например:
яйц;яйц;яйца;яйцо
Результат записывается в файлы file_output_название_обработанной_позиции

Если test_difference истина, то
Выгружает продукты, указанные в file_input и заполняет таблицу products_in_contracts
РАЗНИЦЕЙ в этих продуктах. Т.е результирующая таблица содержит не содержит общих контрактов,
которые есть в списке file_input
'''

# import requests
# from bs4 import BeautifulSoup
import datetime
import csv
import os
import time
import sqlite3 as sq
from lib_gz import data_path, clean_str, file_db, clean_num, get_soup

start_year = 2017
end_year = 2022
file_input = data_path + 'products.csv'
file_error = data_path + 'error.txt'
file_log = data_path + 'log.txt'
test_difference = 0

# Генерируем список дат
list_date = []
for year in range(start_year, end_year + 1):
    date_start = datetime.datetime(year, 1, 1).strftime('%d.%m.%Y')
    date_end = datetime.datetime(year, 12, 31).strftime('%d.%m.%Y')
    list_date.append(f'{date_start},{date_end}')


def get_rows(name_pos, num_page, start_date, end_date):
    search_string = f'searchString={name_pos}&' if name_pos else ''

    url = f'https://zakupki.gov.ru/epz/contract/search/results.html?{search_string}' + (
        'morphology=on&'
        'fz44=on&'
        'contractStageList_1=on&'
        'contractStageList_2=on&'
        'contractStageList=1%2C2&'
        'selectedContractDataChanges=ANY&'
        'contractCurrencyID=-1&'
        'budgetLevelsIdNameHidden=%7B%7D&'
        'customerPlace=5277347&'
        f'executionDateStart={start_date}&'
        f'executionDateEnd={end_date}&'
        'countryRegIdNameHidden=%7B%7D&'
        'sortBy=UPDATE_DATE&'
        f'pageNumber={str(num_page)}&'
        'sortDirection=false&'
        'recordsPerPage=_500&'
        'showLotsInfoHidden=false'
    )

    rows = get_soup(url).find_all('div', class_='row no-gutters registry-entry__form mr-0')

    return rows


def write_log(message):
    """Записываем данные <message> в лог-файл"""
    datetime_now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    message = f"{datetime_now}; {message}" + '\n'
    print(message)
    with open(file_log, 'a') as file:
        file.write(message)


if __name__ == "__main__":

    # Открываем файл file_input, считываем продукты в список
    list_products = []
    with open(file_input, 'r') as file:
        text = file.read()

    for i in text.split('\n'):
        if len(i) > 0:
            list_products.append(i)

    # Парсим контракты, содержащие данные продукты
    for find_text in list_products:
        products = find_text.split(',')
        for product in products:

            list_contracts = []
            sum_row = 0
            last_sum_row = 0

            for item_list_date in list_date:
                start_date, end_date = item_list_date.split(',')

                num_page = 1

                # Получаем коллекцию BeautifulSoup согласно заданным параметрам
                rows = get_rows(product, num_page, start_date, end_date)

                while len(rows) > 0:
                    for item in rows:
                        # Номер контракта
                        contract_num = item.find('a').text.strip()[2:]
                        # Год исполнения контракта
                        contract_year_complite = item.find_all('div', class_='data-block__value')[1].text.strip()[-4::]
                        # Список позиций контракта
                        contract_list_products = item.find('span', class_='pl-0 col').find('a')
                        # Заказчик
                        contract_customer = clean_str(
                            item.find('div', class_='registry-entry__body-href').text.strip())
                        # Берем общую сумму позиций данного контакта на сайте
                        total_in_site = clean_num(item.find('div', class_='price-block__value').text.strip())

                        # Если данный контракт содержит электронную версию, и контракта нет в списке, то сохраняем его
                        if contract_list_products is not None:
                            contract_exist = 0
                            for i in list_contracts:
                                if contract_num in i:
                                    contract_exist = 1
                            if contract_exist == 0:
                                list_contracts.append(
                                    contract_num + ';' + contract_year_complite + ';' + total_in_site + ';' + find_text + ';' + contract_customer)
                                sum_row += 1

                    # Листаем страницы
                    if last_sum_row == sum_row:
                        break
                    datetime_now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
                    write_log(
                        f"Product: {product}, Page: {num_page}, Total row = {sum_row}, Period: {start_date} - {end_date}, Time proc.: {datetime_now}")
                    num_page = num_page + 1
                    rows = get_rows(product, num_page, start_date, end_date)
                    last_sum_row = sum_row

            # Записываем результат в файл
            if len(list_contracts) > 0:
                file_output = data_path + 'list_products_in_contracts_' + product + '_from_' + str(start_year) + '_to_' + str(end_year) + '_rows_' + str(
                    sum_row) + '.csv'
                with open(file_output, 'a', newline='') as file:
                    writer = csv.writer(file, delimiter='\n')
                    writer.writerow(list_contracts)
            else:
                with open(file_error, 'a', newline='') as file:
                    file.write(f"Нет данных по продукту: {product}\n")

    '''
    Заходит в папку <data_path> текущего проекта, берет все файлы *.csv и конкотинирует их в файл all.csv
    Заполняет этими данными таблицу products_in_contracts в БД gz.sqlite3 (file_db)
    '''

    # Заходит в папку <data_path> текущего проекта, берет все файлы *.csv и конкотинирует их в файл all.csv
    file_output = data_path + 'all.csv'

    set_union = set()
    # set_union_file = set()
    set_intersection = set()

    with open(file_output, 'w') as f:
        for adress, dirs, files in os.walk(data_path):
            for file in files:
                if file == 'products.csv' or file == 'error.txt':
                    continue
                full_path = os.path.join(adress, file)
                if full_path[-4:] == '.csv':
                    f.write(open(full_path).read())

                    if test_difference:
                        a = open(full_path).read()
                        set_file = set(a.split('\n'))
                        set_file.discard('')
                        set_union = set_union | set_file
                        if len(set_intersection) == 0:
                            set_intersection = set_file
                        else:
                            set_intersection = set_intersection & set_file

    set_diff = set_union - set_intersection

    # Заполняет данными таблицу products_in_contracts в БД gz.sqlite3 (file_db) из исходного файла file_output

    # Открываем файл и для начала выводим справочную информацию по нему
    # set_product = set()
    set_contract = set()
    # set_contract_year = set()
    # set_contract_year_customer = set()
    set_contract_year_product_customer = set()

    with open(file_output, 'r') as file:
        count = 1
        for row in file:
            contract, year, sum, product, customer = row[:-1].split(';')
            # set_product.add(product)
            set_contract.add(contract)
            count += 1
            # set_contract_year.add(contract + ';' + year)
            # set_contract_year_customer.add(contract + ';' + year + ';' + customer)
            set_contract_year_product_customer.add(contract + ';' + year + ';' + sum + ';' + product + ';' + customer)

    os.remove(file_output)
    write_log('Количество контрактов: ' + str(len(set_contract)))

    # Заполняем список кортежей данными из множества
    data = []
    if test_difference:
        set_contract_year_product_customer = set_diff

    for row in set_contract_year_product_customer:
        contract, year, sum, product, customer = row.split(';')
        data.append((contract, year, sum, product, customer, 1))

    with sq.connect(file_db) as con:
        cur = con.cursor()

        cur.execute('DROP table if exists products_in_contracts')
        con.commit()

        # Создаем таблицу
        cur.execute('''
            CREATE TABLE products_in_contracts (
                contract TEXT,
                year INTEGER,
                sum INTEGER,
                find_text TEXT,
                customer TEXT,
                in_work INTEGER
            )
        ''')

        # Заполняем таблицу из списка кортежей
        cur.executemany(
            'INSERT INTO products_in_contracts (contract, year, sum, find_text, customer, in_work) VALUES (?, ?, ?, ?, ?, ?)',
            data)
