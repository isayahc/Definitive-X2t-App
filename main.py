from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import asyncio
import os
import app.Frequency as Freq
from app.Cloud import Cloud

sched = BlockingScheduler()
Asched = AsyncIOScheduler()

# cloud = Cloud()
# print(cloud.getDefaulttBucketName())
# print(cloud.get_s3_keys())

# d = Freq.Daily('spy')
# x = d.collectData()
# print(x)


# daily = Freq.Daily('spy')
# daily.loadData()


if Freq.isWeekday and Freq.marketclosed():
    print (datetime.now())


def tick():
    print('Tick! The time is: %s' % datetime.now())




# if __name__ =='__main__':
#     sched.add_job(tick, 'cron', day_of_week='mon-fri', hour=16,minute=2)
#     sched.add_job(tick, 'interval', minutes=.2)
#     sched.start()