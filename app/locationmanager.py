from app.manager import Manager
from app.location import Location, Local, Cloud
from app.cloud import Cloud as clout
from os import listdir


class LocationManager(Manager,Location): pass

class CloudManager(LocationManager,Cloud):
    def set_cloud_data(self)->None:
        '''Saves data to s3 bucket. Anything in the current file will be saved to the cloud'''
        #might get rid of this
        self.get_clout().store_data_on_buckets(self.file_format())
        

class LocalManager(LocationManager, Local): pass