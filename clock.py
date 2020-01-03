from apscheduler.schedulers.blocking import BlockingScheduler
from batch import mail

scheduler = BlockingScheduler()


@scheduler.scheduled_job('interval', seconds=10)
def timed_job():
    mail.main()


scheduler.start()
