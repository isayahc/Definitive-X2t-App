import botocore
import uuid
from boto3 import client, resource
import logging
import os

#default bucket value or change
class Cloud:
    def __init__(self):
        '''
        ONLY FOR LOCAL MACHINE
        # x = APIs().getamazonCreditals()
        # self.cloud_resource = resource(
        #     's3',
        #     aws_access_key_id = x['aws_access_key_id'],
        #     aws_secret_access_key = x['aws_secret_access_key'],
        #     region_name= x['region_name'],
        # )
        # self.cloud_client = client(
        #     's3',
        #     aws_access_key_id = x['aws_access_key_id'],
        #     aws_secret_access_key = x['aws_secret_access_key'],
        #     region_name= x['region_name'],
        # )
        # self.resource = resource
        # self.client = client
        '''

        self.cloud_resource = resource('s3')
        self.cloud_client = client('s3')
        
    def print_buckets(self) -> None:
        '''Prints all existing buckets'''
        for bucket in self.cloud_resource.buckets.all():
            print(bucket)

    def get_default_bucket_name(self) -> str:
        buckets = [i.name for i in self.cloud_resource.buckets.all() if 'xttest' in i.name][0]
        if buckets:
            return buckets
        else:
            raise "There exist no buckets" 

    def get_default_bucket_object(self):
        bucket = [i for i in self.cloud_resource.buckets.all() if 'xttest' in i.name][0]
        if bucket:
            return bucket
        else:
            raise "There exist no buckets"
 
    def create_bucket(self,bucketname,location=None):
        ''' creates bucket object'''
        self.s3.create_bucket(Bucket=bucketname, CreateBucketConfiguration={
                'LocationConstraint': 'us-east-2'
        })

    def store_data_on_buckets(self,file):
        ''' Probably needs some tweaking. Uploads data to the cloud'''
        try:
            self.cloud_resource.Object(self.get_default_bucket_name(), file).put(Body=open(file, 'rb'))
        except FileNotFoundError:
            #probably should not create an empty file just to upload
            open(file, 'w')
            self.cloud_resource.Object(self.get_default_bucket_name(), file).put(Body=open(file, 'rb'))
        # except FileNotFoundError:
        #     os.makedirs(file.split('/')[0])
        finally:
            os.remove(file)
            print("I should close the file")

    def download_data(self, tofilename : str, fromfilename :str):
        '''first arg is to local, second arg is from cloud file'''
        try:
            bucket = self.get_default_bucket_object()
            with open(tofilename, 'wb') as data:
                bucket.download_fileobj(fromfilename, data)
        except FileNotFoundError:
            raise Exception("Object does not exist on machine")
        except botocore.exceptions.ClientError:
            os.remove(tofilename)
            raise Exception("Object does not exist")

    def get_s3_keys(self):
        """Get a list of keys in an S3 bucket."""
        keys = []
        resp = self.cloud_client.list_objects_v2(Bucket= self.get_default_bucket_name())
        for obj in resp['Contents']:
            keys.append(obj['Key'])
        return keys

    def delete_file(self, file: str):
        bucket = self.get_default_bucket_name()
        self.cloud_resource.Object(bucket, file).delete()
        