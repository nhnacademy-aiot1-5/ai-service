import sql
import train
import outlier
import electricity
import redis_r as redis

backup_table = 'predict_electricity_consumption_backup'
predict_table = 'predict_electricity_consumption'

outlier_table = 'hourly_outlier_test'

def set_outlier():
    df = electricity.get_hourly_electricity()
    df_hourly_outlier = outlier.find_hourly_outlier(df)

    redis.set(outlier_table, df_hourly_outlier)

def forecast():
    sql.backup(predict_table, backup_table)

    df_train = electricity.get_hourly_usage()
    df_train = outlier.set_outlier(df_train)

    model = train.run(df_train)
    df_forecast = train.forecast(model)
    sql.insert(df_forecast, predict_table)

set_outlier()
forecast()