import sqlite3 as sq

con = None

try:

    con = sq.connect('/home/olejonos/pni.db')
    cur = con.cursor()

    sname = "'бройлер'"
    sql2 = '''
    WHERE sname is null and total > 10000 and namea like '%цыплят%' and namea like '%бройлер%' and namea like '%тушк%' 
    '''
    sql1 = 'UPDATE positions SET sname = ' + sname + ' '
    cur.execute(sql1 + sql2.replace('\n', ''))
    sql2 = '''
    WHERE sname is null and total > 10000 and namea like '%мясо цыплят-бройлеров%' 
    '''
    sql1 = 'UPDATE positions SET sname = ' + sname + ' '
    cur.execute(sql1 + sql2.replace('\n', ''))

    con.commit()

except:
    if con: con.rollback()
    print('Ошибка выполнения запроса')

finally:
    if con: con.close()

# with sq.connect('/home/olejonos/pni.db') as con:
#     cur = con.cursor()
#
#     sname = "'бройлер'"
#     sql2 = '''
#     WHERE sname is null and total > 10000 and namea like '%цыплят%' and namea like '%бройлер%' and namea like '%тушк%'
#     '''
#     sql1 = 'UPDATE positions SET sname = ' + sname + ' '
#     cur.execute(sql1 + sql2.replace('\n', ''))
#     sql2 = '''
#     WHERE sname is null and total > 10000 and namea like '%мясо цыплят-бройлеров%'
#     '''
#     sql1 = 'UPDATE positions SET sname = ' + sname + ' '
#     cur.execute(sql1 + sql2.replace('\n', ''))
