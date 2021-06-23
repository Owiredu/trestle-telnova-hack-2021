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
        export_data = self.dequeue()
        print(export_data)
        # create the update notifier file
        open(DATABASES_BASE_DIR + os.sep + export_data['year'] + UPDATE_NOTIFIER_EXTENSION)

    def run(self):
        while True:
            if not self.data_queue.empty():
                self.update_db()
            QApplication.processEvents()