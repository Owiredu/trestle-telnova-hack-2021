import os
import sys
from datetime import datetime
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QThread
from queue import Queue
from constants import *


class LoggerThread(QThread):

    def __init__(self):
        super().__init__()
        self.data_queue = Queue()

    def enqueue(self, data):
        """
        Adds data to the queue
        """
        self.data_queue.put(data)

    def dequeue(self):
        """
        Returns the next item in the queue
        """
        return self.data_queue.get()

    def update_db(self):
        """
        Updates the logger file
        """
        # get the data from the queue
        export_data = self.dequeue()
        # update the json database file
        updated_data = {
            f"{export_data['cam_id']}": export_data['cam_data']
        }
        # open json database files for today and the year
        year_json_file = DATABASES_BASE_DIR + os.sep + export_data['year'] + '.json'
        today_json_file = DATABASES_BASE_DIR + os.sep + export_data['year'] + '_today' + '.json'
        # create the update notifier file
        open(DATABASES_BASE_DIR + os.sep + export_data['year'] + UPDATE_NOTIFIER_EXTENSION, 'w')

    def run(self):
        while True:
            try:
                if not self.data_queue.empty():
                    self.update_db()
            except Exception as e:
                print(e)
            QApplication.processEvents()