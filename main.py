from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
import os
import app.Frequency as Freq
from app.Cloud import Cloud

def update_all():
    for d in dated:
        try:
            d.UpdateCloud()
            print(f'{d} worked')
        except PermissionError:
            print(f'error occured in {d}')
            continue


if __name__ =='__main__':
    i = Freq.IntraDay('spy',1)
    x = Freq.Daily('spy')
    y = Freq.Weekly('spy')
    z = Freq.Monthly('spy')
    dated =(x,y,z,i)
    update_all()
    # sched = BlockingScheduler()
    # sched.add_job(update_all, 'cron', day_of_week='mon-fri', hour= 16,minute=4 )
    # sched.start()

