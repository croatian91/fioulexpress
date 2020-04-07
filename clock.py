from apscheduler.schedulers.blocking import BlockingScheduler
from batch import mail

scheduler = BlockingScheduler()


@scheduler.scheduled_job('interval', seconds=10)
def timed_job():
    print("DEBUG test")
    mail.main()
    print("DEBUG end test")


scheduler.start()
