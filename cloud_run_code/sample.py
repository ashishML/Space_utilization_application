import pandas
import os
import pandas_gbq
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="creds.json"

project_id = 'springml-gcp-internal-projects'
# table_id = 'space_utilization.ROI'

# # df = pandas.DataFrame(
# #     [{
# #         "Room": "Room1",
# #         "Camera_ID": "Room1_A",
# #         "ROI":'[(5,3),(67,47),(89.189),(133,148),(859,780)]'
# #     }]
# # )

# # table_schema=[{'name': 'Room','type': 'STRING'},
# #                                    {'name': 'Camera_ID','type': 'STRING'},
# #                                    {'name': 'ROI','type': 'STRING'}]

# # pandas_gbq.to_gbq(df, table_id, project_id=project_id, if_exists='append', table_schema=table_schema)



# sql = """
#     SELECT *
#     FROM `space_utilization.ROI`
#     WHERE Room = 'Room1' and Camera_ID = 'Room1_A'
#     LIMIT 100
# """

# # Run a Standard SQL query using the environment's default project
# df = pandas.read_gbq(sql, dialect='standard')

# # Run a Standard SQL query with the project set explicitly

# df = pandas.read_gbq(sql, project_id=project_id, dialect='standard')
# print(df.shape)


import csv
from io import BytesIO
import cv2
import datetime


from google.cloud import storage

storage_client = storage.Client()
bucket = storage_client.get_bucket('space_utilization_application')

blob = bucket.blob('videos/pexels-arvin-latifi-6466763.mp4')
blob = blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
video_obj = cv2.VideoCapture(blob)

# blob.download_to_filename('pexels-arvin-latifi-6466763.mp4')
# blob = blob.download_as_string()	
# print(type(blob))
# cap = cv2.VideoCapture(BytesIO(blob))
# print(cap)

# cap = cv2.VideoCapture()
# cap.open(blob,0)

# blob = blob.decode('utf-8')


# blob = np.frombuffer(blob, np.uint8)  #tranform bytes to string here
# img_np = cv2.imdecode(blob, cv2.IMREAD_COLOR) 
