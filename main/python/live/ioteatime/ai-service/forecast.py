import train

model = train.model
future = model.make_future_dataframe(periods=30*24, freq='1h', include_history=False)
forecast = model.predict(future)

df = forecast[['ds', 'yhat']]
df['ds'] = df['ds'].dt.strftime('%Y-%m-%d 00:00:00')
df = pd.DataFrame(df.groupby(df.ds)['yhat'].sum())
df = df.round(2)
df = df.reset_index()
df.rename(columns={'yhat':'kwh', 'ds':'time'} ,inplace=True)
