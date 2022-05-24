#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, absolute_import

import os
import tensorflow as tf
import keras.backend.tensorflow_backend as KTF

from timeit import time
import warnings
import argparse

import sys
import cv2
import numpy as np
import base64
import requests
import urllib
from urllib import parse
import json
import random
import time
from PIL import Image
from collections import Counter
import operator
import datetime


from yolo_v4 import YOLO4
from deep_sort import preprocessing
from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from tools import generate_detections as gdet
from deep_sort.detection import Detection as ddet

from reid import REID
import copy

import pandas_gbq
from google.cloud import bigquery
bq_client = bigquery.Client.from_service_account_json('creds.json')


from google.cloud import storage
storage_client = storage.Client.from_service_account_json('creds.json')

# Constants
max_cosine_distance = 0.3
nn_budget = None
nms_max_overlap = 0.4

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="creds.json"
project_id = 'springml-gcp-internal-projects'
roi_table_id = 'space_utilization.ROI'


def preProcessVideo(gcp_video_path , room, camera_id):
    print('Reading the file')
    cap = cv2.VideoCapture(gcp_video_path)

def upload_to_GCS():
    pass

def region_of_interest(img, vertices):
    # Define a blank matrix that matches the image height/width.
    mask = np.zeros_like(img)
    # Retrieve the number of color channels of the image.
    channel_count = img.shape[2]
    # Create a match color with the same color channel counts.
    match_mask_color = (255,) * channel_count
    # Fill inside the polygon
    cv2.fillPoly(mask, vertices, match_mask_color)
    # Returning the image only where mask pixels match
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def main(gcp_video_path, room ,camera_id, roi):

    yolo = YOLO4()

    model_filename = 'model_data/models/mars-small128.pb'
    encoder = gdet.create_box_encoder(model_filename,batch_size=1) # use to get feature
    metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
    tracker = Tracker(metric, max_age=100)

    output_frames = []
    output_rectanger = []
    output_areas = []
    output_wh_ratio = []

    is_vis = True


    ############################ Todo save to the GCS bucket output video #####################
    # out_dir = f'videos/output/'
    # print('The output folder is',out_dir)
    # if not os.path.exists(out_dir):
    #     os.mkdir(out_dir)
    ###############################################################################################


    all_frames = []

    bucket = storage_client.get_bucket('space_utilization_application')
    blob = bucket.blob(gcp_video_path)
    video_url = blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')

    # loadvideo = LoadVideo(video_url)
    video_capture = cv2.VideoCapture(video_url)
    # video_capture, frame_rate, w, h = loadvideo.get_VideoLabels()
    while True:
        ret, frame = video_capture.read() 
        if ret != True:
            video_capture.release()
            break

        all_frames.append(frame)

    frame_nums = len(all_frames)
    print('Total_Frames ', frame_nums)

    h = all_frames[0].shape[0] 
    w = all_frames[0].shape[1]



    out_dir = 'temp_results'
    if not  os.path.exists(out_dir):
        os.mkdir(out_dir)
    tracking_path = out_dir+'/completed'+'.avi'
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(tracking_path, fourcc, 2, (w, h))
#     combined_path = out_dir+'allVideos'+'.avi'


#     #Initialize tracking file
    # filename = out_dir+'/tracking.txt'
    # open(filename, 'w')
    
    fps = 0.0
    frame_cnt = 0
    t1 = time.time()
    
    track_cnt = dict()
    images_by_id = dict()
    ids_per_frame = []
    
    all_frames = all_frames[::15]
    print('All_Frames:' , len(all_frames))
    for frame in all_frames:

        # image = Image.fromarray(frame[...,::-1]) #bgr to rgb
        # image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        

        # image = frame
        # frame = cv2.fillPoly(frame, [np.array(roi)], 0)
        frame = region_of_interest(frame, np.array([roi],np.int32))
        boxs = yolo.detect_image(Image.fromarray(frame)) # n * [topleft_x, topleft_y, w, h]
        features = encoder(frame,boxs) # n * 128
        detections = [Detection(bbox, 1.0, feature) for bbox, feature in zip(boxs, features)] # length = n
        text_scale, text_thickness, line_thickness = get_FrameLabels(frame)

        
        # Run non-maxima suppression.
        boxes = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        indices = preprocessing.delete_overlap_box(boxes, nms_max_overlap, scores) #preprocessing.non_max_suppression(boxes, nms_max_overlap, scores)
        detections = [detections[i] for i in indices] # length = len(indices)

        # Call the tracker 
        tracker.predict()
        tracker.update(detections)
        tmp_ids = []
        for track in tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue 
            
            bbox = track.to_tlbr()
            area = (int(bbox[2]) - int(bbox[0])) * (int(bbox[3]) - int(bbox[1]))
            if bbox[0] >= 0 and bbox[1] >= 0 and bbox[3] < h and bbox[2] < w:
                tmp_ids.append(track.track_id)
                if track.track_id not in track_cnt:
                    track_cnt[track.track_id] = [[frame_cnt, int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]), area]]
                    images_by_id[track.track_id] = [frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])]]
                else:
                    track_cnt[track.track_id].append([frame_cnt, int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3]), area])
                    images_by_id[track.track_id].append(frame[int(bbox[1]):int(bbox[3]), int(bbox[0]):int(bbox[2])])
            cv2_addBox(track.track_id,frame,int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3]),line_thickness,text_thickness,text_scale)
            # write_results(filename,'mot',frame_cnt+1,str(track.track_id),int(bbox[0]),int(bbox[1]),int(bbox[2]),int(bbox[3]),w,h)
        ids_per_frame.append(set(tmp_ids))

        # save a frame               
        # if is_vis:
        out.write(frame)
        t2 = time.time()
        
        frame_cnt += 15  # Reading 2 frames per seconds
        print(frame_cnt, '/', frame_nums)

    # if is_vis:
    out.release()
    print('Tracking finished in {} seconds'.format(int(time.time() - t1)))
    print('Tracked video : {}'.format(tracking_path))
    # print('Combined video : {}'.format(combined_path))

    os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"
    reid = REID()
    threshold = 320
    exist_ids = set()
    final_fuse_id = dict()

    print('Total IDs = ',len(images_by_id))

    print('\nWriting videos took {} seconds'.format(int(time.time() - t2)))
    print('Total: {} seconds'.format(int(time.time() - t1)))

    time_now = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    destination_file_path = f'results/{time_now}_{room}_{camera_id}_{gcp_video_path.split("/")[-1]}'
    blob = bucket.blob(destination_file_path)
    blob.upload_from_filename(tracking_path)


    # Insert into the BQ table
    table = bq_client.get_table("{}.{}.{}".format(project_id, 'space_utilization', 'people_count'))
    results = [{"Time":time_now.split('_')[0]+' '+time_now.split('_')[1],"Room":room, "Camera_ID":camera_id, "Count": len(images_by_id)}]
    errors = bq_client.insert_rows_json(table, results)
    print(errors)
    if errors == []:
        print("success")

    




def get_FrameLabels(frame):
    text_scale = max(1, frame.shape[1] / 1600.)
    text_thickness = 1 if text_scale > 1.1 else 1
    line_thickness = max(1, int(frame.shape[1] / 500.))
    return text_scale, text_thickness, line_thickness

def cv2_addBox(track_id, frame, x1, y1, x2, y2, line_thickness, text_thickness,text_scale):
    color = get_color(abs(track_id))
    cv2.rectangle(frame, (x1, y1), (x2, y2),color=color, thickness=line_thickness)
    cv2.putText(frame, str(track_id),(x1, y1+30), cv2.FONT_HERSHEY_PLAIN, text_scale, (0,0,255),thickness=text_thickness)
    
def write_results(filename, data_type, w_frame_id, w_track_id, w_x1, w_y1, w_x2, w_y2, w_wid, w_hgt):
    if data_type == 'mot':
        save_format = '{frame},{id},{x1},{y1},{x2},{y2},{w},{h}\n'
    else:
        raise ValueError(data_type)
    with open(filename, 'a') as f:
        line = save_format.format(frame=w_frame_id, id=w_track_id, x1=w_x1, y1=w_y1, x2=w_x2, y2=w_y2, w=w_wid, h=w_hgt)
        f.write(line)
    #print('save results to {}'.format(filename))

warnings.filterwarnings('ignore')
def get_color(idx):
    idx = idx * 3
    color = ((37 * idx) % 255, (17 * idx) % 255, (29 * idx) % 255)
    return color    




if __name__ =='__main__':
    # os.environ["CUDA_VISIBLE_DEVICES"] = "0,1,2,3"
    # sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto())
    # preProcessVideo('https://storage.cloud.google.com/space_utilization_application/videos/Video1.mp4','','')
    main('videos/VID-20220422-WA0002.mp4','Room2','Room2A',[(0, 194), (0, 350), (640, 350), (640, 250)] )