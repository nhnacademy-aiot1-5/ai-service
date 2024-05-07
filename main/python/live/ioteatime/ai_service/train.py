import itertools
import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation
from prophet.diagnostics import performance_metrics
from . import influx

def get_weekend():
    saturday_dates = pd.date_range(start=influx.start_time, end=influx.end_time, freq='W-SAT')

    holidays = pd.DataFrame({
        'holiday': 'weekend',
        'ds': saturday_dates,
        'lower_window': 0,
        'upper_window': 1
    })

    return holidays

def run(df, param_grid):
    all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
    rmses = []

    for params in all_params:
        m = Prophet(holidays=get_weekend(), **params)
        m.add_country_holidays(country_name='KR')
        m.fit(df)

        df_cv = cross_validation(m, horizon='1 days', parallel="processes")
        df_p = performance_metrics(df_cv, rolling_window=1)
        rmses.append(df_p['rmse'].values[0])

    tuning_results = pd.DataFrame(all_params)
    tuning_results['rmse'] = rmses

    best_params = all_params[np.argmin(rmses)]

    model = Prophet(holidays=get_weekend(), **best_params)
    model.add_country_holidays(country_name='KR')
    model.fit(df)
    return model

def forecast(model, periods, freq):
    future = model.make_future_dataframe(periods=periods, freq=freq, include_history=False)
    forecast = model.predict(future)

    df = forecast[['ds', 'yhat']].copy()
    df.loc[:,'ds'] = df['ds'].dt.strftime('%Y-%m-%d 00:00:00')
    df = df.rename(columns={'yhat':'kwh', 'ds':'time'})

    return df

def daily_forecast(model, periods, freq):
    df = forecast(model, periods, freq)
    df = pd.DataFrame(df.groupby(df.time)['kwh'].sum())
    df = df.round(2)
    df = df.reset_index()
    return df

