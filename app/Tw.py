from app.manager import Manager, IntraDay, markethours , marketclosed
from app.locationmanager import LocalManager, CloudManager
from os import rename, listdir,remove
from datetime import date
import json
import asyncio

#Tw objects
class Tw(IntraDay):
    '''used to compare with Frequency objects. After the data is streamed compare it to cloud and update it.'''
    def __str__(self): return f'twillio_{self.symbol}_{self.interval}min_{self.end}'
    def prefix(self) ->str: return "_".join((str(self).split('_')[:3]))
    def file_type(self) ->str: 
        '''the file format'''
        return 'json'
    def new_day(self) -> None:
        '''changes the date to be current date if valid trading day'''
        try: 
            old_name = self.valid_files()
            new_name = Tw(self.symbol,self.interval,date.today()).file_format()
            rename(old_name , new_name)
        except IndexError:
            raise FileNotFoundError
    def get_data(self) -> dict:
        '''returns data from file into dictionary object'''
        print('retrieving file')
        f = open(self.file_format(),'r')
        old_data = f.read()
        old_data = dict(json.loads(old_data))
        f.close()
        return old_data

    def combine_dicts(self,dict_a,dict_b) -> dict:
        '''returns a dict object that appends values if both dicts have the same keys.
        values with non matching keys are forgone
        '''
        x,y = dict_a,dict_b
        x = {i: [x[i]] if isinstance(x[i],int) else x[i]  for i in x.keys()}
        y = {i: [y[i]] if isinstance(y[i],int) else x[i]  for i in y.keys()}
        return {i: [*{*(x[i] + y[i])}] for i in {*x.keys()} & {*y.keys()} }
    
    def add_data(self,new_data:dict,old_data:dict) -> dict:
        '''takes all of the values in new_data AND old_data'''
        dict1 = new_data
        dict2 = old_data
        if dict1 == dict2:
            print('easy')
            return dict1
        elif {*dict1.keys()} & {*dict2.keys()} == set():
            return{**dict1,**dict2}
        else:
            x = {i: [dict1[i]] if isinstance(dict1[i],int) else dict1[i]  for i in dict1.keys()}
            y = {i: [dict2[i]] if isinstance(dict2[i],int) else dict2[i]  for i in dict2.keys()}
            
            return {
                **{i: [*{*(y[i] + x[i]) } ] for i  in {*x.keys()} & {*y.keys()} },
                **{i: y[i] if i in y else x[i] for i in {*x.keys()} ^ {*y.keys()} }
            }

    def delete_data(self,new_dict:dict, old_dict:dict) -> dict:
        '''removes from old anythin in new. If any new[values] == None del value in old, else take new[value] ^ old value. input {} to delete dict'''
        new = new_dict 
        old = old_dict
        print(new, old)
        if (new == old):
            return {}
        elif  new == {}:
            return old_dict

        [ old.pop(i) for i in new if not new[i] ]
        print(old)
        if ({*new.keys()} & {*old.keys()} == set()):
            return old

        old ={
            **{i: [*({*old[i]} ^ {*new[i]} )] for i in ({*new.keys()} & {*old.keys()}) },
            **{i : old[i] for i in ( {*old.keys()}& ({*new.keys()} ^ {*old.keys()})) }
        }
        return old
    
class CloudTw(Tw,CloudManager): 
    '''can get/set data from the cloud but cannot be stored on local files.
    Needs a str symbol and a valid int timeframe. This version of tw cannot stream data.
    '''
    def get_data(self) -> dict:
        '''returns data from cloud into dictionary object'''
        print('retrieving file')
        filename = self.file_format()
        temp_filename = self.temp_file()
        self.get_clout().download_data(temp_filename, filename)
        f = open(temp_filename,'r')
        old_data = f.read()
        old_data = dict(json.loads(old_data))
        f.close()
        remove(temp_filename)
        return old_data
    def get_data_and_file(self) -> dict:
        '''returns data and file'''
        print('retrieving file')
        filename = self.file_format()
        self.get_clout().download_data(filename, filename)
        f = open(filename,'r')
        old_data = f.read()
        old_data = dict(json.loads(old_data))
        f.close()
        return old_data
    
    def set_cloud_data(self,data:dict) -> None:
        '''sets dict to json to store on cloud. Overwrites existing data'''
        file_form = self.file_format()
        f = open(file_form,'w')
        data = json.dumps(data)
        f.write(data)
        f.close()
        self.get_clout().store_data_on_buckets(file_form)
        remove(file_form)
        
class LocalTw(Tw,LocalManager):
    def __init__(self, symbol, interval, end=date.today()):
        super().__init__(symbol, interval, end=end)
        print(self.valid_files())
    '''Can get/set data from Local machine but cannot upload to cloud.
    Needs a str symbol and a valid int timeframe
    '''

    async def data_stream(self,dict_data) ->None:
        ##part1 
        if marketclosed():
            raise PermissionError("Invalid time")
        else:
            keys = [*dict_data.keys()]
            key = keys[0]
            print(keys)
            master_data = self.get_data()
            if len(dict_data) ==1 and len(keys) ==1:
                if  key in master_data:
                    value = dict_data[key]
                else: 
                    raise ValueError(f'{keys[0]} not in data ')
            else:
                raise ValueError('incorrect format ')
        #part2 
        if isinstance(master_data[key], int):
            while value != master_data[key] and markethours():
                print('int')
                print(value, master_data[key])
                await asyncio.sleep (self.interval*1)
                print('again')
            print('That a GOOOOOO')
            return_dict = self.delete_data({key:[value]},master_data)
            self.save_data(return_dict)
        elif isinstance(master_data[key], list):
            while value not in self.get_data()[key] and markethours():
                print('list')
                print(value, master_data[key])
                print(value not in self.get_data()[key])
                await asyncio.sleep(self.interval*1)
                print('again')
            print('That a GOOOOOO')
            return_dict = self.delete_data({key:[value]},master_data)
            self.save_data(return_dict)
                         
    def save_data(self,data:dict) -> None:
        '''saves data to file'''
        f = open(self.file_format(),'w')
        f.write(json.dumps(data))
        f.close()
        
            
            
        
        