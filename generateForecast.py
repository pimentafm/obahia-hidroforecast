import pandas as pd
from pandas import DataFrame
import numpy as np
from datetime import date
from dateutil.relativedelta import relativedelta

estacao = pd.read_csv('utils/lista_estacoes.csv', sep=',')

vazao_output = DataFrame(index=[x for x in range(len(estacao.id))], columns=[
                         'Estacao', 'Localizacao', 'Qsup', 'VazaoMinPrev', 'Status', 'isForecast'])

now = date(2021, 6, 1)

modeldates = [date(2021, 5, 1), date(2021, 6, 1), date(2021, 7, 1)]

if now in modeldates:
    a_month = relativedelta(months=1)
    start_date = (now - a_month).strftime('%d/%m/%Y')
    end_date = now.strftime('%d/%m/%Y')
else:
    print('Some error was occurred!')

d0 = date(now.year, 1, 1)

d2 = date(now.year, 10, 31)

a_month = relativedelta(months=1)

dt1 = now - relativedelta(days=1)
dt = dt1 - d0
dt2 = d2 - dt1

mes_prev = now.month - 1

for est in range(len(estacao.id)):

    # ler o arquivo e mostrar a separação
    dados_telemetria = pd.read_csv(
        'filtrado/'+str(estacao.id[est])+'_filtrado.csv', sep=';', encoding='latin-1')
    dados_telemetria = pd.DataFrame(dados_telemetria)
    dados_telemetria['data'] = pd.to_datetime(dados_telemetria['data'])
    dados_telemetria['dia'] = dados_telemetria['data'].dt.dayofyear
    dados_telemetria['mes'] = dados_telemetria['data'].dt.month
    dados_telemetria.drop(
        dados_telemetria.loc[dados_telemetria['vazao diaria'] == 0].index, inplace=True)

    alfa_pond = estacao.alfa[est]
    q_noventa = estacao.q90[est]
    vsup = estacao.vsup[est]

    dados_mes_prev = dados_telemetria.loc[(
        dados_telemetria['mes'] == mes_prev)]
    dados_mes_prev.drop(
        dados_mes_prev.loc[dados_mes_prev['vazao diaria'] == 0].index, inplace=True)
    dados_mes_prev.drop(dados_mes_prev.loc[dados_mes_prev['vazao diaria']
                                           != dados_mes_prev['vazao diaria'].min()].index, inplace=True)
    dados_mes_prev.drop(
        dados_mes_prev.loc[dados_mes_prev['dia'] != dados_mes_prev['dia'].max()].index, inplace=True)

    dia_valor = np.array(dados_mes_prev['dia'])

    if not dia_valor:
        vazao_output['Estacao'][est] = str(estacao.id[est])
        vazao_output['Localizacao'][est] = str(estacao.localizacao[est])
        vazao_output['Qsup'][est] = str(estacao.vsup[est])
        vazao_output['VazaoMinPrev'][est] = np.nan
        vazao_output['Status'][est] = 'Sem previsão'
        vazao_output['isForecast'][est] = 'no'
    else:
        quantidade_dias = dt.days - int(dia_valor) + dt2.days

        dia = {}
        b = 0
        for i in range(quantidade_dias):
            dia[str(b)] = dia_valor + i
            b = b + 1

        dia = pd.DataFrame.from_dict(
            dia, orient='index', columns=['dia_do_ano'])

        qo = np.array(dados_mes_prev['vazao diaria'])
        to = np.array(dados_mes_prev['dia'])
        valor_mask = to[0]
        dado_selecionado_mask = dados_mes_prev.loc[(
            dados_mes_prev['mes'] == mes_prev)]

        dado_selecionado_mask = dado_selecionado_mask.mask(
            dado_selecionado_mask['dia'] < valor_mask)
        dado_final = pd.concat([dia, dado_selecionado_mask])

        dia_periodo = dia['dia_do_ano']
        vazao_calculada = {}

        k = 0
        for dias in range(len(dia_periodo)):
            vazao_calculada[str(k)] = (
                qo[0]*(np.exp((alfa_pond)*(dia_periodo[dias]-to[0]))))
            k = k+1

        vazao_feita = pd.DataFrame.from_dict(
            vazao_calculada, orient='index', columns=['vazao'])
        vazao_minima_prevista = vazao_feita["vazao"].iloc[-1]

        if(vsup <= 0.70*vazao_minima_prevista):
            status = 'Baixo'
        elif (vsup > 0.70*vazao_minima_prevista and vsup <= vazao_minima_prevista):
            status = 'Moderado'
        else:
            status = "Alto"

        vazao_output['Estacao'][est] = str(estacao.id[est])
        vazao_output['Localizacao'][est] = str(estacao.localizacao[est])
        vazao_output['Qsup'][est] = str(estacao.vsup[est])
        vazao_output['VazaoMinPrev'][est] = vazao_minima_prevista
        vazao_output['Status'][est] = status
        vazao_output['isForecast'][est] = 'yes'

    vazao_output.to_csv('hidroforecast.csv', sep=',')


print('End forecast')
