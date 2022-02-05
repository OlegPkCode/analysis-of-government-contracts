import requests
from bs4 import BeautifulSoup
import csv

KONTRAKT = '2782001254217000094'  # Номер контракта
ORG = '812-4'  # Идентификатор организации
URL_HEADER = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order.html?reestrNumber=' + KONTRAKT + '&#contractSubjects'
URL_POSITIONS = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order-list.html?reestrNumber=' + KONTRAKT + '&page=1&pageSize=200'
# https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order.html?reestrNumber=2782506561118000012&#contractSubjects
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
}

r_head = requests.get(URL_HEADER, headers=HEADERS)
soup_head = BeautifulSoup(r_head.text, 'html.parser')
r_pos = requests.get(URL_POSITIONS, headers=HEADERS)
soup_pos = BeautifulSoup(r_pos.text, 'html.parser')

line = soup_pos.find_all('tr', class_='tableBlock__row')

data = []
pos = 0
total = 0
wf = True

for item in line:
    name = item.find('div', class_='padBtm5 inline js-expand-all-list--not-count')
    qtyIzm = item.find('div', class_='align-items-center w-space-nowrap')
    price = item.find_all('td', class_='tableBlock__col tableBlock__col_right')
    if (name is not None) and (qtyIzm is not None) and (price is not None):
        name = name.text.strip()
        # Преобразование столбцов количества и единиц измерений
        qtyIzm = qtyIzm.text.strip()
        razd = qtyIzm.find('\n')
        qty = qtyIzm[:razd]
        qty = ''.join(qty.split())
        izm = qtyIzm[razd + 1:].strip()
        # Преобразование столбцов цены и суммы
        price, sum = price[0].text.strip(), price[1].text.strip()
        razd = sum.find('\n')
        sum = sum[:razd]
        sum = ''.join(sum.split())

        pos += 1
        total += float(sum.replace(',', '.'))

        data.append({'name': name, 'qtyIzm': qtyIzm, 'qty': qty, 'izm': izm, 'price': price, 'sum': sum})

year_finish = soup_head.find('div', class_='date mt-auto').find_all('div', class_='cardMainInfo__section')[
    1].text.strip()
razd = year_finish.find('\n')
year_finish = year_finish[razd + 1:]
year_finish = ''.join(year_finish.split())
year_finish = ''.join(year_finish.split())
year_finish = year_finish[6:]

line_footer = soup_pos.find('tfoot', class_='tableBlock__foot').find_all('tr', class_='tableBlock__row')
for items in line_footer:
    total_site = items.find('td', class_='tableBlock__col tableBlock__col_right cost').text.strip()

total_site = ''.join(total_site.split())
total_site = float(total_site.replace(',', '.'))
total = round(total, 2)

if total == total_site:
    with open(KONTRAKT + '.csv', 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        for i in data:
            writer.writerow(
                (
                    i['name'],
                    i['qty'],
                    i['izm'],
                    i['price'],
                    i['sum'],
                    KONTRAKT,
                    ORG,
                    year_finish
                )
            )
    print('Контракт: ' + KONTRAKT + ' Позиций - ', pos)
    print('Сумма импортированных позиций - ', total)
    print('Сумма позиций на сайте - ', total_site)
else:
    print('!!!!! СУММА ИМПОРТИРОВАННЫХ ПОЗИЦИЙ РАСХОДИТСЯ С ОБЩЕЙ СУММОЙ КОНТРАКТОВ НА САЙТЕ!!!!!')
    print()
    print()
    print()
    print('Позиций - ', pos)
    print('Сумма импортированных позиций - ', total)
    print('Сумма позиций на сайте - ', total_site)
