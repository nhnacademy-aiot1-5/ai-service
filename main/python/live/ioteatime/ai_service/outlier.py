from outlier import main
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler(timezone='Asia/Seoul')
organization_id = 1

@sched.scheduled_job('cron', hour='0', minute='5', id='outlier')
def job():
    main.run(organization_id)

sched.start()

while True:
    pass
