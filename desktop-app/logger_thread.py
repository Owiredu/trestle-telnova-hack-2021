import os
import json
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
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
        # total statistics
        total_stats = {
            "timestamp": export_data['timestamp'],
            "down": 0,
            "up": 0,
            "diff": 0
        }
        # open json database files for today and the year
        year_json_file = DATABASES_BASE_DIR + os.sep + export_data['year'] + '.json'
        today_json_file = DATABASES_BASE_DIR + os.sep + export_data['year'] + '_today' + '.json'
        # write update to the year json database file
        year_data = dict()
        if os.path.exists(year_json_file):
            # load the current year's data and update it
            # open the json database and read it
            fr = open(year_json_file, 'r')
            year_data = json.load(fr)
            fr.close()
            # update the json database
            if not export_data['month'] in year_data:
                year_data[export_data['month']] = dict()
            if not export_data['day'] in year_data[export_data['month']]:
                year_data[export_data['month']][export_data['day']] = dict()
            year_data[export_data['month']][export_data['day']][export_data['cam_id']] = export_data['cam_data']
        else:
            # update the json database
            year_data[export_data['month']] = dict()
            year_data[export_data['month']][export_data['day']] = dict()
            year_data[export_data['month']][export_data['day']][export_data['cam_id']] = export_data['cam_data']
            
        # get the total statistics
        day_data = year_data[export_data['month']][export_data['day']]
        list_of_cam_ids = list(day_data.keys())
        if list_of_cam_ids.__contains__('total'):
            list_of_cam_ids.remove('total')

        total_down = 0
        total_up = 0
        for cam_id in list_of_cam_ids:
            total_down += day_data[cam_id]['down']
            total_up += day_data[cam_id]['up']
        total_stats['down'] = total_down
        total_stats['up'] = total_up
        total_stats['diff'] = abs(total_down - total_up)

        # update day data in year database with total statistics
        year_data[export_data['month']][export_data['day']]['total'] = total_stats

        # save the updated years json database
        fw = open(year_json_file, 'w')
        fw.write(json.dumps(year_data, indent=4))
        fw.close()

        # save today's date separately to be sent as an update
        today_updated_data = {
            export_data['year']: {
                export_data['month']: {
                    export_data['day']: year_data[export_data['month']][export_data['day']]
                }
            }
        }
        fw = open(today_json_file, 'w')
        fw.write(json.dumps(today_updated_data, indent=4))
        fw.close()

        # create the update notifier file
        open(DATABASES_BASE_DIR + os.sep + export_data['year'] + UPDATE_NOTIFIER_EXTENSION, 'w')

    def run(self):
        while True:
            try:
                if not self.data_queue.empty():
                    self.update_db()
            except:
                pass
            QApplication.processEvents()