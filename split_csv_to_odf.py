import os
import csv
import pyexcel_ods
from lib_gz import data_path

files = os.listdir(data_path)
csv_files = [f for f in files if f.endswith('.csv')]
for csv_file in csv_files:
    with open(data_path + csv_file, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        data = [row for row in reader]

del data[0]
list_find_text = {row[10] for row in data}
for find_text in list_find_text:
    data_find_text = [row[:10] for row in data if row[10] == find_text]
    data_find_text.sort(key=lambda x: x[1])
    data_find_text.insert(0, ['sname', 'name', 'name_dop', 'qty', 'unit', 'price', 'total', 'contract', 'year', 'customer'])
    pyexcel_ods.save_data(data_path + find_text + '.ods', {'Sheet 1': data_find_text})


