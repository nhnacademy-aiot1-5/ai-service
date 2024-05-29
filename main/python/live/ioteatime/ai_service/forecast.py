from apscheduler.schedulers.background import BackgroundScheduler

from forecast import main

sched = BackgroundScheduler(timezone='Asia/Seoul')

param_grid = {
    'changepoint_prior_scale': [0.01, 0.05, 0.1],
    'seasonality_prior_scale': [0.01, 0.05, 0.1],
    'holidays_prior_scale': [0.01, 0.05, 0.1],
    'growth':['logistic', 'linear']
}

@sched.scheduled_job('cron', hour='0', minute='5', id='forecast')
def job():
    main.run(param_grid)

sched.start()

while True:
    pass

