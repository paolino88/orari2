from flask import Flask, render_template, url_for
from tabula import read_pdf
import urllib.request
import pandas as pd
import numpy as np
import datetime
import re


app = Flask(__name__)

today = datetime.datetime.today()
time = datetime.datetime.now()
num_month = time.month
num_day = today.weekday() + 1

def arancio_andata(direction,a,b):
    dir=direction
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


    if(num_day != 6 and num_day != 7):
        if (num_month < 5 or num_month > 9):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/invernale/arancio.pdf',
                'arancio.pdf')
            df = read_pdf('arancio.pdf')
            l1 = df.loc[[a]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
                                                                                                   axis=1).values
            l2 = df.loc[[b]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^A"),
                                                                                                     axis=1).values
            var='ORARIO INVERNALE'
        elif(num_day != 5):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/arancio.pdf',
                'arancio.pdf')
            df = read_pdf('arancio.pdf')
            l1 = df.loc[[a]].replace(r'.* (\d{2}:\d{2})', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
                                                                                                       axis=1).values
            l2 = df.loc[[b]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R"),
                                                                                                    axis=1).values
            var='ORARIO ESTIVO'
        else:
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/arancio.pdf',
                'arancio.pdf')
            df = read_pdf('arancio.pdf')
            l1 = df.loc[[a]].replace(r'.* (\d{2}:\d{2})', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
                                                                                                        axis=1).values
            l2 = df.loc[[b]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R"),
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
                    try:
                        dict[hour + 1]
                        delta_minute = list_min[0] - minute
                        tup.append(delta_minute)
                        delta_minute_next = dict[hour + 1][0] + 60 - minute
                        tup.append(delta_minute_next)
                    except:
                        delta_minute = 'Ultimo ed unico delle ore '+ str(hour) + ' tra ' + str(list_min[0] - minute) + ' min'
                        tup.append(delta_minute)
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
                    try:
                        dict[hour + 1]
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
                    except:
                        h=hour+2
                        while not h in dict.keys():
                            h+=1
                        M = min(dict[h])
                        delta_minute = 'Riprende alle ' + str(datetime.time(h, M).strftime("%H:%M"))
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
                if (hour > max(dict.keys())):
                    delta_minute = "Finish"  # 'NON CI SONO CORSE PER OGGI'
                    tup.append(delta_minute)
                else:
                    h=hour+1
                    while not h in dict.keys():
                        h += 1
                    M = min(dict[h])
                    delta_minute = 'Riprende alle ' + str(datetime.time(h, M).strftime("%H:%M"))
                    tup.append(delta_minute)
    else:
        var=''
        tup=[]
        delta_minute = 'Stop'
        tup.append(delta_minute)
    return tup,var,dir



def arancio_ritorno(direction,a,b):
    dir=direction

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


    if (num_day != 6 and num_day != 7):
        if (num_month < 5 or num_month > 9):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/invernale/arancio.pdf',
                'arancio.pdf')
            df = read_pdf('arancio.pdf')
            if(a == 4):
                l1 = df.loc[[a]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R|dal.*"),
                                                                                                       axis=1).values
            else:
                l1 = df.loc[[a]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R"),
                                                                                                        axis=1).values
            l2 = df.loc[[b]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*R.*"),
                                                                                                       axis=1).values
            var = 'ORARIO INVERNALE'
        elif (num_day != 5):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/arancio.pdf',
                'arancio.pdf')
            df = read_pdf('arancio.pdf')
            if(a == 7):
                l1 = df.loc[[a]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R|dal.*"),
                                                                                                       axis=1).values
            else:
                l1 = df.loc[[a]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R"),
                                                                                                           axis=1).values
            l2 = df.loc[[b]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
                                                                                                       axis=1).values
            var = 'ORARIO ESTIVO'
        else:
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/arancio.pdf',
                'arancio.pdf')
            df = read_pdf('arancio.pdf')
            if (a == 25):
                l1 = df.loc[[a]].replace(r'.* (\d{2}:\d{2})', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R|dal.*"),
                                                                                                        axis=1).values
            else:
                l1 = df.loc[[a]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=("^R"),
                                                                                                           axis=1).values
            l2 = df.loc[[b]].replace(r'.* (\d+:\d+)', r'\1', regex=True).dropna(axis='columns').filter(regex=(".*A.*"),
                                                                                                        axis=1).values
            var = 'VENERDI\' ESTIVO - ORARIO RIDOTTO'


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
                    try:
                        dict[hour + 1]
                        delta_minute = list_min[0] - minute
                        tup.append(delta_minute)
                        delta_minute_next = dict[hour + 1][0] + 60 - minute
                        tup.append(delta_minute_next)
                    except:
                        delta_minute = 'Ultimo ed unico delle ore '+ str(hour) + ' tra ' + str(list_min[0] - minute) + ' min'
                        tup.append(delta_minute)
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
                    try:
                        dict[hour + 1]
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
                    except:
                        h=hour+2
                        while not h in dict.keys():
                            h+=1
                        M = min(dict[h])
                        delta_minute = 'Riprende alle ' + str(datetime.time(h, M).strftime("%H:%M"))
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
                if (hour > max(dict.keys())):
                    delta_minute = "Finish"  # 'NON CI SONO CORSE PER OGGI'
                    tup.append(delta_minute)
                else:
                    h=hour+1
                    while not h in dict.keys():
                        h += 1
                    M = min(dict[h])
                    delta_minute = 'Riprende alle ' + str(datetime.time(h, M).strftime("%H:%M"))
                    tup.append(delta_minute)
    else:
        var=''
        tup=[]
        delta_minute = 'Stop'
        tup.append(delta_minute)
    return tup,var,dir




def rossa_andata(direction,nn):
    dir=direction
    def schedul(lis,nn):
        li0 = []
        li = []
        for i in lis:
            li0.append(re.findall(r'\d+:\d+', i))
            try:
                li0.remove([])
            except:
                li0
        for m in range(len(li0)):
            li.append(li0[m][nn])
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



        li = schedul(lis,nn)

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
                    try:
                        dict[hour + 1]
                        delta_minute = list_min[0] - minute
                        tup.append(delta_minute)
                        delta_minute_next = dict[hour + 1][0] + 60 - minute
                        tup.append(delta_minute_next)
                    except:
                        delta_minute = 'Ultimo ed unico delle ore '+ str(hour) + ' tra ' + str(list_min[0] - minute) + ' min'
                        tup.append(delta_minute)
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
                    try:
                        dict[hour + 1]
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
                    except:
                        h=hour+2
                        while not h in dict.keys():
                            h+=1
                        M = min(dict[h])
                        delta_minute = 'Riprende alle ' + str(datetime.time(h, M).strftime("%H:%M"))
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
                if (hour > max(dict.keys())):
                    delta_minute = "Finish"  # 'NON CI SONO CORSE PER OGGI'
                    tup.append(delta_minute)
                else:
                    h=hour+1
                    while not h in dict.keys():
                        h += 1
                    M = min(dict[h])
                    delta_minute = 'Riprende alle ' + str(datetime.time(h, M).strftime("%H:%M"))
                    tup.append(delta_minute)
    else:
        var=''
        tup=[]
        delta_minute = 'Stop'
        tup.append(delta_minute)
    return tup,var,dir




def rossa_ritorno(direction,mm):
    dir=direction
    def schedul(lis):
        li0 = []
        li = []
        for i in lis:
            li0.append(re.findall(r'\d+:\d+', i))
            try:
                li0.remove([])
            except:
                li0
        for m in range(len(li0)):
            li.append(li0[m][0])
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


    if(num_day != 6 and num_day != 7):
        if (num_month < 5 or num_month > 9):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/invernale/rossa.pdf',
                'rossa.pdf')
            df = read_pdf('rossa.pdf')

            ind = df.iloc[:, mm].dropna().str.contains('\)')
            idx = ind[ind].index.values
            if (idx.shape[0] > 1):
                lis = df.iloc[idx[0]:idx[1], mm].dropna().values
            else:
                lis = df.iloc[idx[0]:, mm].dropna().values

            var='ORARIO INVERNALE'
        elif(num_day != 5):
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/rossa.pdf',
                'rossa.pdf')
            df = read_pdf('rossa.pdf')

            ind = df.iloc[:, mm].dropna().str.contains('\)')
            idx = ind[ind].index.values
            if (idx.shape[0] > 1):
                lis = df.iloc[idx[0]:idx[1], mm].dropna().values
            else:
                lis = df.iloc[idx[0]:, mm].dropna().values

            var='ORARIO ESTIVO'
        else:
            urllib.request.urlretrieve(
                'https://myeni.eni.com/it_IT/common/documents/Eni_per_noi/trasporti/spostamenti_casa_lavoro/sdm/estivo/rossa.pdf',
                'rossa.pdf')
            df = read_pdf('rossa.pdf')

            ind = df.iloc[:, mm].dropna().str.contains('\)')
            idx = ind[ind].index.values
            if(idx.shape[0] > 2):
                lis = df.iloc[idx[1]:idx[2], mm].dropna().values
            else:
                lis = df.iloc[idx[-1]:, mm].dropna().values

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
                    try:
                        dict[hour + 1]
                        delta_minute = list_min[0] - minute
                        tup.append(delta_minute)
                        delta_minute_next = dict[hour + 1][0] + 60 - minute
                        tup.append(delta_minute_next)
                    except:
                        delta_minute = 'Ultimo ed unico delle ore '+ str(hour) + ' tra ' + str(list_min[0] - minute) + ' min'
                        tup.append(delta_minute)
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
                    try:
                        dict[hour + 1]
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
                    except:
                        h=hour+2
                        while not h in dict.keys():
                            h+=1
                        M = min(dict[h])
                        delta_minute = 'Riprende alle ' + str(datetime.time(h, M).strftime("%H:%M"))
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
                if (hour > max(dict.keys())):
                    delta_minute = "Finish"  # 'NON CI SONO CORSE PER OGGI'
                    tup.append(delta_minute)
                else:
                    h=hour+1
                    while not h in dict.keys():
                        h += 1
                    M = min(dict[h])
                    delta_minute = 'Riprende alle ' + str(datetime.time(h, M).strftime("%H:%M"))
                    tup.append(delta_minute)
    else:
        var=''
        tup=[]
        delta_minute = 'Stop'
        tup.append(delta_minute)
    return tup,var,dir















###ARANCIO ANDATA
@app.route('/arancio_andata/Ar_anda_Stazione')
def index_Ar_anda_Stazione():
    if (num_month < 5 or num_month > 9):
        out_def = arancio_andata('Stazione F.F.S.S.',0,11)
    elif (num_day != 5):
        out_def = arancio_andata('Stazione F.F.S.S.', 1, 15)
    else:
        out_def = arancio_andata('Stazione F.F.S.S.', 19, 34)

    return render_template("arancia_A_R.html",Dir='Direzione Bolgiano',tup=out_def[0], var=out_def[1], direction=out_def[2])



@app.route('/arancio_andata/Ar_anda_Emilia')
def index_Ar_anda_Emilia():
    if (num_month < 5 or num_month > 9):
        out_def = arancio_andata('Via Emilia (5°Pu)',1,10)
    elif (num_day != 5):
        out_def = arancio_andata('Via Emilia (5°Pu)', 3, 14)
    else:
        out_def = arancio_andata('Via Emilia (5°Pu)', 21, 33)
    return render_template("arancia_A_R.html",Dir='Direzione Bolgiano', tup=out_def[0], var=out_def[1], direction=out_def[2])


@app.route('/arancio_andata/Ar_anda_Agadir')
def index_Ar_anda_Agadir():
    if (num_month < 5 or num_month > 9):
        out_def = arancio_andata('Via Agadir (Eniservizi)',2,9)
    elif (num_day != 5):
        out_def = arancio_andata('Via Agadir (Eniservizi)', 5, 12)
    else:
        out_def = arancio_andata('Via Agadir (Eniservizi)', 23, 31)
    return render_template("arancia_A_R.html",Dir='Direzione Bolgiano', tup=out_def[0], var=out_def[1], direction=out_def[2])


###ARANCIA RITORNO

@app.route('/arancio_ritorno/Ar_rit_Bolgiano')
def index_Ar_rit_Bolgiano():
    if (num_month < 5 or num_month > 9):
        out_def = arancio_ritorno('Via Maritano (Lab. Bolgiano)',4,8)
    elif (num_day != 5):
        out_def = arancio_ritorno('Via Maritano (Lab. Bolgiano)', 7, 10)
    else:
        out_def = arancio_ritorno('Via Maritano (Lab. Bolgiano)', 25, 29)
    return render_template("arancia_A_R.html",Dir='Direzione Stazione', tup=out_def[0], var=out_def[1], direction=out_def[2])

@app.route('/arancio_ritorno/Ar_rit_Agadir')
def index_Ar_rit_Agadir():
    if (num_month < 5 or num_month > 9):
        out_def = arancio_ritorno('Via Agadir (EniServizi)',2,9)
    elif (num_day != 5):
        out_def = arancio_ritorno('Via Agadir (EniServizi)', 5, 12)
    else:
        out_def = arancio_ritorno('Via Agadir (EniServizi)', 23, 31)
    return render_template("arancia_A_R.html",Dir='Direzione Stazione', tup=out_def[0], var=out_def[1], direction=out_def[2])

@app.route('/arancio_ritorno/Ar_rit_Emilia')
def index_Ar_rit_Emilia():
    if (num_month < 5 or num_month > 9):
        out_def = arancio_ritorno('Via Emilia (5°Pu)',1,10)
    elif (num_day != 5):
        out_def = arancio_ritorno('Via Emilia (5°Pu)', 3, 14)
    else:
        out_def = arancio_ritorno('Via Emilia (5°Pu)', 21, 33)
    return render_template("arancia_A_R.html",Dir='Direzione Stazione', tup=out_def[0], var=out_def[1], direction=out_def[2])


###ROSSA ANDATA

@app.route('/rossa_andata/Ros_anda_MM3')
def index_Ros_anda_MM3():
    if (num_month < 5 or num_month > 9):
        out_def = rossa_andata('MM3 - Via Marignano',0)
    elif (num_day != 5):
        out_def = rossa_andata('MM3 - Via Marignano',0)
    else:
        out_def = rossa_andata('MM3 - Via Marignano',0)

    return render_template("rossa_A_R.html",Dir='Direzione Torre E-Tower',tup=out_def[0], var=out_def[1], direction=out_def[2])



@app.route('/rossa_andata/Ros_anda_Vanoni')
def index_Ros_anda_Vanoni():
    if (num_month < 5 or num_month > 9):
        out_def = rossa_andata('P.zza Vanoni',1)
    elif (num_day != 5):
        out_def = rossa_andata('P.zza Vanoni',1)
    else:
        out_def = rossa_andata('P.zza Vanoni',1)
    return render_template("rossa_A_R.html",Dir='Direzione Torre E-Tower', tup=out_def[0], var=out_def[1], direction=out_def[2])


@app.route('/rossa_andata/Ros_anda_Emilia')
def index_Ros_anda_Emilia():
    if (num_month < 5 or num_month > 9):
        out_def = rossa_andata('Via Emilia (5°Pu)',2)
    elif (num_day != 5):
        out_def = rossa_andata('Via Emilia (5°Pu)',2)
    else:
        out_def = rossa_andata('Via Emilia (5°Pu)',2)
    return render_template("rossa_A_R.html",Dir='Direzione Torre E-Tower', tup=out_def[0], var=out_def[1], direction=out_def[2])

###ROSSA RITORNO

@app.route('/rossa_ritorno/Ros_rit_Torre')
def index_Ros_rit_Torre():
    if (num_month < 5 or num_month > 9):
        out_def = rossa_ritorno('Torre E-Tower',0)
    elif (num_day != 5):
        out_def = rossa_ritorno('Torre E-Tower',0)
    else:
        out_def = rossa_ritorno('Torre E-Tower',0)

    return render_template("rossa_A_R.html",Dir='Direzione MM3',tup=out_def[0], var=out_def[1], direction=out_def[2])



@app.route('/rossa_ritorno/Ros_rit_Emilia')
def index_Ros_rit_Emilia():
    if (num_month < 5 or num_month > 9):
        out_def = rossa_ritorno('Via Emilia (5°Pu)',1)
    elif (num_day != 5):
        out_def = rossa_ritorno('Via Emilia (5°Pu)',1)
    else:
        out_def = rossa_ritorno('Via Emilia (5°Pu)',1)
    return render_template("rossa_A_R.html",Dir='Direzione MM3', tup=out_def[0], var=out_def[1], direction=out_def[2])


@app.route('/rossa_ritorno/Ros_rit_Vanoni')
def index_Ros_rit_Vanoni():
    if (num_month < 5 or num_month > 9):
        out_def = rossa_ritorno('P.zza Vanoni (1°- 2°Pu)',2)
    elif (num_day != 5):
        out_def = rossa_ritorno('P.zza Vanoni (1°- 2°Pu)',2)
    else:
        out_def = rossa_ritorno('P.zza Vanoni (1°- 2°Pu)',2)
    return render_template("rossa_A_R.html",Dir='Direzione MM3', tup=out_def[0], var=out_def[1], direction=out_def[2])



@app.route('/arancio_andata')
def index_arancia_andata():
    return render_template('arancio_andata.html')

@app.route('/arancio_ritorno')
def index_arancia_ritorno():
    return render_template('arancio_ritorno.html')

@app.route('/rossa_andata')
def index_rossa_andata():
    return render_template('rossa_andata.html')

@app.route('/rossa_ritorno')
def index_rossa_ritorno():
    return render_template('rossa_ritorno.html')


@app.route('/')
def index():
    return render_template('index.html')




if __name__ == '__main__':
    app.run(use_reloader = True,debug=True)