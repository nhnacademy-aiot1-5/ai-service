from ai_service import main
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler(timezone='Asia/Seoul')

param_grid = {
    'changepoint_prior_scale': [0.001, 0.01, 0.05, 0.1, 0.5],
    'seasonality_prior_scale': [0.01, 0.1, 1.0, 5.0, 10.0],
    'holidays_prior_scale': [0.01, 0.1, 5.0, 10.0],
    'growth':['logistic', 'linear']
}

@sched.scheduled_job('cron', hour='0', minute='5', id='forecast')
def job():
    main.backup()
    main.total_usage_forecast(param_grid)
    main.channel_usage_forecast(param_grid)

sched.start()

while True:
    pass

