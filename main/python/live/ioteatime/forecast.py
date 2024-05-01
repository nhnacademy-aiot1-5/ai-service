from ai_service.main import forecast

backup_table = 'predict_electricity_consumption_backup'
predict_table = 'predict_electricity_consumption'

forecast(predict_table, backup_table)