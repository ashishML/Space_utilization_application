import datetime
from google.cloud import storage
from app import app
from base64 import b64encode
import urllib
import google.auth.transport.requests
import google.oauth2.id_token
import pandas as pd
import pandas_gbq
import pandas_gbq
import json
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'creds.json'
# os.environ["GCLOUD_PROJECT"]= "springml-gcp-internal-projects"
client = storage.Client()
# credentials_pd = service_account.Credentials.from_service_account_file('creds.json',)

def upload_file_to_bucket(file):
    name = file.filename
    data = file.read()
    remote_path = 'videos' + "/" + name
    # storage_client = storage.Client.from_service_account_json('creds.json')
    bucket = client.get_bucket(app.config['BUCKET_NAME'])
    blob = bucket.blob(remote_path)
    blob.upload_from_string(data, content_type = 'video/mp4')
    return 



def read_file_from_bucket(video_name):
    # storage_client = storage.Client()
    bucket = client.bucket(app.config['BUCKET_NAME'])
    blob = bucket.blob('results/'+video_name+'.mp4')
    return blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
  
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

# Function to check video in 'results'
def check_video_name(name):
    result = False
    for blob in client.list_blobs(app.config['BUCKET_NAME'],prefix='results/'):
        if blob.name.split('/')[-1] == name:
            result = True
    return result

# Funtion to return urls of multiple videos
def get_videos(video_name):
    # storage_client = storage.Client.from_service_account_json('creds.json')
    bucket = client.get_bucket(app.config['BUCKET_NAME'])
    result = []
    for v_name in video_name:
        blob = bucket.blob('results/'+ v_name)

        url = blob.generate_signed_url(
            expiration=datetime.timedelta(minutes=15000),
            method='GET'
            )
        result.append(url)  
    return result


def read_file_to_bucket(video_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(app.config['BUCKET_NAME'])
    blob = bucket.blob('videos/'+video_name)
    return blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')


def upload_image_file_to_bucket(img_str,names):
    remote_path = 'first_frame' + "/" + names
    # storage_client = storage.Client.from_service_account_json('creds.json')
    bucket = client.get_bucket(app.config['BUCKET_NAME'])
    blob = bucket.blob(remote_path)
    blob.upload_from_string(img_str, content_type = 'image/png', timeout=600)
    return 

def get_image_from_bucket(names):  
    bucket = client.bucket('my-bucket')
    blob = bucket.blob('first_frame/'+names+'.png')
    serving_url = blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
    return serving_url



def read_image_from_bucket(names):
    bucket = client.get_bucket(app.config['BUCKET_NAME'])
    blobs = bucket.list_blobs(prefix='first_frame/'+names)
    for idx, bl in enumerate(blobs):
        data = bl.download_as_string()
        b = b64encode(data).decode("utf-8")
    return b



def make_authorized_get_request(v_name,room,cameraid,roi):
    endpoint ='https://spaceutilizationv14-6xbmpiqwia-uc.a.run.app/get_count?vname='+v_name+'&room='+room+'&cameraid='+cameraid+'&roi='+roi
    audience = 'https://spaceutilizationv14-6xbmpiqwia-uc.a.run.app'
    req = urllib.request.Request(endpoint)
    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
    req.add_header("Authorization", f"Bearer {id_token}")
    response = urllib.request.urlopen(req)
    data = json.loads(response.read().decode('utf-8'))
    return data
    #roi_result.append(data)
import concurrent.futures
def save_cordinates_to_bq(roi):
    temp_df = pd.DataFrame(roi)
    temp_df['x'] = temp_df['x'].astype(int)
    temp_df['y'] = temp_df['y'].astype(int)
    temp_df['x'] = temp_df['x'].astype(str)
    temp_df['y'] = temp_df['y'].astype(str)
    temp_df['ROI'] = '(' + temp_df['x'] + ',' +temp_df['y'] + ')'
    temp_df = temp_df.groupby(['id','v_name']).agg(lambda ROI: ','.join(ROI)).reset_index()
    temp_df['id'] = temp_df['id'].astype(str)
    temp_df['ROI'] = '[' + temp_df['ROI'] + ']'
    temp_df = temp_df[['id','v_name','ROI']]
    temp_df['Room'] = 'RoomA'
    temp_df.columns = ['Camera_ID','Video_Nmae','ROI','Room']
    temp_df_2  = temp_df[['Room','Camera_ID','ROI']]
    pandas_gbq.to_gbq(temp_df_2, 'space_utilization.ROI', project_id='springml-gcp-internal-projects',if_exists='append')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(make_authorized_get_request, row['Video_Nmae'],'Room',str(row['Camera_ID']),str(row['ROI'])) for index, row in temp_df.iterrows()]
        return_value = [f.result() for f in futures]
    return return_value
