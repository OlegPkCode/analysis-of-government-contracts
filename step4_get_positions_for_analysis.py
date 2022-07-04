import requests
from bs4 import BeautifulSoup
import time
import sqlite3 as sq
from lib_parse import *

file_output = 'step4_log.csv'


def great_table_positions():
    ''' Создаем таблицу positions, если ее нет в БД'''

    with sq.connect(file_db) as con:
        cur = con.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                name TEXT,
                name_dop TEXT,
                qty REAL,
                unit TEXT,
                price REAL,
                total REAL,
                contract TEXT,
                year INTEGER,
                customer TEXT,
                find_text TEXT
            )
        ''')


def get_list_products_and_contracts():
    '''Получаем список позиций, которые осталось спарсить'''

    positions_need = set()
    positions_have = set()

    with sq.connect(file_db) as con:
        con = sq.connect(file_db)
        cur = con.cursor()

        # ################################################################################################################

        # cur.execute("DELETE FROM positions")
        # con.commit()

        # ################################################################################################################

        # Выбираем позиции, которые нужно спарсить
        for row in cur.execute("SELECT * FROM products_in_contracts"):
            positions_need.add(row)

        # Выбираем позиции, которые уже спарсены и возвращаем разницу
        for row in cur.execute("SELECT contract, year, find_text, customer FROM positions"):
            positions_have.add(row)

    return positions_need - positions_have


def get_list_products_in_contract(contract):
    ''' Берем список всех продуктов, которые могут быть в данном контракте'''

    positions = []
    with sq.connect(file_db) as con:
        cur = con.cursor()
        sql = f"SELECT product FROM products_in_contracts WHERE contract = '{contract}'"
        for item in cur.execute(sql).fetchall():
            positions.append(item[0])

    return positions


# def if_exist_str(str1, str2, ls):
#     '''Возвращает позицию списка, которая содержится в первой или во второй строке'''
#     res = ''
#     for item in ls:
#         if item in str2:
#             res = item
#         if item in str1:
#             res = item
#             break
#
#     return res.strip()


def parse_positions(contract, year, positions, customer):
    URL_ITEMS = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order-list.html?reestrNumber=' + contract + '&page=1&pageSize=200'
    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    }

    # Считываем позиции в контракте
    r_pos = requests.get(URL_ITEMS, headers=HEADERS)
    soup_pos = BeautifulSoup(r_pos.text, 'html.parser')
    position_list = soup_pos.find_all('tr', class_='tableBlock__row')
    data = []

    for product in positions:

        # Заполняем список data позициями контракта
        for item in position_list:
            name = item.find('div', class_='padBtm5 inline js-expand-all-list--not-count')
            qtyUnit = item.find('div', class_='align-items-center w-space-nowrap')
            priceAndSum = item.find_all('td', class_='tableBlock__col tableBlock__col_right')
            if (name is not None) and (qtyUnit is not None) and (priceAndSum is not None):
                name = convert_str(name.text)
                name_dop = convert_str(item.find_all('td', class_='tableBlock__col')[2].text)
                if (product.lower() in name.lower()) or (product.lower() in name_dop.lower()):
                    # Преобразование столбцов количества и единиц измерений
                    qtyUnit = qtyUnit.text.strip()
                    qty, unit = qtyUnit.split('\n')
                    qty = convert_num(qty)
                    unit = convert_str(unit)
                    # Преобразование столбцов цены и суммы
                    price = convert_num(priceAndSum[0].text.strip())
                    sum = priceAndSum[1].text.strip()
                    sum = convert_num(sum[:sum.find('\n')])

                    data.append((name, name_dop, qty, unit, price, sum, contract, year, customer, product))

    for input_pos in positions:
        find_pos = False
        for data_pos in data:
            if input_pos == data_pos[9]:
                find_pos = True
        if find_pos == False:
            print('!!! Не данных по продукту ' + input_pos + ' в контракте ' + contract)
            write_log('!!! Не данных по продукту ' + input_pos + ' в контракте ' + contract)

    con = None

    try:
        con = sq.connect(file_db)
        cur = con.cursor()
        cur.executemany(
            "INSERT INTO positions (name, name_dop, qty, unit, price, total, contract, year, customer, product) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            data)
        con.commit()

    except sq.DatabaseError as err:
        if con: con.rollback()
        print("Error: ", err)

    finally:
        if con: con.close()


def write_log(message):
    '''Записываем данные <message> в лог-файл'''

    with open(file_output, 'a') as file:
        file.write('\n')
        file.write(message)


if __name__ == "__main__":
    great_table_positions()

    # Получаем список продуктов и привязанных к ним контрактов, которые нужно спарсить
    list_parsing = list(get_list_products_and_contracts())
    print('1. Всего позиций для парсинга:', len(list_parsing))
    write_log('1. Всего позиций для парсинга: ' + str(len(list_parsing)))

    while len(list_parsing) > 0:
        # Сортируем по наименованию продукта
        list_parsing.sort(key=lambda i: i[2])
        contract, year, position, customer = list_parsing[0]
        # contract, year, position, customer = '2781702775719000005;2020;абрикос;ГОСУДАРСТВЕННОЕ БЮДЖЕТНОЕ ДОШКОЛЬНОЕ ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ ДЕТСКИЙ САД № 57 КОМБИНИРОВАННОГО ВИДА КОЛПИНСКОГО РАЙОНА САНКТ-ПЕТЕРБУРГА'.split(';')
        print('2. Берем в работу: ', contract, year, position, customer)
        write_log('2. Берем в работу: ' + contract + ' / ' + str(year) + ' / ' + position + ' / ' + customer)
        # Берем список всех остальных продуктов, которые могут быть в данном контракте
        positions = get_list_products_in_contract(contract)
        print('3. У данного контракта берем в работу позиции: ', positions)
        write_log('3. У данного контракта берем в работу позиции: ' + str(positions))
        # Парсим заданную строку
        parse_positions(contract, year, positions, customer)
        time.sleep(3)
        list_parsing = list(get_list_products_and_contracts())
        print('1. Всего позиций для парсинга:', len(list_parsing))
        write_log('1. Всего позиций для парсинга: ' + str(len(list_parsing)))
