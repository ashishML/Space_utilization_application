from flask import Flask,jsonify, request
app = Flask(__name__)
import cv2
import os


IMAGE_FOLDER = os.path.join('static', 'images')
app.config['UPLOAD_FOLDER'] = IMAGE_FOLDER

VIDEO_FOLDER = os.path.join('static', 'videos')
app.config['VIDEO_UPLOAD_FOLDER'] = VIDEO_FOLDER


@app.route('/upload_video',methods = ['POST'])
def video_upload():
    response_dict={"status": True, "message": "video saved successfully",'data':{}}
    if request.method == 'POST':
        video_file =request.files['file']
        if not video_file:
            response_dict['status'] = False
            response_dict['message'] = 'there is no file in form!'
            return jsonify(response_dict)
        video_path = os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], video_file.filename)
        video_file.save(video_path)
        return jsonify(response_dict)


@app.route('/get_frame',methods = ['GET'])
def video_frame_capture():
    response_dict={"status": True, "message": "",'data':{}}
    if request.method == 'GET':
        try:
            video_obj = cv2.VideoCapture(os.path.join(app.config['VIDEO_UPLOAD_FOLDER'],'test_video.MOV'))
            success = 1
            while success:
                success, image = video_obj.read()
                cv2.imwrite('./static/images/video_01.png',image)
                img_path = '/static/images/video_01.png'
                response_dict['data'] = img_path
                break
            return jsonify(response_dict)
        except:
            response_dict['status'] = False
            response_dict['message'] = 'there is no video files!'
            return jsonify(response_dict)









if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug = True)

