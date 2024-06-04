import datetime

from apscheduler.schedulers.background import BackgroundScheduler
import logging

from forecast import main as forecast
from outlier import main as outlier

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler('ioteatime.log')
log.addHandler(handler)

sched = BackgroundScheduler(timezone='Asia/Seoul')

param_grid = {
    'changepoint_prior_scale': [0.01, 0.05, 0.1],
    'seasonality_prior_scale': [0.01, 0.05, 0.1],
    'holidays_prior_scale': [0.01, 0.05, 0.1],
    'growth':['logistic', 'linear']
}

organization_id = 1

@sched.scheduled_job('cron', hour='00', minute='10', id='forecast')
def run_forecast():
    log.info("forecast job start : " + str(datetime.datetime.now()))
    forecast.run(param_grid)
    log.info("forecast job end : " + str(datetime.datetime.now()))

@sched.scheduled_job('cron', hour='00', minute='05', id='outlier')
def run_outlier():
    log.info("outlier job start : " + str(datetime.datetime.now()))
    outlier.run(organization_id)
    log.info("outlier job end : " + str(datetime.datetime.now()))

sched.start()

while True:
    pass

