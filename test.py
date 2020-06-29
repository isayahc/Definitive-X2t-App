from app.Cloud import Cloud
from app.Frequency import IntraDay, Monthly, Daily, Weekly
import pandas as pd
import app.Frequency as F
from datetime import date
import matplotlib.pyplot as plt
import numpy as np
import app.anaylsis_tools as toolz
d = Daily('spy')
w = Weekly('spy')
m = Monthly('spy')
# i = IntraDay('spy',1)


df_20 = w.df_filter_by_date(year=2020)
d_df_20 = d.df_filter_by_date(year=2020,month=6) #['1. open'] #.mean()


data = pd.to_datetime(d_df_20.index)

# def graph_stuff():
#     x = np.linspace(0, 20, 100)
#     plt.axhline(y=d_df_20['3. low'].mean(), color='r', linestyle='-')
#     [ d['3. low'].plot(y='weeks') for d in toolz.split_by_week(d_df_20) ]
#     plt.show()
    
# graph_stuff()

# t = toolz.split_by_week(d_df_20)
# print(t)
# # print( [x for x in t if toolz.is_green_day(t[0]) ] )
# print( [x[:1] for x in t if toolz.is_green_day(x[:1]) ] )

#print(d_df_20.sort_values(by=['5. volume']))
df = d_df_20
df = df.assign(HighToLow= (df['2. high']-df['3. low']) )
print(toolz.add_weekdays(df).sort_values(by=['5. volume']))

