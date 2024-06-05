import datetime
import logging

import schedule
import time

from forecast import main as forecast
from outlier import main as outlier

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
handler = logging.FileHandler('ioteatime.log')
log.addHandler(handler)

param_grid = {
    'changepoint_prior_scale': [0.01, 0.05, 0.1],
    'seasonality_prior_scale': [0.01, 0.05, 0.1],
    'holidays_prior_scale': [0.01, 0.05, 0.1],
    'growth':['logistic', 'linear']
}

organization_id = 1
count = 0

def run_forecast():
    log.info("forecast job start : " + str(datetime.datetime.now()))
    forecast.run(param_grid)
    log.info("forecast job end : " + str(datetime.datetime.now()))

def run_outlier():
    log.info("outlier job start : " + str(datetime.datetime.now()))
    outlier.run(organization_id)
    log.info("outlier job end : " + str(datetime.datetime.now()))

outlier_job = schedule.every().day.at("00:05").do(run_outlier)
forecast_job = schedule.every().day.at("00:10").do(run_forecast)

while True:
    schedule.run_pending()
    time.sleep(1)
