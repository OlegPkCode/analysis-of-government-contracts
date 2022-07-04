import requests
from bs4 import BeautifulSoup
import csv
import time
from lib_parse import *

start_date = '01.01.2017'
end_date = '31.12.2021'
file_input = data_path + 'products.csv'


def get_rows(name_pos, num_page):
    searchString = lambda: '' if len(name_pos) == 0 else 'searchString=' + name_pos + '&'

    url1 = 'https://zakupki.gov.ru/epz/contract/search/results.html?' + searchString()
    url2 = ''' 
    morphology=on&
    fz44=on&
    contractStageList_1=on&
    contractStageList_2=on&
    contractStageList=1%2C2&
    selectedContractDataChanges=ANY&
    contractCurrencyID=-1&
    budgetLevelsIdNameHidden=%7B%7D&
    customerPlace=5277347&
    executionDateStart=''' + start_date + '''&
    executionDateEnd=''' + end_date + '''&
    countryRegIdNameHidden=%7B%7D&
    sortBy=UPDATE_DATE&
    pageNumber=''' + str(num_page) + '''&
    sortDirection=false&
    recordsPerPage=_500&
    showLotsInfoHidden=false'''

    url2 = url2.replace('\n', '')
    url = url1 + ''.join(url2.split())

    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    }

    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.find_all('div', class_='row no-gutters registry-entry__form mr-0')

    return rows


if __name__ == "__main__":

    # Открываем файл file_input, считываем продукты в список
    list_products = []
    with open(file_input, 'r') as file:
        for i in file:
            list_products.append(i[:-1])

    # Парсим контракты, содержащие данные продукты
    for item_list_products in list_products:

        products = item_list_products.split(';')
        product_name = products.pop(0)

        for product in products:

            num_page = 1
            sum_row = 0
            list_contracts = []

            # Получаем коллекцию BeautifulSoup согласно заданным параметрам
            rows = get_rows(product, num_page)

            while len(rows) > 0:
                print('Page', num_page, product)
                for item in rows:
                    # Номер контракта
                    contract_num = item.find('a').text.strip()[2:]
                    # Год исполнения контракта
                    contract_year_complite = item.find_all('div', class_='data-block__value')[1].text.strip()[-4::]
                    # Список позиций контракта
                    contract_list_products = item.find('span', class_='pl-0 col').find('a')
                    # Заказчик
                    contract_customer = convert_str(item.find('div', class_='registry-entry__body-href').text.strip())

                    # Если данный контракт содержит электронную версию, и контракта нет в списке, то сохраняем его
                    if contract_list_products != None:
                        contract_exist = 0
                        for i in list_contracts:
                            if contract_num in i:
                                contract_exist = 1
                        if contract_exist == 0:
                            list_contracts.append(
                                contract_num + ';' + contract_year_complite + ';' + product_name + ';' + contract_customer)
                            sum_row += 1

                # Листаем страницы
                print('Total row =', sum_row)
                num_page = num_page + 1
                rows = get_rows(product, num_page)
                time.sleep(3)

            # Записываем результат в файл
            file_output = data_path + 'list_products_in_contracts_' + product + '_from_' + start_date + '_to_' + end_date + '_rows_' + str(
                sum_row) + '.csv'
            with open(file_output, 'a', newline='') as file:
                writer = csv.writer(file, delimiter='\n')
                writer.writerow(list_contracts)
