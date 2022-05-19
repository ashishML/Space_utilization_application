import os
import datetime
from google.cloud import storage
from app import app
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'creds.json'

client = storage.Client()

def upload_file_to_bucket(file):
    name = file.filename
    data = file.read()
    remote_path = 'videos' + "/" + name
    storage_client = storage.Client.from_service_account_json('creds.json')
    bucket = storage_client.get_bucket(app.config['BUCKET_NAME'])
    blob = bucket.blob(remote_path)
    blob.upload_from_string(data, content_type = 'video/mp4', timeout=600)
    return 

def get_bucket_file_names():
    result = []
    succ = True
    for blob in client.list_blobs(app.config['BUCKET_NAME']):
            if blob.name.split('/')[1] == '':
                continue
            result.append( blob.name.split('/')[1].split('.')[0])
    if not result:
        succ = False
    return result,succ

def read_file_to_bucket(video_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(app.config['BUCKET_NAME'])
    blob = bucket.blob('videos/'+video_name+'.mp4')
    return blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
    