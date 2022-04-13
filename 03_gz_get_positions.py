import requests
from bs4 import BeautifulSoup
import csv
import time


def convert_namePos(x):
    # Удаляем впередистоящие знаки, отличные от символьных и кавычки и лишние пробелы в начале и в конце
    x = x.strip()
    while x[0].isdecimal():
        x = x[1:]
    x = x.replace('"', '')
    x = x.replace("'", '')
    # Удаляем дублирующие пробелы и переносы строки
    x = ' '.join(x.split())

    return x.strip()


def convert_num(x):
    # Удаляем внутренние непереносимые пробелы
    # x = x.replace(',', '.')
    x = x.replace('\xa0', '')
    return x


def parsing(contract, find_text):
    URL_HEADER = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order.html?reestrNumber=' + str(
        contract) + '&#contractSubjects'
    URL_POSITIONS = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order-list.html?reestrNumber=' + str(
        contract) + '&page=1&pageSize=200'
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
            name = convert_namePos(name.text)
            name_dop = convert_namePos(item.find_all('td', class_='tableBlock__col')[2].text)

            if (find_text.lower() in name.lower()) or (find_text.lower() in name_dop.lower()):
                # Преобразование столбцов количества и единиц измерений
                qtyIzm = qtyIzm.text.strip()
                razd = qtyIzm.find('\n')
                qty = convert_num(qtyIzm[:razd])
                izm = qtyIzm[razd + 1:].strip().replace(';', '').replace('"', '')
                # Преобразование столбцов цены и суммы
                price = convert_num(priceInPage[0].text.strip())
                sum = priceInPage[1].text.strip()
                sum = convert_num(sum[:sum.find('\n')])

                data.append({'name': name, 'name_dop': name_dop, 'qtyIzm': qtyIzm, 'qty': qty, 'izm': izm, 'price': price,
                             'sum': sum})

    if len(data) > 0:
        org_full_name = soup_head.find('div', class_='sectionMainInfo__body').find_all('span', class_='cardMainInfo__content')[0].text.strip()
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
                        convert_namePos(org_full_name)
                    )
                )


list_contract = []
with open('list_contract.csv', 'r') as csvfile:
    for i in csvfile:
        list_contract.append(i[:-1])

find_text = 'творог'
for i in list_contract:
    print(f'{list_contract.index(i) + 1:04} из {len(list_contract)}', i)
    parsing(i, find_text)
    time.sleep(3)
