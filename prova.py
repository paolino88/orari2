from tabula import read_pdf
import urllib.request
import pandas as pd
import numpy as np
import datetime
import re




urllib.request.urlretrieve(
    'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/invernale/arancio.pdf',
    'arancio.pdf')
df = read_pdf('C:/Users/uid1031656/Desktop/arancio.pdf')
l1 = df.loc[[1]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
                                                                                           axis=1).values
l2 = df.loc[[10]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^A"), axis=1).values
li = np.concatenate((l1[0], l2[0]), axis=0)

dict = {}
for el in li:
    t = re.findall(r'\d+', el)
    if not int(t[0]) in dict.keys():
        dict[int(t[0])] = [int(t[1])]
    else:
        dict[int(t[0])].append(int(t[1]))

time = datetime.datetime.now()
if time.hour in dict.keys():
    for m in dict[time.hour]:
        if (time.minute < m):
            delta_minute = m - time.minute
            delta_minute_next = dict[time.hour + 1][0] + 60 - time.minute
            print(delta_minute)
            print(delta_minute_next)