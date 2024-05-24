import configparser as parser
import itertools

import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation
from prophet.diagnostics import performance_metrics

from . import electricity
from . import sql

properties = parser.ConfigParser()
properties.read('./config.ini')

hourly_backup = properties['TABLE']['hourly_backup']
hourly_predict = properties['TABLE']['hourly_predict']
daily_backup = properties['TABLE']['daily_backup']
daily_predict = properties['TABLE']['daily_predict']

def forecast(param_grid, org, query, channel, channel_id):
    organization_id = org.organization_id

    df_usage = electricity.get_usage(org, query)
    df_usage = electricity.format_w(df_usage)

    if df_usage.empty or electricity.is_constant(df_usage, daily_predict, organization_id, channel_id):
        return

    outlier_value = electricity.find_outlier(df_usage, 'y')
    df_train = electricity.set_outlier(df_usage, outlier_value)

    param_grid = find_param(org, df_train, channel, param_grid)
    model = modeling(org, param_grid, df_train)

    df_daily_forecast = daily_forecast(model, 24*60, '1h', outlier_value)
    sql.save(df_daily_forecast, daily_predict, organization_id, channel_id)

    df_hourly_forecast = hourly_forecast(model, 24*3, '1h', outlier_value)
    sql.save(df_hourly_forecast, hourly_predict, organization_id, channel_id)

def modeling(org, params, df):
    model = Prophet(holidays=get_weekend(org), **params)
    model.add_country_holidays(country_name='KR')
    model.fit(df)

    return model

def hourly_forecast(model, periods, freq, outlier_value):
    future = model.make_future_dataframe(periods=periods, freq=freq, include_history=False)
    electricity.set_outlier(future, outlier_value)
    forecast = model.predict(future)

    df = forecast[['ds', 'yhat']].copy()
    df = df.round(1)
    df = df.rename(columns={'yhat':'kwh', 'ds':'time'})

    return df

def daily_forecast(model, periods, freq, outlier_value):
    df = hourly_forecast(model, periods, freq, outlier_value)
    df.loc[:,'time'] = df['time'].dt.strftime('%Y-%m-%d 00:00:00')
    df = pd.DataFrame(df.groupby(df.time)['kwh'].sum())
    df = df.round(1)
    df = df.reset_index()

    return df

def get_weekend(org):
    saturday_dates = pd.date_range(start=org.start_time, end=org.end_time, freq='W-SAT')

    holidays = pd.DataFrame({
        'holiday': 'weekend',
        'ds': saturday_dates,
        'lower_window': 0,
        'upper_window': 1
    })

    return holidays

def get_best_param(org, df, param_grid):
    all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
    rmses = []

    for params in all_params:
        model = modeling(org, params, df)
        df_cv = cross_validation(model, horizon='1 days', parallel="processes")
        df_p = performance_metrics(df_cv, rolling_window=1)
        rmses.append(df_p['rmse'].values[0])

    tuning_results = pd.DataFrame(all_params)
    tuning_results['rmse'] = rmses

    best_params = all_params[np.argmin(rmses)]

    return best_params

def find_param(org, df, channel, param):
    if channel == 'main':
        return get_best_param(org, df, param)

    param = {
        'growth':'logistic'
    }

    return param
