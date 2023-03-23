import os
import re

import pandas as pd

data_path = './data/'
file_db = 'gz.sqlite3'


# Удаляем впередистоящие знаки отличные от символьных, дублирующие пробелы, кавычки и знаки ';'
def convert_str(x):
    x = x.strip()
    x = ' '.join(x.split())
    x = x.replace('"', '')
    x = x.replace("'", '')
    x = x.replace(';', '')

    while len(x) > 0 and not x[0].isalpha():
        x = x[1:]

    return x


# Удаляем из все символы, кроме чисел, точки и запятой
def convert_num(x):
    x = re.sub(r"[^\d.,]", "", x)
    return x


# Переворачиваем запятую на точку в числе
def convert_num_dot(x):
    return x.replace(',', '.')


# Функция конвертирует все файлы ods в каталоге data_path в файлы csv и формирует итоговый файл file_name в формате csv
def convert_ods_to_csv(file_output):
    list_files_ods = [i for i in os.listdir(data_path) if i.endswith('.ods')]
    list_files_ods.sort()

    with open(file_output, 'w') as f:
        for item in list_files_ods:
            print('Обработка файла', item)
            file_csv = data_path + item[:-4] + '.csv'
            read_file = pd.read_excel(data_path + item)
            read_file.to_csv(file_csv, index=False, sep=';', header=(lambda *x: list_files_ods.index(item) == 0)())
