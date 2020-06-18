from datetime import date, datetime, time, timedelta
from os import path, getenv, listdir
import pandas as pd
from app.Cloud import Cloud
from abc import abstractmethod
from alpha_vantage.timeseries import TimeSeries
from calendar import monthrange
import asyncio

key = alphaKey = getenv('ALPHA_KEY')

class Frequency:
    def __init__(self,symbol,start=None, end=None):
        self.symbol = symbol.upper()
        self.start = start
        self.end = end
        self.cloud = Cloud()

    def properplace(self):
        start = strToDate(self.start)
        end = strToDate(self.end)
        assert start < end

    def fileFormat(self):
        return f'{self}.csv'
    
    def __repr__(self):
        return f'start:{self.start} end:{self.end}'
    
    def SaveToCloud(self):
        self.c.storeDataonBucket(self.fileFormat())
    
    def loadData(self):
        try:
            return pd.read_csv(self.fileFormat(), index_col='date')
        except FileNotFoundError:
            self.cloud.downloadData(self.fileFormat(),self.fileFormat())
            return pd.read_csv(self.fileFormat(), index_col='date')
        else:
            raise FileNotFoundError

    def saveDataLocally(self,df: pd.DataFrame):
        fileform = self.fileFormat()
        if path.isfile(fileform):
            print(f"reading data from {fileform}")
            read_df = pd.read_csv(fileform, index_col='date')
            temp_df = read_df.combine_first(df)
            temp_df.to_csv(fileform)
            self.cleanData()
        else:
            print(f"Creating {fileform}....")
            df.to_csv(fileform)

    def cleanData(self, df=None) -> pd.DataFrame:
        if df is None:
            try:
                x = pd.read_csv(self.fileFormat(), index_col='date')
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

    def UpdateCloud(self):
        if self.NewInterval:
            self.cloud_Data()

    @abstractmethod
    def NewInterval(self): pass

    @abstractmethod
    def collectData(self) -> pd.DataFrame: pass

    @abstractmethod
    def prefix(self): pass

    @abstractmethod
    def ValidFiles(self): pass

class IntraDay(Frequency):
    def __init__(self, symbol, interval,end=date.today()):
        super().__init__(symbol, end=end)
        self.cloud = Cloud()
        if interval not in [1,5,10,15,30,60]:
            raise ValueError(f"valid intervals are{[1,5,10,15,30,60]}")
        self.interval = interval

    def ValidFiles(self):
        return [i for i in self.cloud.get_s3_keys() if self.prefix() in i ]

    def __repr__(self):
        return f'end:{self.end}'

    def __str__(self):
        return f'{self.symbol}_{self.interval}min_{self.end}'

    def prefix(self):
        return "_".join((str(self).split('_')[:2]))

    def collectData(self):
        week_day = date(*[int(i) for i in str(self.end).split('-')]).weekday()
        #This means that the market is open
        start = '9:31:00'
        date_form_start = f'{self.end} {start}'

        ts = TimeSeries(key= key, output_format='pandas')
        data , metadata = ts.get_intraday(symbol=self.symbol,
        interval=f'{self.interval}min', outputsize='full')

        date_form_end = data.head(1).index[0].__str__()
        print([date_form_start,date_form_end])

        return  data.loc[self.end.__str__()]
    
    def collectDataToCloud(self):
        week_day = date(*[int(i) for i in str(self.end).split('-')]).weekday()
        #This means that the market is open

        ts = TimeSeries(key= key, output_format='pandas')
        data , metadata = ts.get_intraday(symbol=self.symbol,
        interval=f'{self.interval}min', outputsize='full')

        while len(data) !=0:
            date_form_end = data.head(1).index[0].__str__()
            d = date_form_end.__str__().split(' ')[0]
            k = data.loc[d]
            data = data[~data.isin(k)].dropna()
            print(k)
            k.to_csv(IntraDay(self.symbol,self.interval,d).fileFormat())

        x = [i for i in listdir() if self.prefix() in i ]
        [self.cloud.storeDataonBucket(i) for i in x ]

    
class MultiDay(Frequency):
    def __init__(self, symbol, start=None, end=None):
        super().__init__(symbol, start=start, end=end)
        ''' 
        proper format: {symbol}_{start_date}_{end_date}
        '''
        self.cloud = Cloud()
        self.set_start_and_end()

    def set_start_and_end(self):
        try:
            x = ((self.ValidFiles()).split('.')[0]).split('_')[-2:]
            self.start, self.end = x
            assert self.start < self.end
        except IndexError:
            print('getting new data')
            x = self.collectData()
            self.start = datetimeToDate(x.index[-1])
            self.end = datetimeToDate(x.index[0])
            print(self.start, self.end)
            start = strToDate(self.start)
            end = strToDate(self.end)
            assert start < end
            self.cloud.storeDataonBucket((self.fileFormat()))
        finally:
            start = strToDate(self.start)
            end = strToDate(self.end)
            assert start < end

    def __str__(self):
        return f'{self.symbol}_{type(self).__name__.lower()}_{self.start}_{self.end}'

    def ValidFiles(self):
        return [i for i in self.cloud.get_s3_keys() if self.prefix() in i ][0]

    def prefix(self):
        k = (type(self).__name__).lower()
        return f'{self.symbol}_{k}'

    def cloud_df(self):
        self.cloud.downloadData(self.ValidFiles(),self.ValidFiles())
        return pd.read_csv(self.ValidFiles(), index_col='date')
        
    def combineCloudandAPI(self): 
        cdf = self.cloud_df()
        newdf = self.collectData()
        temp_data = cdf.combine_first(newdf)
        x = self.cleanData(temp_data)
        #might cause issues in the future
        self.start = (x.index[0]).__str__().split(' ')[0]
        self.end = (x.index[-1]).__str__().split(' ')[0]
        self.properplace()
        return x

    def UpdateCloud(self):
        if not self.NewInterval():
            raise PermissionError('not the right time')
        else:
            new_data = self.combineCloudandAPI()
            new_data.to_csv(self.fileFormat())
            self.cloud.deleteFile(self.ValidFiles())
            self.cloud.storeDataonBucket(self.fileFormat())
            print('presto')

    @abstractmethod
    def NewInterval(self): pass

class Daily(MultiDay):
    def __init__(self, symbol, start=None, end=None):
        super().__init__(symbol, start=start, end=end)

    def collectData(self,outputsize='compact'):
        ts = TimeSeries(key= key, output_format='pandas')
        data , metadata = ts.get_daily(self.symbol,outputsize='full')
        return pd.DataFrame(data)

    def NewInterval(self):
        return marketclosed() and isWeekday()

class Weekly(MultiDay):
    def __init__(self, symbol, start=None, end=None):
        super().__init__(symbol, start=start, end=end)

    def collectData(self,outputsize='compact'):
        ts = TimeSeries(key= key, output_format='pandas')
        data , metadata = ts.get_weekly(self.symbol)
        return pd.DataFrame(data)

    def NewInterval(self):
        return isFriday()

class Monthly(MultiDay):
    def __init__(self, symbol, start=None, end=None):
        super().__init__(symbol, start=start, end=end)

    def collectData(self,outputsize='compact'):
        ts = TimeSeries(key= key, output_format='pandas')
        data , metadata = ts.get_monthly(self.symbol)
        return  pd.DataFrame(data)

    def NewInterval(self):
        return dateEndofMonth()



### Helper functions
def datetimeToDate(x:datetime):
        return date( *[int(i) for i in x.__str__().split(' ')[0].split('-')])

strToDate =lambda x : date(*[int(i) for i in str(x).split('-')])

def isWeekday():
    today = date.today().weekday()
    return 7 > date.today().weekday() <= 4

def markethours():
    return time(9,30) < datetime.now().time() < time(16,3)

def marketclosed():
    return datetime.now().time() > time(16,3)

def isFriday():
    return date.today().weekday() == 4


def endofMonth():
    m = date.today().month
    y = date.today().year
    day,m_date = monthrange(y,m)
    # print(day)
    if 7 > day <= 4:
        return date.today() == date(y,m,m_date)
    else:
        x = date(y,m,m_date)
        while not 7 > x.weekday() <=4:
            x - timedelta(days=1)
            return date.today() == x

def dateEndofMonth(date_data: date= datetime.today()):
    m = date_data.month
    y = date_data.year
    day,m_date = monthrange(y,m)
    if 7 > day <= 4:
        return date_data == date(y,m,m_date)
    else:
        x = date(y,m,m_date)
        while not 7 > x.weekday() <=4:
            x - timedelta(days=1)
            return date_data == x