#!/bin/bash

python3.7 -W ignore downloadTelemetryStations.py
python3.7 -W ignore filtering.py
python3.7 -W ignore generateForecast.py
python3.7 -W ignore shp2postgis.py
