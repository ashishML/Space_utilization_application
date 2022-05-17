from flask import Flask,jsonify, request
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
            video.save(os.path.join(app.config['VIDEO_UPLOAD_FOLDER'], video.filename))
        return jsonify(response_dict)


@app.route('/get_video_names',methods = ['GET'])
def list_of_video_names():
    # import ipdb;ipdb.set_trace()
    # import ffmpeg
    # os.system("ffmpeg -i {0} -f image2 -vf fps=fps=1 output%d.png".format(filename))
    response_dict={"status": True, "message": "",'data':{}}
    if request.method == 'GET':
        video_names = os.listdir(app.config['VIDEO_UPLOAD_FOLDER'])
        if video_names:
            response_dict['data'] =video_names
        else:
            response_dict['status'] = False
            response_dict['message'] = 'files not available!'
        return jsonify(response_dict)


@app.route('/get_frame',methods = ['GET'])
def video_frame_capture():
    response_dict={"status": True, "message": "",'data':{}}
    if request.method == 'GET':
        try:
            video_name = request.args.get('v_name') 
            video_obj = cv2.VideoCapture(os.path.join(app.config['VIDEO_UPLOAD_FOLDER'],video_name))
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









if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug = True)

