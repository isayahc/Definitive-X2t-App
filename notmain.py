from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime 

def test():
    print("I work")
    
if __name__ == '__main__':
    sched = BlockingScheduler()
    x = datetime.now()
    sched.add_job(test, 'cron', day_of_week='mon-fri', hour= x.hour,minute=x.minute+3 )
    sched.add_job(test, 'interval', minutes=5)
    sched.start()
    