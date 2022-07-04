import os
from lib_parse import data_path

file_output = data_path + 'all.csv'

# Заходит в папку <data_path> текущего проекта, берет все файлы *.csv и конкотинирует их в файл all.csv

ls = [i for i in os.listdir(data_path) if i.endswith('.csv')]
ls.sort()
with open(file_output,'w') as file:
    for j in ls:
        s = open(data_path + j).read()
        file.write(s)


