import os
ls = [i for i in os.listdir() if i.endswith('.csv')]
ls.sort()
with open('all_data.csv','w') as f:
    for j in ls:
        s = open(j).read()
        f.write(s)
