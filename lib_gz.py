import os
import re
import pandas as pd

data_path = './data/'
file_db = 'gz.sqlite3'


def clean_str(x: str) -> str:
    """Removes leading non-alphabetic characters, redundant spaces, quotes and semicolons."""
    x = ' '.join(x.split()).replace('"', '').replace("'", '').replace(';', '')
    return x.lstrip('0123456789 ')


def clean_num(x: str) -> str:
    """Removes all characters except numbers, dot and comma."""
    return re.sub(r"[^\d.,]", "", x)


def replace_comma(x: str) -> str:
    """Replaces comma with dot in a number."""
    return x.replace(',', '.')


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
