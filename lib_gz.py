import os
import re
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time

data_path = './data/'
file_db = 'gz.sqlite3'
HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
}


def clean_str(x: str) -> str:
    """Removes leading non-alphabetic characters, redundant spaces, quotes and semicolons."""
    x = ' '.join(x.split()).replace('"', '').replace("'", '').replace(';', '')
    return x.lstrip('0123456789. ')


def clean_num(x: str) -> str:
    """Removes all characters except numbers, dot and comma."""
    return re.sub(r"[^\d.,]", "", x)


def replace_comma(x: str) -> str:
    """Replaces comma with dot in a number."""
    return x.replace(',', '.')


def get_soup(url):
    while True:
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()  # Check for any request errors
            soup = BeautifulSoup(response.text, 'html.parser')
            time.sleep(7)
            return soup
        except Exception as e:
            print(f'Connection error: {e}. Pausing for 1 minute.')
            time.sleep(60)


def contract_items_parsing(contract_positions):
    contract_items = []

    # Fill the data list with contract positions
    for item in contract_positions:
        name = item.find('div', class_='padBtm5 inline js-expand-all-list--not-count')
        qtyUnit = item.find('div', class_='align-items-center')
        priceAndSum = item.find_all('td', class_='tableBlock__col tableBlock__col_right')
        if name and qtyUnit and priceAndSum:
            name = clean_str(name.text)
            name_dop = clean_str(item.find_all('td', class_='tableBlock__col')[2].text)

            # Converting quantity and measurement units columns
            qtyUnit = qtyUnit.text.strip()
            try:
                qty, unit = qtyUnit.split('\n')
                qty = clean_num(qty)
                unit = clean_str(unit)
            except:
                qty = 0
                unit = clean_str(qtyUnit)

            # Converting price and sum columns
            price = clean_num(priceAndSum[0].text.strip())
            summ = priceAndSum[1].text.strip()
            summ = clean_num(summ[:summ.find('\n')])

            contract_items.append(
                {'name': name, 'name_dop': name_dop, 'qty': qty, 'unit': unit, 'price': price, 'summ': summ})

    return contract_items


def convert_ods_to_csv(file_output):
    """Converts all ods files in the data_path directory to csv files and
    generates a final file file_name in csv format."""
    list_files_ods = sorted([i for i in os.listdir(data_path) if i.endswith('.ods')])
    with open(file_output, 'w') as f:
        for item in list_files_ods:
            print(f'Processing file {item}')
            file_csv = f'{data_path}{item[:-4]}.csv'
            read_file = pd.read_excel(f'{data_path}{item}')
            read_file.to_csv(file_csv, index=False, sep=';', header=bool(list_files_ods.index(item) == 0))
