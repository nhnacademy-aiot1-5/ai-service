import itertools
from datetime import datetime

import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation
from prophet.diagnostics import performance_metrics

from . import electricity


def get_weekend(org):
    saturday_dates = pd.date_range(start=org.start_time, end=org.end_time, freq='W-SAT')

    holidays = pd.DataFrame({
        'holiday': 'weekend',
        'ds': saturday_dates,
        'lower_window': 0,
        'upper_window': 1
    })

    return holidays

def run(org, df, param_grid):
    all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
    rmses = []

    for params in all_params:
        m = Prophet(holidays=get_weekend(org), **params)
        m.add_country_holidays(country_name='KR')
        m.fit(df)

        df_cv = cross_validation(m, horizon='1 days', parallel="processes")
        df_p = performance_metrics(df_cv, rolling_window=1)
        rmses.append(df_p['rmse'].values[0])

    tuning_results = pd.DataFrame(all_params)
    tuning_results['rmse'] = rmses

    best_params = all_params[np.argmin(rmses)]

    model = Prophet(holidays=get_weekend(org), **best_params)
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

def constant(value):
    df = pd.DataFrame(columns=['time', 'kwh'])
    df['time'] = pd.date_range(start=datetime.now(), periods=30 ,freq='D')
    df.loc[:,'time'] = df['time'].dt.strftime('%Y-%m-%d 00:00:00')
    df['kwh'] = value

    return df
