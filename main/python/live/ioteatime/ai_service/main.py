import sql
import redis_r as redis

from . import train
from . import outlier
from . import electricity

def set_outlier(outlier_table):
    df = electricity.get_hourly_electricity()
    df_hourly_outlier = outlier.find_hourly_outlier(df)

    redis.set(outlier_table, df_hourly_outlier)

def forecast(predict_table, backup_table, param_grid):
    sql.backup(predict_table, backup_table)

    df_train = electricity.get_hourly_usage()
    df_train = outlier.set_outlier(df_train)

    model = train.run(df_train, param_grid)
    df_forecast = train.forecast(model)
    sql.insert(df_forecast, predict_table)
