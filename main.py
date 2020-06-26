from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
import os
import app.Frequency as Freq
from app.Cloud import Cloud

def update_all():
    print("i am now running")
    for d in dated:
        try:
            d.UpdateCloud()
            print(f'{d} worked')
        except PermissionError:
            print(f'error occured in {d}')
            continue

def test():
    update_all()

def test2():
    print(datetime.now().__str__())

if __name__ =='__main__':
    i = Freq.IntraDay('spy',1)
    x = Freq.Daily('spy')
    y = Freq.Weekly('spy')
    z = Freq.Monthly('spy')
    dated =(x,y,z,i)
    sched = BlockingScheduler()
    #just to make sure things are running properly
    x = datetime.now()
    print(x)
    sched.add_job(update_all, 'cron', day_of_week='mon-fri', hour= 20,minute=4 )
    #remember it is based on UTC
    sched.start()
