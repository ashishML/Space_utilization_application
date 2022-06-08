from flask import Flask,Blueprint,send_from_directory,jsonify, request, render_template
from app import app
app = Flask(__name__, static_folder='angular/dist/angular')
import cv2
from flask_cors import CORS
from utils import upload_file_to_bucket, get_bucket_file_names, read_file_to_bucket,\
                  upload_image_file_to_bucket, read_image_from_bucket, save_cordinates_to_bq,\
                  check_video_name, get_videos

angular = Blueprint('angular', __name__, template_folder='angular/dist/angular')
app.register_blueprint(angular)

@app.route('/assets/<path:filename>')
def custom_static_for_assets(filename):
    return send_from_directory('angular/dist/angular/assets', filename)


@app.route('/<path:filename>')
def custom_static(filename):
    return send_from_directory('angular/dist/angular/', filename)

@app.route('/')
def index():
    return render_template('index.html')
    
@app.route('/roi_cordinates',methods = ['POST'])
def save_cordinates():
    response_dict={"status": True, "message": "data saved.",'data':{}}
    roi = [{"x":102,"y":103,"id":0,"v_name":"video2.mp4"},{"x":349,"y":569,"id":1,"v_name":"video1.mp4"}]
    try:
        if request.method == 'POST':
            #data = save_cordinates_to_bq(roi)
            data = save_cordinates_to_bq(eval(request.json['roi']))
            if not data:
                response_dict['status'] = False
                response_dict['message'] = 'data not saved!'
            else:
                response_dict['data'] = data
    except:
            response_dict['status'] = False
            response_dict['message'] = 'service unavailable!'
    return jsonify(response_dict)


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


#have to remove the call
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


# API to check video in 'results'
@app.route('/check_video',methods = ['POST'])
def check_video():
    response_dict={"status": True, "message": "",'data':{}}
    if request.method == 'POST':
        video_name = request.json['video_name']
        if not video_name:
            response_dict['data'] = 'NULL'
            response_dict['status'] = False
            response_dict['message'] = 'Null Video Name'
            return jsonify(response_dict)
        else:
            result = check_video_name(video_name)
            if result:
                response_dict['data'] = True
                response_dict['message'] = 'File available'
            else:
                response_dict['data'] = False
                response_dict['message'] = 'File not available'
    return jsonify(response_dict)


# API to display result videos
@app.route('/play_videos',methods = ['GET'])
def play_videos():
    response_dict={"status": True, "message": "",'data':{}}
    if request.method == 'GET':
        v_name = eval(request.args.get('v_name'))
        response_dict['data'] = get_videos(v_name)
        return jsonify(response_dict)


@app.route('/get_frame',methods = ['GET'])
def video_frame_capture():
    response_dict={"status": True, "message": "",'data':{}}
    if request.method == 'GET':
        try:
            result = []
            for names in eval(request.args.get('v_frames')):
                video_obj = cv2.VideoCapture(read_file_to_bucket(names))
                success = 1
                while success:
                    success, image = video_obj.read()
                    img_str = cv2.imencode('.png', image)[1].tobytes()
                    upload_image_file_to_bucket(img_str,names)
                    break
                result.append(read_image_from_bucket(names))
            response_dict['data'] = result
            return jsonify(response_dict)
        except:
            response_dict['status'] = False
            response_dict['message'] = 'there is no video files!'
    return jsonify(response_dict)



#for backend
# @app.route('/upload_video',methods = ['POST','GET'])
# def video_upload():
    
#     response_dict={"status": True, "message": "video saved successfully",'data':{}}
#     if request.method == 'POST':
#         video_file = request.files.getlist('file')
#         if not video_file:
#             response_dict['status'] = False
#             response_dict['message'] = 'file not available!'
#             return jsonify(response_dict)
#         for video in video_file:
#             upload_file_to_bucket(video)
#             if video.filename.split('.')[0] == '':
#                 continue
#         return jsonify(response_dict)



if __name__ == '__main__':
    CORS(app)
    app.run(host='127.0.0.1', port=8080, debug = True)

