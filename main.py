from flask import Flask,jsonify, request, Response, render_template
import numpy as np
from app import app
app = Flask(__name__)
import cv2
import os
from utils import upload_file_to_bucket, get_bucket_file_names, read_file_to_bucket
from flask_cors import CORS


@app.route('/upload_video',methods = ['POST','GET'])
def video_upload():
    response_dict={"status": True, "message": "video saved successfully",'data':{}}
    if request.method == 'POST':
        video_file = request.files
        if not video_file:
            response_dict['status'] = False
            response_dict['message'] = 'file not available!'
            return jsonify(response_dict)
        for video in range(len(video_file)):
            upload_file_to_bucket(request.files[str(video)])
        return jsonify(response_dict)


@app.route('/get_names',methods = ['GET'])
def list_of_video_names():
    response_dict={"status": True, "message": "",'data':{}}
    if request.method == 'GET':
        result ,succ = get_bucket_file_names()
        if succ:
            response_dict['data'] = result
        else:
            response_dict['data'] = False
            response_dict['message'] = 'files not available!'
        return jsonify(response_dict)


@app.route('/get_frame',methods = ['GET'])
def video_frame_capture():
    response_dict={"status": True, "message": "",'data':{}}
    if request.method == 'GET':
        try:
            video_name = request.args.get('v_name')
            video_obj = cv2.VideoCapture(read_file_to_bucket(video_name))
            success = 1
            while success:
                success, image = video_obj.read()
                cv2.imwrite('./static/images/'+video_name+'.png',image)
                response_dict['data'] ='/static/images/'+video_name+'.png'
                break
            return jsonify(response_dict)
        except:
            response_dict['status'] = False
            response_dict['message'] = 'there is no video files!'
            return jsonify(response_dict)

def region_of_interest(img, vertices):
    mask = np.zeros_like(img)
    channel_count = img.shape[2]
    match_mask_color = (255,) * channel_count
    cv2.fillPoly(mask, [vertices], match_mask_color)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image

def gen_frames():
    camera = cv2.VideoCapture('video-01.mp4')
    while True:
        success, frame = camera.read()  # read the camera frame
        frame = cv2.cvtColor(frame,cv2.COLOR_RGB2BGR)
        vertices = np.array([(10, 46), (291, 161), (633, 230), (634, 461), (37, 456), (49, 61), (47, 64)])
        cropped_frame = region_of_interest(frame, vertices)

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', cropped_frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/live')
def index():
    return render_template('index.html')
    
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')









if __name__ == '__main__':
    CORS(app)
    app.run(host='127.0.0.1', port=8080, debug = True)

