import os, json 
from posixpath import expanduser
from flask import Flask, render_template, request, Response
import util
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    try:
        # load the current year's data and send current day's data to webpage
        base_dir = os.path.dirname(__file__)
        folder = "static" + os.sep + "count_data"
        data_dir = os.path.join(base_dir, folder)
        os.makedirs(data_dir, exist_ok=True)
        
        data = dict()
        with open(os.path.join(data_dir, "2021.json")) as f:
            data = json.load(f)
        cur_date = datetime.now()
        cur_day_data = data.get(str(cur_date.month), dict()).get(str(str(cur_date.day)), {
            "total":{
                "timestamp":cur_date.ctime(),
                "in": "0",
                "out": "0",
                "cur_in": "0"
            }}
        )
        # print(cur_day_data)
        return render_template("index.html", data=cur_day_data)
    except Exception as e:
        print(e)
        return Response(json.dumps({'status':'FAIL', 'message': 'Fatal error'}), status=400, mimetype='application/json')



@app.route("/get_update", methods=['POST'])
def get_update():
    try:
        # get posted json data
        json_data = request.get_json(force=True)
        # get the file path
        base_dir = os.path.dirname(__file__)
        folder = "static" + os.sep + "count_data"
        data_dir = os.path.join(base_dir, folder)
        os.makedirs(data_dir, exist_ok=True)
        year = list(json_data.keys())[0]
        json_file_path = os.path.join(data_dir, f"{year}.json")
        # remove year from json data and keep only the month, day and camera data since year no more needed
        json_data = json_data[year]
        # create the data holder dictionary
        data = dict()
        # get the month and day from the data received from the post
        cur_month = list(json_data.keys())[0]
        cur_day = list(json_data[cur_month].keys())[0]
        if os.path.exists(json_file_path):
            # load the current year's data and update it
            # open the json database and read it
            fr = open(json_file_path, 'r')
            data = json.load(fr)
            fr.close()
            # update the json database
            if not cur_month in data:
                data[cur_month] = dict()
            data[cur_month][cur_day] = json_data[cur_month][cur_day]
        else:
            # update the json database
            data[cur_month] = dict()
            data[cur_month][cur_day] = json_data[cur_month][cur_day]
        # write the updated json data
        fw = open(json_file_path, 'w')
        fw.write(json.dumps(data, indent=4))
        fw.close()

        return Response(json.dumps({'status':'SUCCESS', 'message': 'Posted successfully'}), status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(json.dumps({'status':'FAIL', 'message': 'Fatal error'}), status=400, mimetype='application/json')