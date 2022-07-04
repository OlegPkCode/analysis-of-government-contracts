data_path = './data/'
file_db = 'gz.sqlite3'


# Удаляем впередистоящие знаки отличные от символьных, дублирующие пробелы, кавычки и знаки ';'
def convert_str(x):
    x = x.strip()
    if len(x) > 0:
        while x[0].isdecimal():
            x = x[1:]

    x = ' '.join(x.split())
    x = x.replace('"', '')
    x = x.replace("'", '')
    x = x.replace(';', '')

    return x


# Удаляем все пробелы из числа
def convert_num(x):
    return ''.join(x.split())


# Переворачиваем запятую на точку в числе
def convert_num_dot(x):
    return x.replace(',', '.')
