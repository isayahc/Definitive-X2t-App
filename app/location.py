from abc import abstractmethod
from datetime import date, time, timedelta, datetime, timezone
import pandas as pd
from app.cloud import Cloud as clout
from os import path, getenv, listdir, remove, rename
import asyncio
import pytz
import json
import botocore.exceptions


#2nd level
class Location(object):pass
class Cloud(Location): 
    '''Cloud files can make changes to the cloud. Also can download dataframes from the cloud to the app'''
    def get_clout(self): 
        '''object for handiling the cloud'''
        return clout ()
    def valid_files(self): 
        try:
            x=  [i for i in self.get_clout().get_s3_keys() if self.prefix() in i ]
            if not x:
                raise IndexError("no file matching the prefix here. Please Try a different folder or using Cloud Multiday")
            elif len(x) > 1:
                raise Exception('Too many values. Please adjust')
            else: 
                return x[0]
        except botocore.exceptions.SSLError:
            print('no internet. PAY YO BILLZZ!')
            
    def temp_file(self): return f'temp_{self.file_format()}'
class Local(Location):
    '''Under most curcumstances should not be able to make changes to the cloud'''
    def valid_files(self): 
        '''File names should be unique unless file is for IntraDayFreq Object'''
        x=  [i for i in listdir() if self.prefix() in i ]
        if not x:
            raise IndexError("no file matching the prefix here. Please Try getting data from the cloud first")
        elif len(x) > 1:
            raise Exception('Too many values. Please adjust')
        else: 
            return x[0]
