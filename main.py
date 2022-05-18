from flask import Flask,jsonify, request, Response, render_template
from google.cloud import storage
import numpy as np
app = Flask(__name__)
import cv2
import os


IMAGE_FOLDER = os.path.join('static', 'images')
app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_FOLDER

VIDEO_FOLDER = os.path.join('static', 'videos')
app.config['VIDEO_UPLOAD_FOLDER'] = VIDEO_FOLDER


@app.route('/upload_video',methods = ['POST','GET'])
def video_upload():
    response_dict={"status": True, "message": "video saved successfully",'data':{}}
    if request.method == 'POST':
        video_file = request.files.getlist("file")
        if not video_file:
            response_dict['status'] = False
            response_dict['message'] = 'file not available!'
            return jsonify(response_dict)
        for video in video_file:
            #upload to gcp

            video.save(os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], video.filename))
        return jsonify(response_dict)



@app.route('/get_video_names',methods = ['GET'])
def list_of_video_names():
    response_dict={"status": True, "message": "",'data':{}}
    if request.method == 'GET':
        video_names = os.listdir(app.config['VIDEO_UPLOAD_FOLDER'])
        if video_names:
            response_dict['data'] =[v.split('.')[0] for v in video_names]
        else:
            response_dict['status'] = False
            response_dict['message'] = 'files not available!'
        return jsonify(response_dict)


@app.route('/get_frame',methods = ['GET'])
def video_frame_capture():
    response_dict={"status": True, "message": "",'data':{}}
    if request.method == 'GET':
        try:
            video_name = request.args.get('v_name') #path from gcp
            video_obj = cv2.VideoCapture(os.path.join(app.config['VIDEO_UPLOAD_FOLDER'],video_name+'.mp4'))
            success = 1
            v_name = video_name.split('.')[0]
            while success:
                success, image = video_obj.read()
                cv2.imwrite('./static/images/'+v_name+'.png',image)
                response_dict['data'] ='/static/images/'+v_name+'.png'
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
        vertices = np.array([(140,154),(460,121),(600,369),(25,381)])
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



def upload_to_bucket():
    storage_client = storage.Client.from_service_account_json('springml-gcp-credentials.json')
    bucket = storage_client.get_bucket('space_utilization_application')
    blob_name = "%s/%s"%('','test_video.mp4')
    blob = bucket.blob(blob_name)
    with open('video-01.mp4','rb') as f:
        blob.upload_from_file(f)
    return blob.public_url









if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug = True)

