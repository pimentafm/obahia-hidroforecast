import xml.etree.ElementTree as ET
import requests
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

stations = pd.read_csv('utils/lista_estacoes.csv', sep=',')

today = date(2021, 6, 1)  # date.today()

modeldates = [date(2021, 5, 1), date(2021, 6, 1), date(2021, 7, 1)]

if today in modeldates:
    a_month = relativedelta(months=1)
    start_date = (today - a_month).strftime('%d/%m/%Y')
    end_date = today.strftime('%d/%m/%Y')
else:
    print('Some error was occurred!')


for i in stations['id']:
    telemetryXML = requests.get('http://telemetriaws1.ana.gov.br/ServiceANA.asmx/DadosHidrometeorologicos?CodEstacao=' +
                                str(i)+'&DataInicio='+start_date+'&DataFim='+end_date)
    tree = ET.fromstring(telemetryXML.text)
    aa = tree.getchildren()[1]
    bb = aa.getchildren()[0]

    df = pd.DataFrame(
        columns=['CodEstacao', 'DataHora', 'Vazao', 'Nivel', 'Chuva'])

    for dados in bb.findall('DadosHidrometereologicos'):
        codEstacao = dados.find('CodEstacao')
        data = dados.find('DataHora')
        vazao = dados.find('Vazao')
        nivel = dados.find('Nivel')
        chuva = dados.find('Chuva')

        new_row = {
            'CodEstacao': codEstacao.text,
            'DataHora': data.text,
            'Data': data.text.split(' ')[0],
            'Hora': data.text.split(' ')[1],
            'Vazao': vazao.text,
            'Nivel': nivel.text,
            'Chuva': chuva.text
        }

        df = df.append(new_row, ignore_index=True)

    df.to_csv('stations/' + str(i) + '.csv', sep=',')


print('Telemetry data was downloaded')
