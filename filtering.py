import pandas as pd
from pandas import DataFrame
import numpy as np
from numpy import savetxt

estacao = pd.read_csv('utils/lista_estacoes.csv', sep=',')

for est in range(len(estacao.id)):
    print('Filtering ' + str(estacao.id[est]))

    # ler o arquivo e mostrar a separação
    dado_tele = pd.read_csv(
        'stations/'+str(estacao.id[est])+'.csv', sep=',', encoding='latin-1')
    dado_tele = pd.DataFrame(dado_tele)

    dado_tele = DataFrame(dado_tele, columns=[
                          'DataHora', 'Data', 'Hora', 'Chuva', 'Nivel', 'Vazao'])

    dado_tele['data'] = pd.to_datetime(dado_tele['Data'])

    dado_tele['dia_ano'] = dado_tele['data'].dt.dayofyear
    dado_tele['dia'] = dado_tele['data'].dt.dayofyear
    dado_tele['mes'] = dado_tele['data'].dt.month

    t = len(dado_tele['data'])
    i = len(dado_tele['dia'])
    # nivel0=np.array(dado_tele['nivel'])
    nivel0 = dado_tele['Nivel'].to_numpy()
    chuva0 = dado_tele['Chuva'].to_numpy()
    nivel1 = np.full(t, np.nan)

    for time in range(1, t):
        if not (np.isnan(nivel0[time]) or np.isnan(nivel0[time-1])):
            if abs((nivel0[time] - nivel0[time-1])/nivel0[time-1]) > 0.1:
                nivel1[time] = np.nan
            else:
                nivel1[time] = nivel0[time]

    hora = (dado_tele['Hora']).to_numpy()
    vazao = dado_tele['Vazao'].to_numpy()
    n1_perc = np.full(t, 1.0)
    av = np.full(t, 0.0)
    dv = np.full(t, 0.0)
    mm = np.full(t, 0.0)
    mm2 = np.full(t, 0.0)
    comp = np.full(t, 0.0)
    nivel2 = np.full(t, 0.0)
    q2 = np.full(t, 0.0)
    q_diario = np.full(t, 0.0)
    vazao_diaria = DataFrame(
        columns=['data', 'hora', 'chuva', 'nivel', 'vazao diaria'])

    for time in range(t-97):
        count = 0
        soma = 0

        for n in range(96):
            if not(np.isnan(nivel1[time+n])):
                count = count + 1
                soma = soma + nivel1[time+n]

        if (hora[time] == '00:00:00'):
            if(count != 0):
                n1_perc[time] = (count/96)
                av[time] = soma/count
            else:
                n1_perc[time] = np.nan
                av[time] = np.nan

            dv[time] = np.nanstd(nivel1[time:time+95])
        else:
            n1_perc[time] = (n1_perc[time-1])
            av[time] = av[time-1]
            dv[time] = dv[time-1]

        mm[time] = av[time]-2*dv[time]
        mm2[time] = av[time]+2*dv[time]

        if (nivel1[time] < mm2[time] and nivel1[time] > mm[time]):
            comp[time] = 1
        else:
            comp[time] = 0

        if (n1_perc[time] < 0.75):
            nivel2[time] = np.nan
        else:
            if(comp[time] == 1):
                nivel2[time] = nivel1[time]
            else:
                nivel2[time] = np.nan

        if not(np.isnan(nivel2[time])):
            q2[time] = vazao[time]
        else:
            q2[time] = np.nan

    for time in range(t-97):
        if (hora[time] == '00:00:00'):
            q2[time:time+95][q2[time:time+95] == 0] = np.nan

            q_diario[time] = np.nanmean(q2[time:time+95])

            # if(q_diario[time] < 30):
            #     print(time, q_diario[time], q2[time:time+95])

            vazao_diaria['data'] = dado_tele['data']
            vazao_diaria['hora'] = pd.Series(hora)
            vazao_diaria['chuva'] = pd.Series(chuva0)
            vazao_diaria['nivel'] = pd.Series(nivel0)
            vazao_diaria['vazao diaria'] = pd.Series(q_diario)

            vazao_diaria.to_csv(
                'filtrado/'+str(estacao.id[est])+'_filtrado000000.csv', sep=';')

        else:
            q_diario[time] = q_diario[time-1]

    vazao_diaria['data'] = dado_tele['data']
    vazao_diaria['hora'] = pd.Series(hora)
    vazao_diaria['chuva'] = pd.Series(chuva0)
    vazao_diaria['nivel'] = pd.Series(nivel0)
    vazao_diaria['vazao diaria'] = pd.Series(q_diario)

    vazao_diaria.drop(
        vazao_diaria[(vazao_diaria['hora'] != '00:00:00')].index, inplace=True)
    vazao_diaria.to_csv(
        'filtrado/'+str(estacao.id[est])+'_filtrado.csv', sep=';')
