'''
This script parses contract data from a website, which is recorded in the file_input file.
The format of the file_input file is:
Contract Number; Year; Customer
The result is recorded in the file_output file.
'''

import csv
import time

from lib_gz import data_path, clean_str, clean_num, replace_comma, get_soup

file_input = f'{data_path}contracts.csv'
file_output = f'{data_path}contract_items.csv'


def parsing_contract(contract, customer):
    HEADER_URL = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order.html?reestrNumber=' + contract + '&#contractSubjects'
    ITEMS_URL = 'https://zakupki.gov.ru/epz/contract/contractCard/payment-info-and-target-of-order-list.html?reestrNumber=' + contract + '&page=1&pageSize=200'
    header_soup = get_soup(HEADER_URL)
    contract_soup = get_soup(ITEMS_URL)
    position_list = contract_soup.find('tbody', class_='tableBlock__body').find_all('tr', class_='tableBlock__row')

    data = []
    pos = 0
    total = 0

    # Fill the data list with contract positions
    for item in position_list:
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
            sum = priceAndSum[1].text.strip()
            sum = clean_num(sum[:sum.find('\n')])

            pos += 1
            total += float(replace_comma(sum))

            data.append(
                {'name': name, 'name_dop': name_dop, 'qtyUnit': qtyUnit, 'qty': qty, 'unit': unit, 'price': price,
                 'sum': sum})

    # Record the year the contract was fulfilled
    year_finish = header_soup.find('div', class_='date mt-auto').find_all('div', class_='cardMainInfo__section')[
                      1].text.strip()[-4:]

    # Full name of the customer
    customer_full_name = header_soup.find('span', class_='cardMainInfo__content').text.strip()

    # Take the total amount of positions of this contract on the site
    total_in_site = clean_num(header_soup.find('td', class_='tableBlock__col tableBlock__col_right cost').text.strip())
    total_in_site = float(replace_comma(total_in_site))

    # If the total amount of imported positions equals the contract sum on the site - write the result to the file
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
                        clean_str(customer_full_name),
                        customer
                    )
                )

        print(
            f'Contract: {contract}, Year: {year_finish}, Positions - {pos}, Customer: {customer}, Processing: {time.strftime("%H:%M:%S")}')
        print(f'Sum of imported positions - {total}')
        print(f'Sum of positions according to the site data - {total_in_site}', end="\n\n")
    else:
        print('!!!!! THE SUM OF IMPORTED POSITIONS DOES NOT MATCH THE TOTAL CONTRACT SUM ON THE SITE!!!!!')
        print('Positions - ', pos)
        print('Sum of imported positions - ', total)
        print('Sum of positions on the site - ', total_in_site)


def load_contracts(file_input: str):
    with open(file_input, 'r') as file:
        contracts = [line.strip() for line in file]
    return contracts


if __name__ == "__main__":

    contracts = load_contracts(file_input)

    # Parse contracts from the list
    for item in contracts:
        contract, year, customer = item.split(';')
        parsing_contract(contract, customer)
