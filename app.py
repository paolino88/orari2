from flask import Flask, render_template, url_for
from tabula import read_pdf
import urllib.request
import pandas as pd
import numpy as np
import datetime
import re


app = Flask(__name__)

@app.route('/arancio_andata')
def andata():
    direction = 'VIA EMILIA - BOLGIANO'
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
                    delta_minute =  'The last one in ' + str(list_min[0] - minute) + ' min'
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
                    delta_minute = "Finish"#'NON CI SONO CORSE PER OGGI'
                    tup.append(delta_minute)
                else:
                    if(len(dict[hour + 1]) > 1):
                        delta_minute = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute)
                        dict[hour + 1].remove(min(dict[hour + 1]))
                        delta_minute_next = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute_next)
                    elif(hour + 1 < max(dict.keys())):
                        delta_minute = 'The only one in this hour ' + str(hour + 1) + 'in ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'The Last one in ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if(hh < 2):
                    delta_minute = 'Start in ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'Start at ' + str(datetime.time(min(dict.keys()),M).strftime("%H:%M"))
                    tup.append(delta_minute)
            else:
                delta_minute = "Finish"#'NON CI SONO CORSE PER OGGI'
                tup.append(delta_minute)
    else:
        var=''
        tup=[]
        delta_minute = 'Stop'
        tup.append(delta_minute)
    return render_template("orari_arancio.html", tup=tup, var=var, direction=direction)



@app.route('/arancio_ritorno')
def ritorno():
    direction = 'BOLGIANO - VIA EMILIA'
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
            l1 = df.loc[[4]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R|A$"),
                                                                                                   axis=1).values
            l2 = df.loc[[8]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*R.*"),
                                                                                                     axis=1).values
            var='ORARIO INVERNALE'
        elif(num_day != 5):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/arancio.pdf',
                'arancio.pdf')
            df = read_pdf('arancio.pdf')
            l1 = df.loc[[7]].replace(r'.* (\d{2}:\d{2})', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R|A$"),
                                                                                                       axis=1).values
            l2 = df.loc[[10]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
                                                                                                    axis=1).values
            var='ORARIO ESTIVO'
        else:
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/arancio.pdf',
                'arancio.pdf')
            df = read_pdf('arancio.pdf')
            l1 = df.loc[[25]].replace(r'.* (\d{2}:\d{2})', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R|A$"),
                                                                                                        axis=1).values
            l2 = df.loc[[29]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
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
                    delta_minute = 'The last one in ' + str(list_min[0] - minute) + ' min'
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
                    delta_minute = "Finish"#'NON CI SONO CORSE PER OGGI'
                    tup.append(delta_minute)
                else:
                    if(len(dict[hour + 1]) > 1):
                        delta_minute = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute)
                        dict[hour + 1].remove(min(dict[hour + 1]))
                        delta_minute_next = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute_next)
                    elif(hour + 1 < max(dict.keys())):
                        delta_minute = 'The only one in this hour ' + str(hour + 1) + 'in ' + \
                                                                str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'The Last one in ' + \
                                                                str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if(hh < 2):
                    delta_minute = 'Start in ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'Start at ' + str(datetime.time(min(dict.keys()),M).strftime("%H:%M"))
                    tup.append(delta_minute)
            else:
                delta_minute = "Finish"#'NON CI SONO CORSE PER OGGI'
                tup.append(delta_minute)
    else:
        var=''
        tup=[]
        delta_minute = 'Stop'
        tup.append(delta_minute)
    return render_template("orari_arancio.html", tup=tup, var=var, direction=direction)











@app.route('/rossa_andata')
def andata():
    direction = 'FS(MM3) - Via Emilia'
    def schedul(lis):
        li = []
        for el in lis:
            if (re.findall(r':', el)):
                el = re.sub(r'^(\d+:\d+).*', r'\1', el)
                li.append(el)
        return li

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
    num_month = 2#time.month
    num_day = today.weekday() + 1

    if(num_day != 6 and num_day != 7):
        if (num_month < 5 or num_month > 9):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/invernale/rossa.pdf',
                'rossa.pdf')
            df = read_pdf('rossa.pdf')

            ind = df[df.iloc[:,0].str.contains('MM3')].index[0]
            lis=df.iloc[ind:,0].values

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



        li = schedul(lis)

        dict = build_dict(li)

        time = datetime.datetime.now()
        tup = []
        hour = time.hour
        minute = time.minute


        if hour in dict.keys():
            list_min = [item for item in dict[hour] if minute < item]
            if (len(list_min) == 1):
                if(hour == max(dict.keys())):
                    delta_minute =  'The last one in ' + str(list_min[0] - minute) + ' min'
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
                    delta_minute = "Finish"#'NON CI SONO CORSE PER OGGI'
                    tup.append(delta_minute)
                else:
                    if(len(dict[hour + 1]) > 1):
                        delta_minute = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute)
                        dict[hour + 1].remove(min(dict[hour + 1]))
                        delta_minute_next = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute_next)
                    elif(hour + 1 < max(dict.keys())):
                        delta_minute = 'The only one in this hour ' + str(hour + 1) + 'in ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'The Last one in ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if(hh < 2):
                    delta_minute = 'Start in ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'Start at ' + str(datetime.time(min(dict.keys()),M).strftime("%H:%M"))
                    tup.append(delta_minute)
            else:
                delta_minute = "Finish"#'NON CI SONO CORSE PER OGGI'
                tup.append(delta_minute)
    else:
        var=''
        tup=[]
        delta_minute = 'Stop'
        tup.append(delta_minute)
    return render_template("orari_rossa.html", tup=tup, var=var, direction=direction)








@app.route('/rossa_ritorno')
def andata():
    direction = 'Via Emilia - FS(MM3)'
    def schedul(lis):
        li = []
        for el in lis:
            if (re.findall(r':', el)):
                el = re.sub(r'^(\d+:\d+).*', r'\1', el)
                li.append(el)
        return li

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
    num_month = 2#time.month
    num_day = today.weekday() + 1

    if(num_day != 6 and num_day != 7):
        if (num_month < 5 or num_month > 9):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/invernale/rossa.pdf',
                'rossa.pdf')
            df = read_pdf('rossa.pdf')

            ind = df.iloc[:, 1].dropna().str.contains('Emilia').index[0]
            lis = df.iloc[ind:, 1].dropna().values

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



        li = schedul(lis)

        dict = build_dict(li)

        time = datetime.datetime.now()
        tup = []
        hour = time.hour
        minute = time.minute


        if hour in dict.keys():
            list_min = [item for item in dict[hour] if minute < item]
            if (len(list_min) == 1):
                if(hour == max(dict.keys())):
                    delta_minute =  'The last one in ' + str(list_min[0] - minute) + ' min'
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
                    delta_minute = "Finish"#'NON CI SONO CORSE PER OGGI'
                    tup.append(delta_minute)
                else:
                    if(len(dict[hour + 1]) > 1):
                        delta_minute = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute)
                        dict[hour + 1].remove(min(dict[hour + 1]))
                        delta_minute_next = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute_next)
                    elif(hour + 1 < max(dict.keys())):
                        delta_minute = 'The only one in this hour ' + str(hour + 1) + 'in ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'The Last one in ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if(hh < 2):
                    delta_minute = 'Start in ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'Start at ' + str(datetime.time(min(dict.keys()),M).strftime("%H:%M"))
                    tup.append(delta_minute)
            else:
                delta_minute = "Finish"#'NON CI SONO CORSE PER OGGI'
                tup.append(delta_minute)
    else:
        var=''
        tup=[]
        delta_minute = 'Stop'
        tup.append(delta_minute)
    return render_template("orari_rossa.html", tup=tup, var=var, direction=direction)














@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(use_reloader = True,debug=True)