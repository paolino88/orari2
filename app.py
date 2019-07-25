from flask import Flask, render_template, url_for
from tabula import read_pdf
import urllib.request
import pandas as pd
import numpy as np
import datetime
import re


app = Flask(__name__)

@app.route('/')

def index():
    urllib.request.urlretrieve(
        'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/invernale/arancio.pdf',
        'arancio.pdf')
    df = read_pdf('arancio.pdf')
    l1 = df.loc[[1]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
                                                                                               axis=1).values
    l2 = df.loc[[10]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^A"),
                                                                                                axis=1).values
    li = np.concatenate((l1[0], l2[0]), axis=0)

    dict = {}
    for el in li:
        t = re.findall(r'\d+', el)
        if not int(t[0]) in dict.keys():
            dict[int(t[0])] = [int(t[1])]
        else:
            dict[int(t[0])].append(int(t[1]))


    time = datetime.datetime.now()
    tup = []
    hour = time.hour
    minute = time.minute


    if hour in dict.keys():
        list_min = [item for item in dict[hour] if minute < item]
        if (len(list_min) == 1):
            if(hour == max(dict.keys())):
                delta_minute = list_min[0] - minute
                tup.append(delta_minute)
            else:
                delta_minute = list_min[0] - minute
                tup.append(delta_minute)
                delta_minute_next = dict[hour + 1][0] + 60 - minute
                tup.append(delta_minute_next)
        elif(len(list_min) > 1):
            delta_minute = list_min[0] - minute
            tup.append(delta_minute)
            delta_minute_next = list_min[1] - minute
            tup.append(delta_minute_next)
        else:
            if(hour == max(dict.keys())):
                delta_minute = 'NON CI SONO CORSE PER OGGI'
                tup.append(delta_minute)
            else:
                delta_minute = dict[hour + 1][0] + 60 - minute
                tup.append(delta_minute)
                delta_minute_next = dict[hour + 1][1] + 60 - minute
                tup.append(delta_minute_next)
    else:
        if (hour < min(dict.keys())):
            hh = min(dict.keys()) - hour
            delta_minute = 'INIZIA TRA ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
            tup.append(delta_minute)
        else:
            delta_minute = 'NON CI SONO CORSE PER OGGI'
            tup.append(delta_minute)

    return render_template("index.html", tup=tup, hour=hour, minute=minute)


if __name__ == '__main__':
    app.run(use_reloader = True,debug=True)