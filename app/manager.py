from abc import abstractmethod
from datetime import date, time, timedelta, datetime, timezone
from calendar import monthrange

#head of heirachy
#abstract
class Manager(object):
    ''' Manages the general files for all of the classes'''
    def __init__(self,symbol,end):
        self.symbol = symbol.upper()
        self.end = end
                
    def file_format(self): 
        '''returns string with file extention'''
        return f'{self}.{self.file_type()}'
        
    @abstractmethod
    def __str__(self): 
        '''returns the specific string'''
        pass
    
    @abstractmethod
    def prefix(self): 
        '''returns the general string'''
        pass
    
    @abstractmethod
    def get_data(self):
        '''test'''
        pass
    
    @abstractmethod
    def new_interval(self):pass
    
    @abstractmethod
    def file_type(self): 
        '''returns the type of file'''
        pass
    
#in manager.py because it is inherited directed from it
class IntraDay(Manager):
    def __init__(self, symbol,interval, end=date.today(), ):
        super().__init__(symbol, end)
        self.interval = interval
    def __str__(self): return f'{self.symbol}_{self.interval}min'
    def prefix(self) -> str: return "_".join((str(self).split('_')[:2]))
    def new_interval(self)->bool: return marketclosed() and isWeekday()
    
### Helper functions
def datetimeToDate(x:datetime) -> str:
    '''turns datetime strimng into datetime'''
    return date( *[int(i) for i in x.__str__().split(' ')[0].split('-')])

string_to_date_func =lambda x : date(*[int(i) for i in str(x).split('-')])

def isWeekday() ->bool: return 7 > date.today().weekday() <= 4

def markethours() -> bool:
    #UTC time
    return (time(12, 29) < datetime.now(timezone.utc).time() < time(20, 2)) and isWeekday()

def marketclosed() -> bool:
    '''returns true if time now is greater than time(20, 2, 30, 40306) UTC'''
    return datetime.now(timezone.utc).time() > time(20, 2, 30, 40306)

def isFriday() -> bool: return date.today().weekday() == 4
        
def endofMonth() -> bool:
    '''return true if today is the last day of the month'''
    day,month,year = date.today().day, date.today().month, date.today().year
    day = monthrange(year,month)[1]
    d = date(year,month,day)
    return date.today() == d

def DaysUntilendofMonth() -> timedelta:
    '''returns days until the end of the month'''
    day,month,year = date.today().day, date.today().month, date.today().year
    day = monthrange(year,month)[1]
    d = date(year,month,day)
    if date.today() != d:
        return (date.today() - d)
    