from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import asyncio
import os
import app.Frequency as Freq
from app.Cloud import Cloud

i = Freq.IntraDay('spy',1)
x = Freq.Daily('spy')
y = Freq.Weekly('spy')
z = Freq.Monthly('spy')
dated =(x,y,z)

def tick():
    print('Tick! The time is: %s' % datetime.now())

def update():
    [print(d) for d in dated]

def update_all():
    for d in dated:
        try:
            d.UpdateCloud()
        except PermissionError:
            continue
    sched.remove_job(sched.get_jobs()[1])




def test():

    loop = asyncio.new_event_loop()
    cors = asyncio.wait([i.dataStream()])
    loop.run_until_complete(cors)
    sched.remove_job(sched.get_jobs()[0])


if __name__ =='__main__':
    i = Freq.IntraDay('spy',1)
    print(i)
    # sched = BlockingScheduler()
    # now = datetime.now()
    # plus2 = datetime.now()+ timedelta(minutes=2)

    # sched.add_job(test, 'cron', day_of_week='mon-fri', hour= now.hour,minute=now.minute+1 )
    # sched.add_job(update_all, 'cron', day_of_week='mon-fri', hour= 16,minute=2 )
    # sched.start()

