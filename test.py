from app.Cloud import Cloud
from app.Frequency import IntraDay, Monthly, Daily, Weekly
import pandas as pd
import app.Frequency as F

d = Daily('spy')
w = Weekly('spy')
m = Monthly('spy')



print(F.marketclosed())
print(F.markethours())


#print( ((wd['2. high']).sub(wd['3. low'])).mean() )
# x =  [ str(i) for i in wd.index if '2001-10' in i] 
# print (x)
# print(wd.loc[x])



# df_20 = df_filter_by_date(wd,year=2020)
# d_df_20 = df_filter_by_date(d,year=2020,month=6)

# print( ((df_20['2. high']).sub(df_20['3. low'])).mean() )
# print( ((d_df_20['1. open']).sub(d_df_20['3. low'])).mean() )