import requests
from bs4 import BeautifulSoup
import time
import sqlite3 as sq
import datetime
import csv
from lib_gz import file_db, convert_str, convert_num, convert_num_dot, data_path

file_output = datetime.datetime.now().strftime("%Y-%m-%d_log.csv")
file_output_err = datetime.datetime.now().strftime("%Y-%m-%d_log_error.csv")


def great_table_positions():
    """ Создаем таблицу positions, если ее нет в БД"""

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
        con.commit()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS positions_err (
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
        con.commit()


def get_list_contracts():
    """Получаем список позиций, которые осталось спарсить"""

    positions_need = set()
    positions_have = set()

    with sq.connect(file_db) as con:
        cur = con.cursor()

        # Выбираем позиции, которые нужно спарсить
        for row in cur.execute(
                # "SELECT contract, year, find_text, customer FROM products_in_contracts WHERE in_work = 1"):
                "SELECT contract, year, customer FROM products_in_contracts WHERE in_work = 1"):
            # for row in cur.execute("SELECT contract, year, customer FROM products_in_contracts WHERE in_work = 1"):
            positions_need.add(row)

        # Выбираем позиции, которые уже спарсены и возвращаем разницу
        # for row in cur.execute("SELECT contract, year, find_text, customer FROM positions"):
        for row in cur.execute("SELECT contract, year, customer FROM positions"):
            # for row in cur.execute("SELECT contract, year, customer FROM positions"):
            positions_have.add(row)

    return positions_need - positions_have


def get_find_text_in_contract(contract):
    """ Берем список всех продуктов, которые могут быть в данном контракте"""

    positions = []
    with sq.connect(file_db) as con:
        cur = con.cursor()
        # sql = f"SELECT find_text FROM products_in_contracts WHERE contract = '{contract}' AND in_work = 1"
        sql = f"SELECT find_text FROM products_in_contracts WHERE contract = '{contract}'"
        for item in cur.execute(sql).fetchall():
            positions.append(item[0])

    return positions


def get_sum_contract(contract):
    """ Возвращаем сумму контракта"""

    with sq.connect(file_db) as con:
        cur = con.cursor()
        sql = f"SELECT sum FROM products_in_contracts WHERE contract = '{contract}'"
        sum_contract = cur.execute(sql).fetchall()[0][0]

    return float(convert_num_dot(sum_contract))


def parse_positions(contract, year, customer):
    URL_ITEMS = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order-list.html?reestrNumber=' + \
                contract + '&page=1&pageSize=200'
    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    }

    while True:
        try:
            # Считываем позиции в контракте
            r_pos = requests.get(URL_ITEMS, headers=HEADERS, timeout=15)
            soup_pos = BeautifulSoup(r_pos.text, 'html.parser')
            position_list = soup_pos.find('tbody', class_='tableBlock__body').find_all('tr', class_='tableBlock__row')
            time.sleep(5)
            break
        except Exception as exp:
            # если возникла какая-либо ошибка
            write_log('', contract, f"Error: {exp}")
            time.sleep(60)

    # Берем список всех остальных продуктов, которые могут быть в данном контракте
    data = []
    find_text = get_find_text_in_contract(contract)
    total_sum_contract = get_sum_contract(contract)
    sum_contract = 0
    flag_sum_contract = True  # Проверить на разницу суммы контракта и сумммы позиций контракта
    flag_contract_err = False  # Признак ошибки при обработке накладной

    # Заполняем список data позициями контракта
    for item in position_list:
        name = item.find('div', class_='padBtm5 inline js-expand-all-list--not-count')
        qtyUnit = item.find('div', class_='align-items-center')
        priceAndSum = item.find_all('td', class_='tableBlock__col tableBlock__col_right')
        if (name is not None) and (qtyUnit is not None) and (priceAndSum is not None):
            name = convert_str(name.text)
            name_dop = convert_str(item.find_all(
                'td', class_='tableBlock__col')[2].text)

            # Преобразование столбцов цены и суммы
            price = convert_num(priceAndSum[0].text.strip())
            sum = priceAndSum[1].text.strip()
            sum = convert_num(sum[:sum.find('\n')])
            if sum != '':
                sum_contract += float(convert_num_dot(sum))
            else:
                flag_sum_contract = False

            parse = False
            for item_find_text in find_text:
                for product in item_find_text.split(','):
                    if (product.lower() in name.lower()) or (product.lower() in name_dop.lower()):
                        parse = True
                        add_product = item_find_text

            if parse:
                # Преобразование столбцов количества и единиц измерений
                qtyUnit = qtyUnit.text.strip()
                try:
                    qty, unit = qtyUnit.split('\n')
                    qty = convert_num(qty)
                    if qty.find(',') == -1:
                        qty = qty + ',00'
                    unit = convert_str(unit)
                except:
                    qty = 0
                    unit = convert_str(qtyUnit)

                if sum != '' and float(convert_num_dot(sum)) >= 10000:
                    data.append((name, name_dop, qty, unit, price, sum, contract, year, customer, add_product))

    if flag_sum_contract:
        if total_sum_contract != round(sum_contract, 2):
            write_log('', contract,
                      f'Не сходится сумма контракта с суммой позиций!!! {total_sum_contract} / {round(sum_contract, 2)}')

    if len(data) == 0:
        flag_contract_err = True

        # Заполняем список data позициями контракта
        for item in position_list:
            name = item.find('div', class_='padBtm5 inline js-expand-all-list--not-count')
            qtyUnit = item.find('div', class_='align-items-center')
            priceAndSum = item.find_all('td', class_='tableBlock__col tableBlock__col_right')
            if (name is not None) and (qtyUnit is not None) and (priceAndSum is not None):
                name = convert_str(name.text)
                name_dop = convert_str(item.find_all(
                    'td', class_='tableBlock__col')[2].text)

                # Преобразование столбцов цены и суммы
                price = convert_num(priceAndSum[0].text.strip())
                sum = priceAndSum[1].text.strip()
                sum = convert_num(sum[:sum.find('\n')])

                parse = False
                for item_find_text in find_text:
                    for product in item_find_text.split(','):
                        if (product.lower() in name.lower()) or (product.lower() in name_dop.lower()):
                            parse = True
                            add_product = item_find_text

                if parse:
                    # Преобразование столбцов количества и единиц измерений
                    qtyUnit = qtyUnit.text.strip()
                    try:
                        qty, unit = qtyUnit.split('\n')
                        qty = convert_num(qty)
                        if qty.find(',') == -1:
                            qty = qty + ',00'
                        unit = convert_str(unit)
                    except:
                        qty = 0
                        unit = convert_str(qtyUnit)

                    data.append((name, name_dop, qty, unit, price, sum, contract, year, customer, add_product))

    con = None
    try:
        con = sq.connect(file_db)
        cur = con.cursor()

        if not flag_contract_err:
            sql = "INSERT INTO positions (name, name_dop, qty, unit, price, total, contract, year, customer, find_text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        else:
            sql = "INSERT INTO positions_err (name, name_dop, qty, unit, price, total, contract, year, customer, find_text) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

        cur.executemany(sql, data)
        con.commit()

        if flag_contract_err:
            sql = f"UPDATE products_in_contracts SET in_work = 0 WHERE contract = '{contract}'"
            cur.execute(sql)
            con.commit()

    except sq.DatabaseError as err:
        if con:
            con.rollback()
        print("Error: ", err)

    finally:
        if con:
            con.close()


def write_log(count_contracts, contract, err=''):
    """Записываем данные <message> в лог-файл"""
    datetime_now = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    message = f"{datetime_now};Осталось контрактов - {count_contracts};Обработка контракта - {contract};{err}" + '\n'
    print(message)
    with open(file_output, 'a') as file:
        file.write(message)


def set_contract_not_in_work_delete(contract):
    con = None

    try:
        con = sq.connect(file_db)
        cur = con.cursor()
        cur.execute(
            f"UPDATE products_in_contracts SET in_work = 0 WHERE contract = '{contract}'")
        con.commit()

    except sq.DatabaseError as err:
        if con:
            con.rollback()
        print("Error: ", err)

    finally:
        if con:
            con.close()


def get_processing_result():
    try:
        conn = sq.connect(file_db)
        cursor = conn.cursor()

        cursor.execute("SELECT count(DISTINCT contract) as sum_1 FROM products_in_contracts WHERE in_work = 1")
        result = cursor.fetchone()
        print('Обработано накладных: ', result[0])

        cursor.execute("SELECT count(DISTINCT contract) as sum_1 FROM products_in_contracts WHERE in_work = 0")
        result = cursor.fetchone()
        print('Не обработано накладных: ', result[0])

    except sq.Error as e:
        print("Ошибка:", e)

    finally:
        cursor.close()
        conn.close()

    # -----------------------------------------------------
    # con = None
    #
    # try:
    #     con = sq.connect(file_db)
    #     cur = con.cursor()
    #     cur.execute("SELECT count(DISTINCT contract) as sum_1 FROM products_in_contracts WHERE in_work = 1")
    #
    #
    #
    #
    #
    #
    # except sq.DatabaseError as err:
    #     if con:
    #         con.rollback()
    #     print("Error: ", err)
    #
    # finally:
    #     if con:
    #         con.close()


if __name__ == "__main__":
    great_table_positions()

    # Получаем список продуктов и привязанных к ним контрактов, которые нужно спарсить
    list_parsing = list(get_list_contracts())

    while len(list_parsing) > 0:
        # Сортируем по контрактам)
        list_parsing.sort(key=lambda x: x[0])
        contract, year, customer = list_parsing[0]
        # Парсим заданную строку
        count_contracts = len(list_parsing)
        write_log(count_contracts, contract)
        parse_positions(contract, year, customer)
        list_parsing = list(get_list_contracts())
        # new_count_contracts = len(list_parsing)
        # Если по какой-либо причине контракт не спарсился - пишем в лог и пропускаем его. Разбираемся с ними отельно.
        # if count_contracts == new_count_contracts:
        #     # write_log(count_contracts, contract, 'Контракт не обработан!')
        #     set_contract_not_in_work(contract)
        #     list_parsing = list(get_list_contracts())

    # Выгружает спарсенные данные из таблицы positions в csv файл дальнейшей очистки и анализа
    with sq.connect(file_db) as con:
        cur = con.cursor()

        # Получаем название файла
        sql = 'SELECT DISTINCT find_text FROM positions'
        file_output = data_path + cur.execute(sql).fetchall()[0][0] + '.csv'

        # Получаем результаты парсинга
        sql = "SELECT DISTINCT '', name, name_dop, qty, unit, price, total, contract, year, customer, find_text FROM positions"

        with open(file_output, 'w') as file:
            writer = csv.writer(file, delimiter=';')
            # Записываем наименования столбцов
            file.write('sname;name;name_dop;qty;unit;price;total;contract;year;customer;find_text' + '\n')
            for i in cur.execute(sql).fetchall():
                writer.writerow(i)

        # Получаем название файла
        sql = 'SELECT DISTINCT find_text FROM positions'
        file_output = data_path + cur.execute(sql).fetchall()[0][0] + '_err.csv'

        # Получаем результаты парсинга
        sql = "SELECT DISTINCT '', name, name_dop, qty, unit, price, total, contract, year, customer, find_text FROM positions_err"

        with open(file_output, 'w') as file:
            writer = csv.writer(file, delimiter=';')
            # Записываем наименования столбцов
            file.write('sname;name;name_dop;qty;unit;price;total;contract;year;customer;find_text' + '\n')
            for i in cur.execute(sql).fetchall():
                writer.writerow(i)

    get_processing_result()
