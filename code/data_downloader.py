#!/usr/bin/env python3

# Note: install requested library
# pip install openmeteo_requests requests_cache retry_requests rich

import openmeteo_requests
import requests_cache
import pandas as pd
import numpy as np
from retry_requests import retry
from datetime import datetime, timezone
from rich.progress import track
import time
import os
from dotenv import load_dotenv
import argparse

utc_tz = timezone.utc
api_key = None

def get_weather(df: pd.DataFrame, lat, long, method='forecast', type='weather', start_date=datetime.now(utc_tz), end_date=datetime.now(utc_tz)):
    cache_session = requests_cache.CachedSession('.cache', expire_after = 86400)
    retry_session = retry(cache_session, retries = 10, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session)

    # define request payload
    params = {
        "latitude": lat,
        "longitude": long,
    }
    if type == 'weather':
        param_columns = {
            'hourly': ['temperature_2m', 'relative_humidity_2m', 'dew_point_2m', 'pressure_msl', 'surface_pressure', 'visibility', 'wind_speed_10m', 'wind_speed_80m', 'wind_speed_100m', 'wind_speed_120m', 'wind_speed_180m', 'wind_direction_10m', 'wind_direction_80m', 'wind_direction_100m', 'wind_direction_120m', 'wind_direction_180m', 'temperature_80m', 'temperature_120m', 'temperature_180m'], 
            'models': 'best_match'}
    elif type == 'air_quality':
        param_columns = {
            'hourly': ['pm10', 'pm2_5', 'carbon_monoxide', 'carbon_dioxide', 'nitrogen_dioxide', 'sulphur_dioxide', 'ozone', 'dust', 'uv_index'],
            'domains': 'cams_global'
        }
    else:
        return df

    # define api url
    if type == 'weather':
        if method == 'forecast':
            if api_key:
                url = 'https://customer-api.open-meteo.com/v1/forecast'
            else:
                url = 'https://api.open-meteo.com/v1/forecast'
        else:
            if api_key:
                url = 'https://customer-archive-api.open-meteo.com/v1/archive'
            else:
                url = 'https://archive-api.open-meteo.com/v1/archive'
    elif type == 'air_quality':
        if api_key:
            url = "https://customer-air-quality-api.open-meteo.com/v1/air-quality"
        else:
            url = 'https://air-quality-api.open-meteo.com/v1/air-quality'
    # set request date
    params['start_date'] = start_date.strftime(r'%Y-%m-%d')
    params['end_date'] = end_date.strftime(r'%Y-%m-%d')
    # set api key, if any
    if api_key:
        params['apikey'] = api_key
    params = {**params, **param_columns}
    
    responses = []
    # loop until can get response
    while True: 
        try:
            # call the api
            responses = openmeteo.weather_api(url, params=params)
            # got response, break the loop
            if responses:
                response = responses[0]
                break
        # wait when get an error and retry in 1 minute
        except Exception:
            time.sleep(60)
            
    # extract hour data
    hourly = response.Hourly()
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
        end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = hourly.Interval()),
        inclusive = "left"
    )}
    hourly_data['latitude'] = params['latitude']
    hourly_data['longitude'] = params['longitude']
    # copy response data
    for i, param in enumerate(params['hourly']):
        hourly_data[param] = hourly.Variables(i).ValuesAsNumpy()
    sum_df = pd.concat([df, pd.DataFrame(data=hourly_data)]).dropna(how='all').reset_index(drop=True)
    sum_df['type'] = type

    return sum_df

def scan_region(start_date, end_date, start_lat, start_long, end_lat, end_long, method='forecast', resolution=0.01):
    sum_weather_df = pd.DataFrame()
    sum_air_quality_df = pd.DataFrame()
    # generate coordination list
    locs = []
    for lat in np.arange(start_lat, end_lat+resolution, resolution):
        for long in np.arange(start_long, end_long+resolution, resolution):
            locs.append([lat, long])
    # loop through coordinations to get data at that point
    for lat, long in track(locs):
        lat = round(lat, 4)
        long = round(long, 4)
        sum_weather_df = get_weather(sum_weather_df, lat=lat, long=long, 
                                     method=method, type='weather', 
                                     start_date=start_date, end_date=end_date)
        sum_air_quality_df = get_weather(sum_air_quality_df, lat=lat, long=long, 
                                         method=method, type='air_quality', 
                                         start_date=start_date, end_date=end_date)
    # save result to file
    save_data(sum_weather_df)
    save_data(sum_air_quality_df)

def save_data(data: pd.DataFrame):
    if 'type' not in data:
        return
    type = data.loc[:, 'type'].unique()
    if type.size == 0:
        return
    type = type[0]
    # generate file name
    start_date = data['date'].min()
    end_date = data['date'].max()
    lat_loc = f'{data["latitude"].min():.0f}' + 't' + f'{data["latitude"].max():.0f}'
    long_loc = f'{data["longitude"].min():.0f}' + 't' + f'{data["longitude"].max():.0f}'
    file = f"../data/environment/{type}-{lat_loc}_{long_loc}_{start_date.strftime(r'%Y%m%d')}_{end_date.strftime(r'%Y%m%d')}.csv"
    # save to file
    data.sort_values(by=['date', 'latitude', 'longitude'], inplace=True)
    data.to_csv(file, index=False)

if __name__ == '__main__':
    # load api key, if any
    load_dotenv()
    api_key = os.getenv('OPENMETEO_API_KEY')
    
    # get default start and end date
    def_end_date = datetime.now(utc_tz).replace(hour=23, minute=59, second=59, microsecond=0)
    def_start_date = def_end_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    parser = argparse.ArgumentParser(description='Environmental data downloader')
    parser.add_argument('--source', help='data source', choices=['forecast', 'archive'], default='forecast')
    parser.add_argument('--start-date', help='start date, e.g. "2024-12-01 00:00:00+00:00"', default=def_start_date.isoformat())
    parser.add_argument('--end-date', help='end date, e.g. "2024-12-01 23:59:59+00:00"', default=def_end_date.isoformat())
    parser.add_argument('--loc-step', help='coordinate step size, e.g. 0.15', type=float, default=0.15)
    parser.add_argument('--start-lat', help='start latitude, e.g. 14.0', type=float)
    parser.add_argument('--end-lat', help='end latitude, e.g. 15.5', type=float)
    parser.add_argument('--start-long', help='start longitude, e.g. 100.0', type=float)
    parser.add_argument('--end-long', help='end longitude, e.g. 101.0', type=float)
    
    args = parser.parse_args()
    #exit
    scan_region(start_date=datetime.fromisoformat(args.start_date), 
             end_date=datetime.fromisoformat(args.end_date), 
             start_lat=args.start_lat, start_long=args.start_long, end_lat=args.end_lat, end_long=args.end_long, resolution=args.loc_step)
