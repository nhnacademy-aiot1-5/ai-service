import pandas as pd
from datetime import datetime

def find_outlier(df, idx):
    df = df.sort_values(by=idx)

    q1 = df.iloc[int(len(df)*(1/4))-1][idx]
    q3 = df.iloc[int(len(df)*(3/4))-1][idx]
    iqr = q3-q1
    min = q1-1.5*iqr
    max = q3+1.5*iqr

    return min, max

def set_outlier(df, value):
    floor = round(value[0],2)
    cap = round(value[1],2)

    if (floor == cap):
        cap += 0.1

    df['floor'] = floor
    df['cap'] = cap

    return df

def find_hourly_outlier(df):
    df_result = pd.DataFrame(columns=["hour"])

    for i in range(0, 24):
        df_hourly = df[(pd.DatetimeIndex(df.ds).hour == i)]
        value = find_outlier(df_hourly, 'y')

        data = {
            "hour": {
                'updated_at': str(datetime.now().date()),
                'min': round(value[0], 2),
                'max': round(value[1], 2)
            }
        }

        df_result.loc[i] = data
    return df_result