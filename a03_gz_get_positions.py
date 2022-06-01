import requests
from bs4 import BeautifulSoup
import csv
import time
import os.path
import a01_gz_parse_contracts as lib


def parsing_step3(contract, find_text):
    URL_HEADER = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order.html?reestrNumber=' + contract + '&#contractSubjects'
    URL_POSITIONS = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order-list.html?reestrNumber=' + contract + '&page=1&pageSize=200'
    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    }

    r_head = requests.get(URL_HEADER, headers=HEADERS)
    soup_head = BeautifulSoup(r_head.text, 'html.parser')
    time.sleep(3)
    r_pos = requests.get(URL_POSITIONS, headers=HEADERS)
    soup_pos = BeautifulSoup(r_pos.text, 'html.parser')

    data = []

    line = soup_pos.find_all('tr', class_='tableBlock__row')
    for item in line:
        name = item.find('div', class_='padBtm5 inline js-expand-all-list--not-count')
        qtyIzm = item.find('div', class_='align-items-center w-space-nowrap')
        priceInPage = item.find_all('td', class_='tableBlock__col tableBlock__col_right')
        if (name is not None) and (qtyIzm is not None) and (priceInPage is not None):
            name = lib.convert_namePos(name.text)
            name_dop = lib.convert_namePos(item.find_all('td', class_='tableBlock__col')[2].text)

            if (find_text.lower() in name.lower()) or (find_text.lower() in name_dop.lower()):
                # Преобразование столбцов количества и единиц измерений
                qtyIzm = qtyIzm.text.strip()
                razd = qtyIzm.find('\n')
                qty = lib.convert_num(qtyIzm[:razd])
                izm = lib.convert_namePos(qtyIzm[razd + 1:])
                # Преобразование столбцов цены и суммы
                price = lib.convert_num(priceInPage[0].text.strip())
                sum = priceInPage[1].text.strip()
                sum = lib.convert_num(sum[:sum.find('\n')])

                data.append(
                    {'name': name, 'name_dop': name_dop, 'qtyIzm': qtyIzm, 'qty': qty, 'izm': izm, 'price': price,
                     'sum': sum})

    if len(data) > 0:
        org_full_name = \
            soup_head.find('div', class_='sectionMainInfo__body').find_all('span', class_='cardMainInfo__content')[
                0].text.strip()
        year_finish = soup_head.find('div', class_='date mt-auto').find_all('div', class_='cardMainInfo__section')[
                          1].text.strip()[-4:]

        with open('list_pos.csv', 'a', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for i in data:
                writer.writerow(
                    (
                        i['name'],
                        i['name_dop'],
                        i['qty'],
                        i['izm'],
                        i['price'],
                        i['sum'],
                        contract,
                        year_finish,
                        lib.convert_namePos(org_full_name),
                        find_text
                    )
                )


def get_contract_positions():
    list_contract_positions = []
    with open('list_pos.csv', 'r') as csvfile:
        for i in csvfile:
            value1 = i.split(';')[6]
            value2 = i.split(';')[9][:-1]
            list_contract_positions.append(value1 + ';' + value2)

    return list_contract_positions


list_contract = []
with open('list_contract.csv', 'r') as csvfile:
    for i in csvfile:
        list_contract.append(i[:-1])

if os.path.exists('list_pos.csv'):
    list_contract_positions = get_contract_positions()
    for i in list_contract_positions:
        if i in list_contract:
            list_contract.remove(i)

for i in list_contract:
    print(f'{list_contract.index(i) + 1 :04} из {len(list_contract)}', i)
    str = i.split(';')
    parsing_step3(str[0], str[1])
    time.sleep(3)
