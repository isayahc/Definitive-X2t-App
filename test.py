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
d_df_20 = d.df_filter_by_date(year=2020) #['1. open'] #.mean()


data = pd.to_datetime(d_df_20.index)

df = d_df_20


x, y, s, c = np.random.rand(4, 30)
x = df['1. open'] - df['4. close']
y = df['5. volume']
s = x

fig, ax = plt.subplots()
ax.scatter(x, y, s)

plt.show()
