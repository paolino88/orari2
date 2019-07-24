from flask import Flask, render_template
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
    strin = ''
    hour = time.hour
    minute = time.minute

    if hour in dict.keys():
        for m in dict[hour]:
            if (minute < m):
                delta_minute = m - minute
                list_min = [item for item in dict[hour] if minute < item]
                if (len(list_min) == 1):
                    delta_minute_next = dict[hour + 1][0] + 60 - minute
                else:
                    delta_minute_next = dict[hour][1] - minute
            elif (m == max(dict[hour])):
                delta_minute = dict[hour + 1][0] + 60 - minute
                delta_minute_next = dict[hour + 1][1] + 60 - minute

    else:
        if (hour < min(dict.keys())):
            hh = min(dict.keys()) - hour
            delta_minute = hh * 60 - minute + min(dict[min(dict.keys())])
        else:
            strin = 'NON CI SONO CORSE PER OGGI'


    return render_template("index.html", delta_minute=delta_minute,delta_minute_next=delta_minute_next,strin=strin)


if __name__ == '__main__':
    app.run(use_reloader = True,debug=True)