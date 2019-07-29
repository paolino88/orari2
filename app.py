from flask import Flask, render_template, url_for
from tabula import read_pdf
import urllib.request
import pandas as pd
import numpy as np
import datetime
import re


app = Flask(__name__)

@app.route('/andata')
def andata():

    def schedul(l1):
        l11 = np.array([])
        for i in range(l1.shape[1]):
            n = np.array(re.findall(r'\d{2}:\d{2}', l1[0][i]))
            l11 = np.concatenate((l11, n), axis=0)
        return l11

    def build_dict(li):
        dict = {}
        for el in li:
            t = re.findall(r'\d+', el)
            if not int(t[0]) in dict.keys():
                dict[int(t[0])] = [int(t[1])]
            else:
                dict[int(t[0])].append(int(t[1]))
        return dict

    today = datetime.datetime.today()
    time = datetime.datetime.now()
    num_month = time.month
    num_day = today.weekday() + 1

    if(num_day != 6 and num_day != 7):
        if (num_month < 5 or num_month > 9):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/invernale/arancio.pdf',
                'arancio.pdf')
            df = read_pdf('arancio.pdf')
            l1 = df.loc[[1]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
                                                                                                   axis=1).values
            l2 = df.loc[[10]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^A"),
                                                                                                     axis=1).values
            var='ORARIO INVERNALE'
        elif(num_day != 5):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/arancio.pdf',
                'arancio.pdf')
            df = read_pdf('arancio.pdf')
            l1 = df.loc[[3]].replace(r'.* (\d{2}:\d{2})', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
                                                                                                       axis=1).values
            l2 = df.loc[[14]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R"),
                                                                                                    axis=1).values
            var='ORARIO ESTIVO'
        else:
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/arancio.pdf',
                'arancio.pdf')
            df = read_pdf('arancio.pdf')
            l1 = df.loc[[21]].replace(r'.* (\d{2}:\d{2})', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
                                                                                                        axis=1).values
            l2 = df.loc[[33]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R"),
                                                                                                    axis=1).values
            var='VENERDI\' ESTIVO - ORARIO RIDOTTO'



        l11 = schedul(l1)
        l22 = schedul(l2)

        li = np.concatenate((l11, l22), axis=0)

        dict = build_dict(li)

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
                delta_minute = min(list_min) - minute
                tup.append(delta_minute)
                list_min.remove(min(list_min))
                delta_minute_next = min(list_min) - minute
                tup.append(delta_minute_next)
            else:
                if(hour == max(dict.keys())):
                    delta_minute = 'NON CI SONO CORSE PER OGGI'
                    tup.append(delta_minute)
                else:
                    if(len(dict[hour + 1]) > 1):
                        delta_minute = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute)
                        dict[hour + 1].remove(min(dict[hour + 1]))
                        delta_minute_next = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute_next)
                    elif(hour + 1 < max(dict.keys())):
                        delta_minute = 'UNICA CORSA DELLA FASCIA ORARIA ' + str(hour + 1) + 'TRA ' + \
                                                                str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'ULTIMA CORSA DEL GIORNO TRA ' + \
                                                                str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if(hh < 2):
                    delta_minute = 'IL SERVIZIO INIZIA TRA ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'IL SERVIZIO INIZIA ALLE ' + str(datetime.time(min(dict.keys()),M).strftime("%H:%M"))
                    tup.append(delta_minute)
            else:
                delta_minute = 'NON CI SONO CORSE PER OGGI'
                tup.append(delta_minute)
    else:
        tup=[]
        var = 'Il servizio riprendera\' il primo giorno feriale utile'
    return render_template("andata.html", tup=tup, var=var)

@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(use_reloader = True,debug=True)