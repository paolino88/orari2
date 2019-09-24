from flask import Flask, render_template, url_for
from tabula import read_pdf
import urllib.request
import pandas as pd
import numpy as np
import datetime
import re


app = Flask(__name__)

@app.route('/arancio_andata')
def arancio_andata():
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
                    delta_minute = 'Ulitmo del giorno tra ' + str(list_min[0] - minute) + ' min'
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
                        delta_minute = 'Unico delle ore ' + str(hour + 1) + 'tra ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'Ultimo del giorno tra ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if(hh < 2):
                    delta_minute = 'Inizio tra ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'Inizio alle ' + str(datetime.time(min(dict.keys()),M).strftime("%H:%M"))
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
def arancio_ritorno():
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
                    delta_minute = 'Ulitmo del giorno tra ' + str(list_min[0] - minute) + ' min'
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
                        delta_minute = 'Unico delle ore ' + str(hour + 1) + 'tra ' + \
                                                                str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'Ultimo del giorno tra ' + \
                                                                str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if(hh < 2):
                    delta_minute = 'Inizio tra ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'Inizio alle ' + str(datetime.time(min(dict.keys()),M).strftime("%H:%M"))
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
def rossa_andata():
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
    num_month = time.month
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
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/rossa.pdf',
                'rossa.pdf')
            df = read_pdf('rossa.pdf')

            ind = df[df.iloc[:,0].str.contains('MM3')].index[0]
            lis=df.iloc[ind:,0].values

            var='ORARIO ESTIVO'
        else:
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/rossa.pdf',
                'rossa.pdf')
            df = read_pdf('rossa.pdf')

            ind = df[df.iloc[:,0].str.contains('MM3')].index[0]
            lis=df.iloc[ind:,0].values

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
                    delta_minute = 'Ulitmo del giorno tra ' + str(list_min[0] - minute) + ' min'
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
                        delta_minute = 'Unico delle ore ' + str(hour + 1) + 'tra ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'Ultimo del giorno tra ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if(hh < 2):
                    delta_minute = 'Inizio tra ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'Inizio alle ' + str(datetime.time(min(dict.keys()),M).strftime("%H:%M"))
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
def rossa_ritorno():
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
    num_month = time.month
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
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/rossa.pdf',
                'rossa.pdf')
            df = read_pdf('rossa.pdf')

            ind = df.iloc[:, 1].dropna().str.contains('Emilia')
            idx = ind[ind].index.values
            lis = df.iloc[idx[0]:idx[1], 1].dropna().values

            var='ORARIO ESTIVO'
        else:
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/rossa.pdf',
                'rossa.pdf')
            df = read_pdf('rossa.pdf')

            ind = df.iloc[:, 1].dropna().str.contains('Emilia')
            idx = ind[ind].index.values
            lis = df.iloc[idx[1]:,1].dropna().values

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
                    delta_minute = 'Ulitmo del giorno tra ' + str(list_min[0] - minute) + ' min'
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
                        delta_minute = 'Unico delle ore ' + str(hour + 1) + 'tra ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'Ultimo del giorno tra ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if(hh < 2):
                    delta_minute = 'Inzio tra ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'Inizio alle ' + str(datetime.time(min(dict.keys()),M).strftime("%H:%M"))
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






@app.route('/blu_andata')
def blu_andata():
    direction = 'Via Fabiani - Via XXV Aprile'
    def schedul(lis):
        li = []
        for el in lis:
            t = re.findall(r'\d{2}:\d{2}', el)
            for el0 in t:
                li.append(el0)
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
    num_month = time.month
    num_day = today.weekday() + 1

    if(num_day != 6 and num_day != 7):
        urllib.request.urlretrieve(
            'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/blu.pdf',
            'blu.pdf')
        df = read_pdf('blu.pdf', multiple_tables=True)

        if (num_month < 5 or num_month > 9):

            ind0 = df[0].iloc[:, 0].dropna().str.contains('Via Fabiani')
            idx0 = ind0[ind0].index.values
            lis0 = df[0].iloc[idx0[0]].dropna().values
            ind1 = df[1].iloc[:, 0].dropna().str.contains('Via Fabiani')
            idx1 = ind1[ind1].index.values
            lis00 = np.concatenate((df[1].iloc[idx1[0]].dropna().values, df[1].iloc[idx1[1]].dropna().values), axis=0)
            lis = np.concatenate((lis0, lis00), axis=0)

            var='ORARIO INVERNALE'
        elif(num_day != 5):
            ind0 = df[0].iloc[:, 0].dropna().str.contains('Via Fabiani')
            idx0 = ind0[ind0].index.values
            lis0 = df[0].iloc[idx0[0]].dropna().values
            ind1 = df[1].iloc[:, 0].dropna().str.contains('Via Fabiani')
            idx1 = ind1[ind1].index.values
            lis00 = np.concatenate((df[1].iloc[idx1[0]].dropna().values, df[1].iloc[idx1[1]].dropna().values), axis=0)
            lis = np.concatenate((lis0, lis00), axis=0)

            var='ORARIO ESTIVO'
        else:
            ind0 = df[0].iloc[:, 0].dropna().str.contains('Via Fabiani')
            idx0 = ind0[ind0].index.values
            lis0 = df[0].iloc[idx0[0]].dropna().values
            ind1 = df[1].iloc[:, 0].dropna().str.contains('Via Fabiani')
            idx1 = ind1[ind1].index.values
            lis00 = np.concatenate((df[1].iloc[idx1[-2]].dropna().values, df[1].iloc[idx1[-1]].dropna().values), axis=0)
            lis = np.concatenate((lis0, lis00), axis=0)


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
                    delta_minute =  'Ulitmo del giorno tra ' + str(list_min[0] - minute) + ' min'
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
                        delta_minute = 'Unico delle ore ' + str(hour + 1) + 'tra ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'Ultimo del giorno tra ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if(hh < 2):
                    delta_minute = 'Inizio tra ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'Inizio alle ' + str(datetime.time(min(dict.keys()),M).strftime("%H:%M"))
                    tup.append(delta_minute)
            else:
                delta_minute = "Finish"#'NON CI SONO CORSE PER OGGI'
                tup.append(delta_minute)
    else:
        var=''
        tup=[]
        delta_minute = 'Stop'
        tup.append(delta_minute)
    return render_template("orari_blu.html", tup=tup, var=var, direction=direction)


@app.route('/blu_ritorno')
def blu_ritorno():
    direction = 'Via XXV Aprile - Via Fabiani'

    def schedul(lis):
        li = []
        for el in lis:
            t = re.findall(r'\d{2}:\d{2}', el)
            for el0 in t:
                li.append(el0)
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
    num_month = time.month
    num_day = today.weekday() + 1

    if (num_day != 6 and num_day != 7):
        urllib.request.urlretrieve(
            'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/blu.pdf',
            'blu.pdf')
        df = read_pdf('blu.pdf', multiple_tables=True)

        if (num_month < 5 or num_month > 9):

            ind0 = df[0].iloc[:, 0].dropna().str.contains('Via XXV')
            idx0 = ind0[ind0].index.values
            lis0 = df[0].iloc[idx0[0]].dropna().values
            ind1 = df[1].iloc[:, 0].dropna().str.contains('Via XXV')
            idx1 = ind1[ind1].index.values
            lis00 = np.concatenate((df[1].iloc[idx1[1]].dropna().values, df[1].iloc[idx1[2]].dropna().values), axis=0)
            lis = np.concatenate((lis0, lis00), axis=0)

            var = 'ORARIO INVERNALE'
        elif (num_day != 5):
            ind0 = df[0].iloc[:, 0].dropna().str.contains('Via XXV')
            idx0 = ind0[ind0].index.values
            lis0 = df[0].iloc[idx0[0]].dropna().values
            ind1 = df[1].iloc[:, 0].dropna().str.contains('Via XXV')
            idx1 = ind1[ind1].index.values
            lis00 = np.concatenate((df[1].iloc[idx1[1]].dropna().values, df[1].iloc[idx1[2]].dropna().values), axis=0)
            lis = np.concatenate((lis0, lis00), axis=0)

            var = 'ORARIO ESTIVO'
        else:
            ind0 = df[0].iloc[:, 0].dropna().str.contains('Via XXV')
            idx0 = ind0[ind0].index.values
            lis0 = df[0].iloc[idx0[0]].dropna().values
            ind1 = df[1].iloc[:, 0].dropna().str.contains('Via XXV')
            idx1 = ind1[ind1].index.values
            lis00 = np.concatenate((df[1].iloc[idx1[-2]].dropna().values, df[1].iloc[idx1[-1]].dropna().values), axis=0)
            lis = np.concatenate((lis0, lis00), axis=0)

            var = 'VENERDI\' ESTIVO - ORARIO RIDOTTO'

        li = schedul(lis)

        dict = build_dict(li)

        time = datetime.datetime.now()
        tup = []
        hour = time.hour
        minute = time.minute

        if hour in dict.keys():
            list_min = [item for item in dict[hour] if minute < item]
            if (len(list_min) == 1):
                if (hour == max(dict.keys())):
                    delta_minute = 'Ulitmo del giorno tra ' + str(list_min[0] - minute) + ' min'
                    tup.append(delta_minute)
                else:
                    delta_minute = list_min[0] - minute
                    tup.append(delta_minute)
                    delta_minute_next = dict[hour + 1][0] + 60 - minute
                    tup.append(delta_minute_next)
            elif (len(list_min) > 1):
                delta_minute = min(list_min) - minute
                tup.append(delta_minute)
                list_min.remove(min(list_min))
                delta_minute_next = min(list_min) - minute
                tup.append(delta_minute_next)
            else:
                if (hour == max(dict.keys())):
                    delta_minute = "Finish"  # 'NON CI SONO CORSE PER OGGI'
                    tup.append(delta_minute)
                else:
                    if (len(dict[hour + 1]) > 1):
                        delta_minute = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute)
                        dict[hour + 1].remove(min(dict[hour + 1]))
                        delta_minute_next = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute_next)
                    elif (hour + 1 < max(dict.keys())):
                        delta_minute = 'Unico delle ore ' + str(hour + 1) + 'tra ' + str(
                            min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'Ultimo del giorno tra ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if (hh < 2):
                    delta_minute = 'Inizio alle ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'Inizio tra ' + str(datetime.time(min(dict.keys()), M).strftime("%H:%M"))
                    tup.append(delta_minute)
            else:
                delta_minute = "Finish"  # 'NON CI SONO CORSE PER OGGI'
                tup.append(delta_minute)
    else:
        var = ''
        tup = []
        delta_minute = 'Stop'
        tup.append(delta_minute)
    return render_template("orari_blu.html", tup=tup, var=var, direction=direction)






@app.route('/verde_andata')
def verde_andata():
    direction = 'FS(MM3) - Bolgiano'

    def build_dict(dat):
        dict = {}
        for l in dat:
            el = re.findall(r'\d{2}', l)
            if not int(el[0]) in dict.keys():
                dict[int(el[0])] = [int(el[1])]
            else:
                dict[int(el[0])].append(int(el[1]))
        return dict

    today = datetime.datetime.today()
    time = datetime.datetime.now()
    num_month = time.month
    num_day = today.weekday() + 1

    if (num_day != 6 and num_day != 7):
        if (num_month < 5 or num_month > 9):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/invernale/verde.pdf',
                'verde.pdf')
            df = read_pdf('verde.pdf', multiple_tables=True)

            Data = df[0].rename(columns={0: "A", 1: "B", 2: "C", 3: "D", 4: "E"})
            dat = Data.A[Data.A.str.contains('\d+:', regex=True, na=False)].values

            var = 'ORARIO INVERNALE'
        elif (num_day != 5):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/verde.pdf',
                'verde.pdf')
            df = read_pdf('verde.pdf', multiple_tables=True)

            Data = df[0].rename(columns={0: "A", 1: "B", 2: "C", 3: "D", 4: "E"})
            dat = Data.A[Data.A.str.contains('\d+:', regex=True, na=False)].values

            var = 'ORARIO ESTIVO'
        else:
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/verde.pdf',
                'verde.pdf')
            df = read_pdf('verde.pdf', multiple_tables=True)

            Data = df[0].rename(columns={0: "A", 1: "B", 2: "C", 3: "D", 4: "E"})
            dat = Data.A[Data.A.str.contains('\d+:', regex=True, na=False)].values

            var = 'VENERDI\' ESTIVO - ORARIO RIDOTTO'


        dict = build_dict(dat)

        time = datetime.datetime.now()
        tup = []
        hour = time.hour
        minute = time.minute


        if hour in dict.keys():
            list_min = [item for item in dict[hour] if minute < item]
            if (len(list_min) == 1):
                if (hour == max(dict.keys())):
                    delta_minute = 'Ulitmo del giorno tra ' + str(list_min[0] - minute) + ' min'
                    tup.append(delta_minute)
                else:
                    delta_minute = list_min[0] - minute
                    tup.append(delta_minute)
                    delta_minute_next = dict[hour + 1][0] + 60 - minute
                    tup.append(delta_minute_next)
            elif (len(list_min) > 1):
                delta_minute = min(list_min) - minute
                tup.append(delta_minute)
                list_min.remove(min(list_min))
                delta_minute_next = min(list_min) - minute
                tup.append(delta_minute_next)
            else:
                if (hour == max(dict.keys())):
                    delta_minute = "Finish"  # 'NON CI SONO CORSE PER OGGI'
                    tup.append(delta_minute)
                else:
                    if (len(dict[hour + 1]) > 1):
                        delta_minute = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute)
                        dict[hour + 1].remove(min(dict[hour + 1]))
                        delta_minute_next = min(dict[hour + 1]) + 60 - minute
                        tup.append(delta_minute_next)
                    elif (hour + 1 < max(dict.keys())):
                        delta_minute = 'Unico delle ore ' + str(hour + 1) + 'tra ' + str(
                            min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)
                    else:
                        delta_minute = 'Ultimo del giorno tra ' + str(min(dict[hour + 1]) + 60 - minute) + ' min'
                        tup.append(delta_minute)

        else:
            if (hour < min(dict.keys())):
                hh = min(dict.keys()) - hour
                if (hh < 2):
                    delta_minute = 'Inizio alle ' + str(hh * 60 - minute + min(dict[min(dict.keys())])) + ' min'
                    tup.append(delta_minute)
                else:
                    M = min(dict[min(dict.keys())])
                    delta_minute = 'Inizio tra ' + str(datetime.time(min(dict.keys()), M).strftime("%H:%M"))
                    tup.append(delta_minute)
            else:
                delta_minute = "Finish"  # 'NON CI SONO CORSE PER OGGI'
                tup.append(delta_minute)
    else:
        var = ''
        tup = []
        delta_minute = 'Stop'
        tup.append(delta_minute)
    return render_template("orari_verde.html", tup=tup, var=var, direction=direction)














@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(use_reloader = True,debug=True)