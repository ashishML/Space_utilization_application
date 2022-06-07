from flask import Flask, request
import json
import ast
app = Flask(__name__)



@app.route("/get_count")
def get_people_count():
    video_name = request.args.get('vname')
    print(video_name)
    room = request.args.get('room')
    print(room)
    camera_id = request.args.get('cameraid')
    print(camera_id)
    roi = request.args.get('roi')
    # print(roi)

    roi = ast.literal_eval(roi)
    print(roi[1],roi[2])
    print(type(roi[1]))
    # status= main(name, room, camera_id, roi)
    return json.dumps({'status':'success'})

if __name__ == "__main__":
	app.run(debug=True)
