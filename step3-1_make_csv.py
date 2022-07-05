import os
from lib_parse import data_path

file_output = data_path + 'all.csv'

# Заходит в папку <data_path> текущего проекта, берет все файлы *.csv и конкотинирует их в файл all.csv

with open(file_output,'w') as f:
    for adress, dirs, files in os.walk(data_path):
        for file in files:
            full_path = os.path.join(adress, file)
            if full_path[-4:] == '.csv':
                f.write(open(full_path).read())

