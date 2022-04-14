import requests
from bs4 import BeautifulSoup
import csv
import time

name_pos = 'треск'
num_place = 1

def get_rows(name_pos, num_page):

    if num_place == 1:  # г. Санкт-Петербург
        customerPlace = '5277347'
    elif num_place == 2:  # Ленинградская область
        customerPlace = '5277342'
    else:  # г. Санкт-Петербург и Ленинградская область
        customerPlace = '5277347%2C5277342'

    url = '''https://zakupki.gov.ru/epz/contract/search/results.html?searchString=''' + name_pos + ''''&
    morphology=on&
    fz44=on&
    contractStageList_1=on&
    contractStageList=1&
    selectedContractDataChanges=ANY&
    contractCurrencyID=-1&
    budgetLevelsIdNameHidden=%7B%7D&    
    customerPlace=''' + customerPlace + '''&
    customerPlaceCodes=%2C&
    executionDateStart=01.01.2017&
    executionDateEnd=31.12.2021&
    countryRegIdNameHidden=%7B%7D&
    sortBy=UPDATE_DATE&
    pageNumber=''' + str(num_page) + '''&
    sortDirection=false&
    recordsPerPage=_500&
    showLotsInfoHidden=false'''
    url = url.replace('\n', '')
    url = ''.join(url.split())

    HEADERS = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    }

    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'html.parser')
    rows = soup.find('div', class_='search-registry-entrys-block')
    rows = rows.find_all('div', class_='registry-entry__header-mid__number')

    return rows


num_page = 1
list_contract = []

rows = get_rows(name_pos, num_page)

while len(rows) > 0:
    print('Total row = ', len(rows))
    if num_page == 1:
        list_contract.append(name_pos)
    for i in rows:
        contract_num = i.find('a').text.strip()[2:]
        list_contract.append(contract_num)
    num_page = num_page + 1

    rows = get_rows(name_pos, num_page)

    time.sleep(5)

with open('list_contract.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter='\n')
    writer.writerow(list_contract)
