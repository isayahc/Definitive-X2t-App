from app.Cloud import Cloud
from app.Frequency import IntraDay

c = Cloud()
print(c.get_s3_keys())

i = IntraDay('spy',1)
i.collectData()

