data_path = './data/'

def convert_str(x):
    # Удаляем впередистоящие знаки отличные от символьных, дублирующие пробелы, кавычки и знаки ';'
    x = x.strip()

    if len(x) > 0:
        while x[0].isdecimal():
            x = x[1:]

    x = ' '.join(x.split())
    x = x.replace('"', '')
    x = x.replace("'", '')
    x = x.replace(';', '')
    # Удаляем непереносимые пробелы
    # x = x.replace('\xa0', '')

    return x


# def convert_namePos(x):
#     # Удаляем впередистоящие знаки отличные от символьных,  кавычки , лишние пробелы в начале и в конце, знаки ";"
#     # Удаляем непереносимые пробелы
#
#     x = x.strip()
#
#     if len(x) > 0:
#         while x[0].isdecimal():
#             x = x[1:]
#
#     x = x.replace('"', '')
#     x = x.replace("'", '')
#     x = x.replace(";", '')
#     x = x.replace('\xa0', '')
#
#     # Удаляем дублирующие пробелы и переносы строки
#     x = ' '.join(x.split())
#
#     return x.strip()


def convert_num(x):
    # Удаляем все пробелы из числа
    # x = x.replace('\xa0', '')
    return ''.join(x.split())
