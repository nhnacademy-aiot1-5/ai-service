from apscheduler.schedulers.background import BackgroundScheduler

from forecast import main as forecast
from outlier import main as outlier

sched = BackgroundScheduler(timezone='Asia/Seoul')

param_grid = {
    'changepoint_prior_scale': [0.01, 0.05, 0.1],
    'seasonality_prior_scale': [0.01, 0.05, 0.1],
    'holidays_prior_scale': [0.01, 0.05, 0.1],
    'growth':['logistic', 'linear']
}

organization_id = 1

@sched.scheduled_job('cron', hour='0', minute='10', id='forecast')
def run_forecast():
    forecast.run(param_grid)

@sched.scheduled_job('cron', hour='0', minute='5', id='outlier')
def run_outlier():
    outlier.run(organization_id)

sched.start()

while True:
    pass

