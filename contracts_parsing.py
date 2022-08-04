'''
Парсит данные с сайта по контрактам, записанным в файле file_input
Формат файла file_input:
Номер контракта;Год;Заказчик
Результат записывается в файл file_output
'''

import requests
from bs4 import BeautifulSoup
import time
import csv
from lib_gz import *

file_input = data_path + 'contracts.csv'
file_output = data_path + 'contract_items.csv'


def parsing_contract(contract, customer):
    URL_HEADER = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order.html?reestrNumber=' + contract + '&#contractSubjects'
    URL_ITEMS = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order-list.html?reestrNumber=' + contract + '&page=1&pageSize=200'
    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    }

    # Считываем заголовок контракта и позиции в контракте
    r_head = requests.get(URL_HEADER, headers=HEADERS)
    soup_head = BeautifulSoup(r_head.text, 'html.parser')
    time.sleep(7)
    r_pos = requests.get(URL_ITEMS, headers=HEADERS)
    soup_pos = BeautifulSoup(r_pos.text, 'html.parser')

    position_list = soup_pos.find_all('tr', class_='tableBlock__row')

    data = []
    pos = 0
    total = 0
    total_in_site = 0

    # Заполняем список data позициями контракта
    for item in position_list:
        name = item.find('div', class_='padBtm5 inline js-expand-all-list--not-count')
        qtyUnit = item.find('div', class_='align-items-center w-space-nowrap')
        priceAndSum = item.find_all('td', class_='tableBlock__col tableBlock__col_right')
        if (name is not None) and (qtyUnit is not None) and (priceAndSum is not None):
            name = convert_str(name.text)
            name_dop = convert_str(item.find_all('td', class_='tableBlock__col')[2].text)

            # Преобразование столбцов количества и единиц измерений
            qtyUnit = qtyUnit.text.strip()
            try:
                qty, unit = qtyUnit.split('\n')
                qty = convert_num(qty)
                unit = convert_str(unit)
            except:
                qty = 0
                unit = convert_str(qtyUnit)

            # Преобразование столбцов цены и суммы
            price = convert_num(priceAndSum[0].text.strip())
            sum = priceAndSum[1].text.strip()
            sum = convert_num(sum[:sum.find('\n')])

            pos += 1
            total += float(convert_num_dot(sum))

            data.append(
                {'name': name, 'name_dop': name_dop, 'qtyUnit': qtyUnit, 'qty': qty, 'unit': unit, 'price': price,
                 'sum': sum})

    # Записываем год исполнения контракта
    year_finish = soup_head.find('div', class_='date mt-auto').find_all('div', class_='cardMainInfo__section')[
                      1].text.strip()[-4:]

    # Берем общую сумму позиций данного контакта на сайте
    total_in_site = convert_num(soup_pos.find('td', class_='tableBlock__col tableBlock__col_right cost').text.strip())
    total_in_site = float(convert_num_dot(total_in_site))

    # Если общая сумма симпортированых позиций равна сумме контракта на сайте - пишем результат в файл
    if round(total, 2) == total_in_site:
        with open(file_output, 'a', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for i in data:
                writer.writerow(
                    (
                        i['name'],
                        i['name_dop'],
                        i['qty'],
                        i['unit'],
                        i['price'],
                        i['sum'],
                        contract,
                        year_finish,
                        customer
                    )
                )
        print('Контракт: ' + contract + ' Позиций - ', pos)
        print('Сумма импортированных позиций - ', total)
        print('Сумма позиций по данным с сайта - ', total_in_site, end="\n" * 2)
    else:
        print('!!!!! СУММА ИМПОРТИРОВАННЫХ ПОЗИЦИЙ РАСХОДИТСЯ С ОБЩЕЙ СУММОЙ КОНТРАКТОВ НА САЙТЕ!!!!!')
        print('Позиций - ', pos)
        print('Сумма импортированных позиций - ', total)
        print('Сумма позиций на сайте - ', total_in_site)


if __name__ == "__main__":

    # Открываем файл file_input, считываем контракты в список
    list_contract = []
    with open(file_input, 'r') as file:
        for i in file:
            list_contract.append(i[:-1])

    # Парсим контракты из списка
    for item in list_contract:
        contract, year, customer = item.split(';')
        print(contract, year)
        parsing_contract(contract, customer)
        time.sleep(7)
