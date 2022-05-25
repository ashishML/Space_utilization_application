import os
import datetime
from google.cloud import storage
from app import app
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'creds.json'

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
    for blob in client.list_blobs(app.config['BUCKET_NAME'],prefix='videos/'):
        if blob.name.split('/')[1] == '':
            continue
        result.append(blob.name.split('/')[1].split('.')[0])
    if not result:
        succ = False
    return result,succ

def read_file_to_bucket(video_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(app.config['BUCKET_NAME'])
    blob = bucket.blob('videos/'+video_name+'.mp4')
    return blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')

def read_file_from_bucket(video_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(app.config['BUCKET_NAME'])
    blob = bucket.blob('results/'+video_name+'.mp4')
    return blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')

def upload_image_file_to_bucket(img_str,names):
    remote_path = 'first_frame' + "/" + names
    storage_client = storage.Client.from_service_account_json('creds.json')
    bucket = storage_client.get_bucket(app.config['BUCKET_NAME'])
    blob = bucket.blob(remote_path)
    blob.upload_from_string(img_str, content_type = 'image/png', timeout=600)
    return 

def get_image_from_bucket(names):  
    bucket = client.bucket('my-bucket')
    blob = bucket.blob('first_frame/'+names+'.png')
    serving_url = blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
    return serving_url


from base64 import b64encode

def read_image_from_bucket(names):

    bucket = client.get_bucket(app.config['BUCKET_NAME'])
    blobs = bucket.list_blobs(prefix='first_frame/'+names)
    for idx, bl in enumerate(blobs):
        data = bl.download_as_string()
        b = b64encode(data).decode("utf-8")
    return b


