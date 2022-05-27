import os
import datetime
from google.cloud import storage
from app import app
from base64 import b64encode
from google.cloud import bigquery
import urllib
import google.auth.transport.requests

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]= 'creds.json'
os.environ["GCLOUD_PROJECT"]= "springml-gcp-internal-projects"

client = storage.Client()



def make_authorized_get_request(v_name,room,cameraid,roi):
    
    endpoint ='https://spaceutilizationv4-6xbmpiqwia-uc.a.run.app/get_count?vname='+v_name+'.mp4&room='+room+'&cameraid='+cameraid+'&roi='+roi
    audience = 'https://spaceutilizationv5-6xbmpiqwia-uc.a.run.app'
    req = urllib.request.Request(endpoint)
    auth_req = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(auth_req, audience)
    req.add_header("Authorization", f"Bearer {id_token}")
    response = urllib.request.urlopen(req)
    return response.read()


def upload_file_to_bucket(file):
    name = file.filename
    data = file.read()
    remote_path = 'videos' + "/" + name
    storage_client = storage.Client.from_service_account_json('creds.json')
    bucket = storage_client.get_bucket(app.config['BUCKET_NAME'])
    blob = bucket.blob(remote_path)
    blob.upload_from_string(data, content_type = 'video/mp4', timeout=600)
    return 

def read_file_from_bucket(video_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(app.config['BUCKET_NAME'])
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

def read_file_to_bucket(video_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(app.config['BUCKET_NAME'])
    blob = bucket.blob('videos/'+video_name+'.mp4')
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



def read_image_from_bucket(names):
    bucket = client.get_bucket(app.config['BUCKET_NAME'])
    blobs = bucket.list_blobs(prefix='first_frame/'+names)
    for idx, bl in enumerate(blobs):
        data = bl.download_as_string()
        b = b64encode(data).decode("utf-8")
    return b

def big_query_test(cord_data):
    rows =[]
    room_count = 0
    for each in cord_data:
        out={}
        out['Camera_ID'] = room_count
        out['ROI'] =  str(each.get(room_count))
        out['Room']='room'+'-0'+str(room_count)
        rows.append(out)
        room_count+=1
    client = bigquery.Client()
    table_id = "springml-gcp-internal-projects.space_utilization.ROI"
    
    errors = client.insert_rows_json(table_id, rows)
    if errors == []:
        return True
    else:
        return False
    


def roi_cordinates(data):
    val = []
    for each in data:
        result = {}
        if each.get('id') in result.keys():
            result[each.get('id')].append((round(each.get('x')),round(each.get('y'))))
            result['v_name'] =each.get('v_name')
        else:
            result[each.get('id')] = [(round(each.get('x')),round(each.get('y')))]
            result['v_name'] =each.get('v_name')
        val.append(result)
    return val
