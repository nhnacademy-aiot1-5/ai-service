from ai_service.main import set_outlier
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler(timezone='Asia/Seoul')

@sched.scheduled_job('cron', hour='0', minute='5', id='outlier')
def job():
    set_outlier()

sched.start()

while True:
    pass
