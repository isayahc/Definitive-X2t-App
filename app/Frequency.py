from abc import abstractmethod
from datetime import date, time, timedelta, datetime, timezone
import pandas as pd
from app.cloud import Cloud as clout
from os import path, getenv, listdir, remove, rename
from alpha_vantage.timeseries import TimeSeries
import asyncio
import pytz
import botocore.exceptions
from app.manager import datetimeToDate, marketclosed, isFriday, endofMonth, IntraDay, markethours, isWeekday, string_to_date_func
from app.locationmanager import LocationManager, LocalManager, CloudManager


class Frequency(LocationManager):
    '''used to collect market data'''
    def file_type(self): return 'csv'
    def clean_data(self, df=None) -> pd.DataFrame:
        '''Removes duplicate data'''
        if df is None:
            try:
                x = pd.read_csv(self.file_format(), index_col='date')
                duplicates = x.index.duplicated()
                keep = duplicates == False
                clean_data = x.loc[keep,:]
                return clean_data
            except FileExistsError:
                print("file doesn't exist")
        else:
            try:
                x = pd.DataFrame(df)
                print(x)
                duplicates = x.index.duplicated()
                keep = duplicates == False
                clean_data = x.loc[keep,:]
                return clean_data
            except FileExistsError:
                print("file doesn't exist")
                
    def proper_place(self):
        start = string_to_date_func(self.start)
        end = string_to_date_func(self.end)
        assert start < end      
  
    
class LocalFrequency(LocalManager,Frequency):
    def save_data_locally(self,df: pd.DataFrame)->None:
        '''saves data to Local machine'''
        file_format = self.file_format()
        if path.isfile(file_format):
            print(f"reading data from {file_format}")
            read_df = pd.read_csv(file_format, index_col='date')
            temp_df = read_df.combine_first(df)
            temp_df.to_csv(file_format)
            self.clean_data()
        else:
            print(f"Creating {file_format}....")
            df.to_csv(file_format)
            
    def get_data(self):
        return pd.read_csv(self.file_format(), index_col='date')
    
    
class CloudFrequency(CloudManager, Frequency): 
    def collect_data(self)-> pd.DataFrame:
        '''does an API call to alpha advantage and returns a DataFrame'''
        
    def get_key(self): return getenv('ALPHA_KEY')
    
    def get_data(self) -> pd.DataFrame:
        '''returns the data on the cloud in a DataFrame. Collects data from cloud and 
        turns the csv file into a Dataframe. while creating a destroying a temporary file
        '''
        try:
            self.get_clout().downloadData(self.temp_file(),self.valid_files())
            return pd.read_csv(self.temp_file(), index_col='date')
        finally:
            remove(self.temp_file())

class MultiDayFreq(Frequency):
    def __init__(self, symbol, start=None,end=None):
        super().__init__(symbol, end)
        self.start = start
        
    def prefix(self): return super
    
    def set_start_and_end(self):
        try:
            x = ((self.valid_files()).split('.')[0]).split('_')[-2:]
            print(x)
            self.start, self.end = x
            print(self.start, self.end)
            assert self.start < self.end
        except IndexError:
            print('getting new data')
            x = self.collect_data()
            self.start = datetimeToDate(x.index[-1])
            self.end = datetimeToDate(x.index[0])
            print(self.start, self.end)
            start = string_to_date_func(self.start)
            end = string_to_date_func(self.end)
            assert start < end
            x.to_csv(self.file_format())
            self.get_clout().store_data_on_buckets((self.file_format()))
        finally:
            start = string_to_date_func(self.start)
            end = string_to_date_func(self.end)
            assert start < end

class CloudMultiDay(MultiDayFreq, CloudFrequency):
    def __init__(self, symbol, start=None, end=None):
        super().__init__(symbol, start=start, end=end)
        self.set_start_and_end()
        
    def collect_data(self) -> pd.DataFrame:
        '''gets df from API'''
        return super().collect_data()
        
    def combine_cloud_and_api(self) -> pd.DataFrame:
        '''
        Combines data recently created with data on the cloud
        '''
        cdf = self.cloud_df()
        newdf = self.collect_data()
        temp_data = cdf.combine_first(newdf)
        x = self.clean_data(temp_data)
        #might cause issues in the future
        self.start = (x.index[0]).__str__().split(' ')[0]
        self.end = (x.index[-1]).__str__().split(' ')[0]
        self.proper_place()
        return x
    

    
    def store_data_on_buckets(self) -> None:
        """
        If The appropiate time is reached. This will update data in the buckets. If not appropriate time
        it will throw an error
        """
        if not self.new_interval():
            raise PermissionError('not the right time')
        else:
            new_data = self.combine_cloud_and_api()
            new_data.to_csv(self.file_format())
            self.get_clout().delete_file(self.valid_files())
            self.get_clout().store_data_on_buckets(self.file_format())
            print('presto')
            

class LocalMultiDay(MultiDayFreq, LocalFrequency): 
    def __init__(self, symbol, start=None, end=None):
        super().__init__(symbol, start=start, end=end)
        if not self.valid_files(): raise ValueError('No files match that prefix')
        # try:
        #     x = self.valid_files()
        #     x = ((self.valid_files()).split('.')[0]).split('_')[-2:]
        #     print(x)
        #     self.start, self.end = x
        #     print(self.start, self.end)
        #     assert self.start < self.end
        # except IndexError:
        #     print("get data from cloud first")
        #     raise PermissionError
        
    def data_location(self):
        '''Maybe store all data in data folder'''
        pass
    
    def get_data(self):
        return pd.read_csv(self.file_format(), index_col='date')
#abstract classes    
class DailyFreq(MultiDayFreq): 
    def __str__(self): return f'{self.symbol}_daily_{self.start}_{self.end}'
    def prefix(self): return f'{self.symbol}_daily'
    def new_interval(self): return marketclosed()

class WeeklyFreq(MultiDayFreq): 
    def __str__(self): return f'{self.symbol}_weekly_{self.start}_{self.end}'
    def prefix(self): return f'{self.symbol}_weekly'
    def new_interval(self): return marketclosed() and isFriday()

class MonthlyFreq(MultiDayFreq): 
    def __str__(self): return f'{self.symbol}_monthly_{self.start}_{self.end}'
    def prefix(self): return f'{self.symbol}_monthly'
    def new_interval(self): return endofMonth() and marketclosed()


class IntraDayFreq(IntraDay,Frequency):
    def collect_data(self):
        #This means that the market is open
        start = '9:31:00'
        date_form_start = f'{self.end} {start}'
        ts = TimeSeries(key= self.get_key(), output_format='pandas')
        data , metadata = ts.get_intraday(symbol=self.symbol,
        interval=f'{self.interval}min', outputsize='full')

        date_form_end = data.head(1).index[0].__str__()
        print([date_form_start,date_form_end])
        return  data.loc[self.end.__str__()]
    
#cloud multiday objects
class CloudDailyFreq(DailyFreq, CloudMultiDay): 
    def collect_data(self,outputsize='compact') -> pd.DataFrame:
        ts = TimeSeries(key= self.get_key(), output_format='pandas')
        data , metadata = ts.get_daily(self.symbol,outputsize='full')

        if self.new_interval():
            return pd.DataFrame(data)
        return pd.DataFrame(data)[1:]

class CloudWeeklyFreq(WeeklyFreq, CloudMultiDay):
    def collect_data(self,outputsize='compact') -> pd.DataFrame:
        ts = TimeSeries(key= self.get_key(), output_format='pandas')
        data , metadata = ts.get_weekly(self.symbol)
       
        if self.new_interval():
            return pd.DataFrame(data)
        return pd.DataFrame(data)[1:]


class CloudMonthlyFreq(MonthlyFreq, CloudMultiDay): 
    def collect_data(self,outputsize='compact') -> pd.DataFrame:
        ts = TimeSeries(key= self.get_key(), output_format='pandas')
        data , metadata = ts.get_monthly(self.symbol)
        if self.new_interval():
            return pd.DataFrame(data)
        return pd.DataFrame(data)[1:]

class LocalDailyFreq(DailyFreq, LocalMultiDay): pass
class LocalWeeklyFreq(WeeklyFreq, LocalMultiDay): pass
class LocalMonthlyFreq(MonthlyFreq, LocalMultiDay): pass

#IntraDay objects
class LocalIntraDayFreq(IntraDayFreq, LocalFrequency):
    '''used for streaming data and data analysis''' 
    def valid_files(self): return [i for i in listdir() if self.prefix() in i ]
    async def data_stream(self):      
        if isWeekday() and markethours():
            flag = True
            while markethours():
                x = self.collect_data()
                self.save_data_locally(x)
                await asyncio.sleep(self.interval * 60)
                if len(x) == 0:
                    flag == False
                    raise "Something is off"
        else:
            print('not now')
            raise InterruptedError
    def get_data(self):
        return pd.read_csv(self.file_format(), index_col=date)
    
class CloudIntraDayFreq(IntraDayFreq, CloudFrequency):
    '''used for get and settting data to and from the cloud''' 
    def valid_files(self): return [i for i in self.get_clout().get_s3_keys() if self.prefix() in i ]
    def store_data_on_buckets(self) -> None:
        if not self.new_interval():
            raise PermissionError('not the right time')
        else: 
            self.collect_data_to_cloud()
            
    def collect_data_to_cloud(self):
        '''collects data and temporarily stores them in files to upload it to the cloud'''
        ts = TimeSeries(key= self.get_key(), output_format='pandas')
        data , metadata = ts.get_intraday(symbol=self.symbol,
        interval=f'{self.interval}min', outputsize='full')

        while len(data) !=0:
            date_form_end = data.head(1).index[0].__str__()
            d = date_form_end.__str__().split(' ')[0]
            k = data.loc[d]
            data = data[~data.isin(k)].dropna()
            print(k)
            k.to_csv(IntraDay(self.symbol,self.interval,d).file_format())

        x = [i for i in listdir() if self.prefix() in i and i not in self.valid_files() ]
        [self.get_clout().store_data_on_buckets(i) for i in x ]
        [remove(i) for i in  listdir() if self.prefix() in i] 
        
    def get_data(self):
        '''Should only get data from cloud it data is not currently being updated '''
        #flase if weekday and markethours and end is today
        # return permission error
        #else get data
        print(self.end)
        if isWeekday() and self.end == date.today() and marketclosed():
            raise PermissionError("cannot get data while it is still being updated")
        else:
            self.get_clout().download_data(self.temp_file(),self.file_format())
            data = pd.read_csv(self.temp_file(), index_col='date')
            remove(self.temp_file())
            return data
        
    def collect_data_to_cloudII(self):
        '''collects data and temporarily stores them in files to upload it to the cloud'''
        ts = TimeSeries(key= self.get_key(), output_format='pandas')
        data , metadata = ts.get_intraday(symbol=self.symbol,
        interval=f'{self.interval}min', outputsize='full')
        print(data)