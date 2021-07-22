import geopandas as gpd
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine
from geoalchemy2 import Geometry, WKTElement

import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DB_HOST = os.environ.get("HOST")
DB_USER = os.environ.get("USER")
DB_NAME = os.environ.get("DBNAME")
DB_PORT = os.environ.get("PORT")
DATABASE_PASSWORD = os.environ.get("PASSWORD")

engine = create_engine(
    "postgresql://geonode:PASSWORD@HOST:PORT/DATABASE")
stations = gpd.read_file(
    'shapefile/estacoes_telemetricas.shp', encoding='utf-8')

stations['geom'] = stations['geometry'].apply(
    lambda x: WKTElement(x.wkt, srid=4326))

stations.drop('geometry', 1, inplace=True)

forecast = pd.read_csv('hidroforecast.csv', sep=',')

newstations = stations.sort_values("code", ascending=True)
newstations = newstations.reset_index(drop=True)

newforecast = forecast.sort_values("Estacao", ascending=True)
newforecast = newforecast.reset_index(drop=True)

newstations['qsup'] = newforecast['Qsup']
newstations['status'] = newforecast['Status']
newstations['isforecast'] = newforecast['isForecast']
newstations['forecast'] = newforecast['VazaoMinPrev']

newstations['code'] = newstations['code'].astype(int)

dtype = {
    'code': sqlalchemy.types.Integer,
    'drainarea': sqlalchemy.types.Float,
    'river': sqlalchemy.types.String,
    'lat': sqlalchemy.types.Float,
    'lon': sqlalchemy.types.Float,
    'qsup': sqlalchemy.types.Float,
    'status': sqlalchemy.types.String,
    'forecast': sqlalchemy.types.Float,
    'isforecast': sqlalchemy.types.String,
    'geom':  Geometry('POINT', srid=4326)
}

newstations.to_sql(name='estacoes_telemetricas',
                   con=engine,
                   if_exists='replace',
                   schema='vector',
                   index=False,
                   dtype=dtype)


print('Send forecast data to postgis')
