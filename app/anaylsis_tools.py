import pandas as pd 
from datetime import date, timedelta
from app.Frequency import IntraDay, Monthly, Daily, Weekly
import matplotlib.pyplot as plt
import numpy as np

def split_by_week(df):
    #find ways to improve
    '''returns a 2d array of days'''
    i = 0 
    dd = [[]]
    dd_num = 0
    data = pd.to_datetime(df.index)
    
    while i < len(df) -1:
        dd[dd_num].append(data[i])
        if data[i] <= data[i+1] - timedelta(days=3):
            print('new Week')
            dd.append([])
            dd_num +=1
        i +=1
    dd[dd_num].append(data[i])
    
    dt_to_d = lambda x: str(x).split(' ')[0]
    return [  (df.loc[dt_to_d(i[0]):dt_to_d(i[-1])])  for i in dd ] 

def locate_min_row(df,column):
    #turn into decorator
    return df.loc[df[column] == df[column].min()]

def df_filter_Weekday(df,day:int):
    #fix later
    '''will filter to only the days matching the day 1=mon'''
    weekdays =  list(map(date.isoweekday,pd.to_datetime(df.index)))
    df = df.assign(Weekday=weekdays)
    #this statement might cause issues in the future
    return df.where(df['Weekday']==day).dropna()

def is_green_day(df):
    ''' used mainly for a single element in a dataFrame. Will return true if positive'''
    openn = (df)['1. open']
    close = (df)['4. close']
    compare = openn - close
    return float(compare) >0

def graph_stuff(df):
    x = np.linspace(0, 20, 100)
    df.plot()
    plt.show()
    
def add_weekdays(df):
    weekdays =  list(map(date.isoweekday,pd.to_datetime(df.index)))
    df = df.assign(Weekday=weekdays)
    return df

def graph_stuff(df,column):
    #used best for daily dataframe
    x = np.linspace(0, 20, 100)
    [ (d[column]-(d[column]).iloc[0]).plot() for d in split_by_week(df) ]
    plt.show()
    
def flatten_column(df,column):
    return (df[column]-(df[column]).iloc[0])
        

# def main():
#     d = Daily('spy')
#     d_df_20 = d.df_filter_by_date(year=2020,month=6)
#     data = pd.to_datetime(d_df_20.index)
#     print(toolz.split_by_week(data))