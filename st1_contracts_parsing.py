'''
This script parses contract data from a website, which is recorded in the file_input file.
The format of the file_input file is:
Contract Number; Year; Customer
The result is recorded in the file_output file.
'''

import csv
import time

from lib_gz import data_path, clean_str, clean_num, replace_comma, get_soup, contract_items_parsing

file_input = f'{data_path}contracts.csv'
file_output = f'{data_path}contract_items.csv'


def contract_parsing(contract, customer):
    HEADER_URL = f'https://zakupki.gov.ru/epz/contract/contractCard/' \
                 f'payment-info-and-target-of-order.html?reestrNumber={contract}&#contractSubjects'
    ITEMS_URL = f'https://zakupki.gov.ru/epz/contract/contractCard/' \
                f'payment-info-and-target-of-order-list.html?reestrNumber={contract}&page=1&pageSize=200'
    header_soup = get_soup(HEADER_URL)
    contract_items = get_soup(ITEMS_URL).find('tbody', class_='tableBlock__body') \
        .find_all('tr', class_='tableBlock__row')

    contract_items = contract_items_parsing(contract_items)
    total_sum_contract = 0
    number_of_items = 0
    for item in contract_items:
        total_sum_contract += float(replace_comma(item["summ"]))
        number_of_items += 1

    # Record the year the contract was fulfilled
    year_finish = header_soup.find('div', class_='date mt-auto') \
                      .find_all('div', class_='cardMainInfo__section')[1].text.strip()[-4:]

    # Full name of the customer
    customer_full_name = header_soup.find('span', class_='cardMainInfo__content').text.strip()

    # Take the total amount of positions of this contract on the site
    total_sum_header = clean_num(
        header_soup.find('td', class_='tableBlock__col tableBlock__col_right cost').text.strip())
    total_sum_header = float(replace_comma(total_sum_header))

    # If the total amount of imported positions equals the contract sum on the site - write the result to the file
    if round(total_sum_contract) == round(total_sum_header):
        with open(file_output, 'a', newline='') as file:
            writer = csv.writer(file, delimiter=';')
            for item in contract_items:
                writer.writerow((item['name'], item['name_dop'], item['qty'], item['unit'], item['price'], item['summ'],
                                 contract, year_finish, clean_str(customer_full_name), customer))

        print(f'Contract: {contract}, Year: {year_finish}, Positions - {number_of_items}, Customer: {customer}, '
              f'Processing: {time.strftime("%H:%M:%S")}')
        print(f'Sum of imported positions - {round(total_sum_contract)}')
        print(f'Sum of positions according to the site data - {round(total_sum_header)}', end="\n\n")
    else:
        print('!!!!! THE SUM OF IMPORTED POSITIONS DOES NOT MATCH THE TOTAL CONTRACT SUM ON THE SITE!!!!!')
        print(f'Positions - {number_of_items}')
        print(f'Sum of imported positions - {round(total_sum_contract)}')
        print(f'Sum of positions on the site - {round(total_sum_header)}')


def load_contracts(file_input: str):
    with open(file_input, 'r') as file:
        contracts = [line.strip() for line in file]
    return contracts


if __name__ == "__main__":

    contracts = load_contracts(file_input)

    # Parse contracts from the list
    for item in contracts:
        contract, year, customer = item.split(';')
        contract_parsing(contract, customer)
