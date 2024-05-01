import itertools
import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation
from prophet.diagnostics import performance_metrics

def run(df, param_grid):
    all_params = [dict(zip(param_grid.keys(), v)) for v in itertools.product(*param_grid.values())]
    rmses = []

    for params in all_params:
        m = Prophet(growth='logistic', **params)
        m.add_country_holidays(country_name='KR')
        m.fit(df)

        df_cv = cross_validation(m, horizon='1 days', parallel="processes")
        df_p = performance_metrics(df_cv, rolling_window=1)
        rmses.append(df_p['rmse'].values[0])

    tuning_results = pd.DataFrame(all_params)
    tuning_results['rmse'] = rmses

    best_params = all_params[np.argmin(rmses)]

    model = Prophet(**best_params)
    model.add_country_holidays(country_name='KR')
    model.fit(df)

    return model

def forecast(model):
    future = model.make_future_dataframe(periods=30*24, freq='1h', include_history=False)
    forecast = model.predict(future)

    df = forecast[['ds', 'yhat']]
    df.loc[:, 'ds'] = df['ds'].dt.strftime('%Y-%m-%d 00:00:00')
    df = pd.DataFrame(df.groupby(df.ds)['yhat'].sum())
    df = df.round(2)
    df = df.reset_index()
    df.rename(columns={'yhat':'kwh', 'ds':'time'} ,inplace=True)
    return df