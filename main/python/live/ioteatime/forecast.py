from ai_service.main import forecast

backup_table = 'predict_electricity_consumption_backup'
predict_table = 'predict_electricity_consumption'

param_grid = {
    'changepoint_prior_scale': [0.001, 0.01, 0.05, 0.1, 0.5],
    'seasonality_prior_scale': [0.01, 0.1, 1.0, 5.0, 10.0],
    'holidays_prior_scale': [0.01, 0.1, 5.0, 10.0]
}

forecast(predict_table, backup_table, param_grid)