from datetime import datetime
import os
import time
import requests
import json
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from constants import *


class PostUpdateThread(QThread):

    def __init__(self):
        super().__init__()
        self.post_url = "http://127.0.0.1:5000/get_update"
        self.year = datetime.now().year
        self.wait_time = UPDATE_WAIT_TIME # seconds

    def is_update_available(self):
        """
        Checks if the json database has been updated and return the year
        """
        year = [file_name.split('.')[0] for file_name in os.listdir(DATABASES_BASE_DIR) if file_name.endswith(UPDATE_NOTIFIER_EXTENSION)]
        if len(year) > 0:
            return year[0]
        return False

    def post_update(self):
        """
        Posts the update to the server
        """
        # load data from json data file
        json_file = open(DATABASES_BASE_DIR + os.sep + str(self.year) + '_today.json', 'r')
        json_data = json.load(json_file)
        json_file.close()
        # post data to server
        response = requests.post(self.post_url, json=json_data)
        # return response
        if response.status_code == 200:
            return True
        return False

    def run(self):
        while True:
            try:
                # check if a new update is available before posting
                year =  self.is_update_available()
                if year:
                    # set the current year to the retrieved one
                    self.year = year
                    # post update
                    ret = self.post_update()
                    # set the wait time depending on whether the post was successful or not
                    if ret:
                        self.wait_time = UPDATE_WAIT_TIME
                    else:
                        self.wait_time = UPDATE_RETRY_TIME
                    # remove update notification
                    os.remove(DATABASES_BASE_DIR + os.sep + self.year + UPDATE_NOTIFIER_EXTENSION)
            except:
                pass
            # wait for a specified number of seconds before running next update post
            time.sleep(self.wait_time)

            QApplication.processEvents()
