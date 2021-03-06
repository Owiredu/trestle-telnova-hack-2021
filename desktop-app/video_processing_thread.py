import os
import time
import cv2
import socket
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage
from mylib.centroidtracker import CentroidTracker
from mylib.trackableobject import TrackableObject
import imutils
from imutils.video import FPS
from mylib.mailer import Mailer
from mylib import config
import torch, datetime
from constants import *


#######################################################################


class VideoCaptureThread(QThread):
    """
    This is the thread that captures, processes, controls and delivers the video feeds to the mdi sub windows
    """

    change_pixmap = pyqtSignal(QPixmap, name='change_pixmap')
    send_logger_data = pyqtSignal(dict, name='send_logger_data')

    # argument types: String or int, String, Function
    def __init__(self, camera_id, camera_id_for_db, resource_path_func):
        super().__init__()
        self.video_playing = False
        self.snapshot = False
        self.color = True
        self.save_video = False
        self.resource_path = resource_path_func
        self.camera_id = camera_id
        self.camera_id_for_db = camera_id_for_db
        # initialize the general video writer for saving video
        self.video_writer_fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter()
        # monitor the recording stream so that whenever it is stopped and started, the next one has a different filename
        self.is_file_named = False
        # set the zero matrix to be used as the black background for the time in the frame
        self.black_surface_colored = np.zeros((18, 62, 3), np.uint8)
        self.black_surface_grayscale = np.zeros((18, 62), np.uint8)
        # boolean to show/hide time in frames
        self.time_visible = True
        # boolean to turn on/off people counting
        self.counting_enabled = False
        # object detection and tracking variables
        self.confidence = 0.5
        self.skip_frames = 10
        # self.net = cv2.dnn.readNetFromCaffe(self.prototxt, self.model)
        self.net = torch.hub.load('yolov5', 'custom', 'yolov5/best.pt', source="local")
        # self.net = torch.hub.load('yolov5', 'custom', 'yolov5/retrained_models/trial_train_retrain/best.pt', source="local")
        # centroid tracker variables
        self.centroid_tracker = CentroidTracker(maxDisappeared=10, maxDistance=50)
        self.trackers = []
        self.trackable_objects = {}
        # initialize the total number of frames processed, thus for, along with the total number of objects that have been
        # moved either up or down
        self.total_frames = 0
        self.total_down = 0
        self.total_up = 0
        self.x = []
        self.empty = []
        self.empty1 = []
        # start the frames per second throughput estimator
        self.fps_estimator = FPS().start()
        # define prescribed maximum width and height of frames
        self.desired_width = 400
        self.desired_height = 300
        # initialize the previously logged data
        self.prev_logger_data = {
            'timestamp': '',
            'year': '',
            'month': '',
            'day': '',
            'cam_id': '',
            'cam_data': {'down': 0, 'up': 0}
        }

    def prep_video_capture(self, buffer_size=10):  # argument types: int, int
        """
        This method prepares the video capture
        """
        # open video stream from selected camera
        self.vid_capture = cv2.VideoCapture(self.camera_id)
        # set the buffersize
        self.vid_capture.set(cv2.CAP_PROP_BUFFERSIZE, buffer_size)
        # get the resolution
        self.frame_res = int(self.vid_capture.get(3)), int(self.vid_capture.get(4))

    def start_capture(self):
        """
        This method starts the video capture
        """
        self.video_playing = True

    def stop_capture(self):
        """
        This method stops the video capture
        """
        self.video_playing = False

    def take_snapshot(self, camera_id):  # argument types: String or int
        """
        This method takes a snapshot
        """
        # get current time, extract the date from and create the folder if it does not exist. Name the image with the time value
        time_taken = time.time()
        current_date = time.strftime('%Y-%m-%d', time.localtime(int(time_taken)))
        os.makedirs(SNAPSHOTS_BASE_DIR + os.sep + current_date, exist_ok=True)
        self.image_path = SNAPSHOTS_BASE_DIR + os.sep + current_date + os.sep + str(camera_id) + '_' + str(time_taken) + '.jpg'
        # enable snapshot
        self.snapshot = True

    def abort_snapshot(self):
        """
        This method stops the snapshot
        """
        self.snapshot = False

    def to_grayscale(self):
        """
        This method switches the video from colored to grayscale
        """
        self.color = False

    def to_colored(self):
        """
        This method switches the video from colored to grayscale
        """
        self.color = True

    def is_color(self):
        """
        This method returns the mode - whether colored or grayscale
        """
        return self.color

    def internet_conn_available(self):
        """
        This method checks if there is internet connection
        """
        try:
            socket.create_connection(("www.google.com", 80))
            return True
        except:
            pass
        return False

    def get_image_path(self):
        """
        This method returns the path of the snapshot
        """
        return self.image_path

    # argument types: String or int
    def activate_vid_saving_to_disk(self, camera_id):
        """
        This method starts saving the video to the local drive
        """
        # get current time, extract the date from and create the folder if it does not exist.
        # Name the video with the time value
        time_taken = time.time()
        current_date = time.strftime(
            '%Y-%m-%d', time.localtime(int(time_taken)))
        os.makedirs(SAVED_VIDEOS_BASE_DIR + os.sep + current_date, exist_ok=True)
        self.video_path = SAVED_VIDEOS_BASE_DIR + os.sep + current_date + os.sep + str(camera_id) + '_' + str(time_taken) + '.avi'
        # enable video recording
        self.save_video = True
        self.is_file_named = True

    def toggle_embedded_time(self):
        """
        This method enables and disables the embedded time
        """
        if self.time_visible:
            self.time_visible = False
        else:
            self.time_visible = True

    def save_video_stream_to_file(self, frame):  # argument types: Mat
        """
        This method saves the video when save is enabled
        """
        if self.save_video:
            if self.is_file_named:
                # open video recording
                self.video_writer.open(self.video_path, self.video_writer_fourcc, self.fps, (frame.shape[1], frame.shape[0]), self.is_color())
                self.is_file_named = False
            # write the current time on the frame with a black background at the bottom left corner
            if self.time_visible:
                frame[frame.shape[0]-18:frame.shape[0], 0:62] = self.black_surface_colored
                cv2.putText(frame, time.strftime('%H:%M:%S', time.localtime(time.time())),
                            (2, frame.shape[0]-5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.4, (255, 255, 255), 1, cv2.LINE_AA)
            # write the frame
            self.video_writer.write(frame)
        else:
            self.video_writer.release()
            self.is_file_named = False

    def stop_saving_vid_to_disk(self):
        """
        This method stops saving video to local drive
        """
        self.save_video = False

    def calc_delay_for_vid_file(self):
        """
        This method calculates the delay for video files
        """
        # check if the video is streaming from a video file or a camera
        if not str(self.camera_id).isdigit() and not str(self.camera_id).startswith('http') and not str(self.camera_id).startswith('rtsp'):
            # calculate the delay to be used for video stream if it is a video file
            fps = self.vid_capture.get(5)  # get fps
            if fps > 0:
                return (20 / fps) * 0.05  # 20 fps requires 0.05 seconds delay
            else:
                return 20

    def convertToRGB(self, frame):  # argument types: Mat
        """
        This method converts bgr image to rgb
        """
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def convertToGRAY(self, frame):  # argument types: Mat
        """
        This method converts bgr image to grayscale
        """
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def rectangle(self, frame, rect):  # argument types: Mat, list
        """
        This method draws a rectangle around the detected face
        """
        (x, y, w, h) = rect
        cv2.rectangle(frame, (x-10, y-10), (w+10, h+10),(0, 255, 0), 2, cv2.LINE_AA)

    def putText(self, frame, text, coord):  # argument types: Mat, String, list
        """
        This method writes the id of the recognized person with the rectangle about the face
        """
        cv2.putText(frame, str(text), coord, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)

    def line(sel, frame, coords):
        """
        This method draws a line of the frame
        """
        cv2.line(frame, coords[0], coords[1], (0, 0, 255), 3, cv2.LINE_AA)

    def circle(sel, frame, center, radius):
        """
        This method draws a line of the frame
        """
        cv2.circle(frame, center, radius, (255, 255, 255), 3, cv2.LINE_AA)

    def start_counting(self):
        """
        Starts counting the people
        """
        self.counting_enabled = True

    def stop_counting(self):
        """
        Starts counting the people
        """
        self.counting_enabled = False

    def run(self):
        """
        This method runs all the processes
        """
        try:
            # get the start time
            self.start_time = time.time()
            # set the frame count for url stream sources
            self.frame_from_url_source = None
            # set loading image
            self.change_pixmap.emit(QPixmap(self.resource_path('icons' + os.sep + 'loading_vid.jpg')))
            # prepare video capture
            self.prep_video_capture()
            # calculate the delay for video file
            self.delay = self.calc_delay_for_vid_file()
            # set fps checker
            is_fps_set = False
            # run video capture loop
            while self.video_playing:
                # get the frames
                ret, frame = self.vid_capture.read()
                # get the fps
                if not is_fps_set:
                    self.fps = self.vid_capture.get(5)
                    is_fps_set = True
                # if a valid frame was returned ...
                if ret:
                    #########
                    # resize the frame is it is larger that 400 in width
                    original_frame = frame.copy()
                    frame = imutils.resize(frame, width=500)
                    frame = self.convertToRGB(frame)
                    self.desired_width = frame.shape[1]
                    self.desired_height = frame.shape[0]

                    # initialize the current status along with our list of bounding
                    # box rectangles returned by either (1) our object detector or
                    # (2) the correlation trackers
                    status = 'Waiting'
                    rects = []

                    #########
                    # get frame count frame if the video stream source is url
                    if not str(self.camera_id).isdigit() and str(self.camera_id).startswith('http') or str(self.camera_id).startswith('rtsp'):
                        self.frame_from_url_source = ret

                    #########
                    # save snapshot
                    if self.snapshot:
                        # if the snapshot method is called, then save the current frame
                        # write the rbg image
                        cv2.imwrite(self.image_path, original_frame)
                        # end snapshot
                        self.abort_snapshot()

                    #########
                    # get grayscale and rgb images from frame
                    gray_image = self.convertToGRAY(frame)
                    rgb_image = self.convertToRGB(frame)

                    if self.counting_enabled:
                        #########
                        # perform object detection and tracking
                        # Reference for detection, tracking and counting algorithm: https://github.com/saimj7/People-Counting-in-Real-Time

                        # check to see if we should run a more computationally expensive
                        # object detection method to aid our tracker
                        if self.total_frames % self.skip_frames == 0:
                            # set the status and initialize our new set of object trackers
                            status = "Detecting"
                            self.trackers = []
                            
                            # perform detection on frame
                            results = self.net(frame)
                            # get the results as a pandas dataframe
                            result_df = results.pandas().xyxy[0]
                            # filter out 'person' detections
                            persons = result_df[result_df["name"] == "person"]

                            # loop over the detections
                            for i in range(persons.shape[0]):
                                # get a detected person detection data
                                person_row = persons.iloc[i]
                                xmin = person_row["xmin"]
                                ymin = person_row["ymin"]
                                xmax = person_row["xmax"]
                                ymax = person_row["ymax"]
                                confidence = person_row["confidence"]

                                # filter out weak detections by requiring a minimum
                                # confidence
                                if confidence > self.confidence:

                                    # compute the (x, y)-coordinates of the bounding box
                                    # for the object
                                    startX, startY, endX, endY = int(xmin), int(ymin), int(xmax), int(ymax)

                                    # create the tracker
                                    csrt_tracker = cv2.TrackerCSRT_create()
                                    csrt_tracker.init(rgb_image, (startX, startY, endX - startX, endY - startY))

                                    # add the tracker to the list of trackers
                                    self.trackers.append(csrt_tracker)

                                QApplication.processEvents()

                        # otherwise, we should utilize our object *trackers* rather than
                        # object *detectors* to obtain a higher frame processing throughput
                        else:
                            # loop over the trackers
                            for tracker in self.trackers:
                                # set the status of our system to be 'tracking' rather
                                # than 'waiting' or 'detecting'
                                status = "Tracking"

                                # grab the new bounding box coordinates of the object
                                (success, box) = tracker.update(rgb_image)
                                # check to see if the tracking was a success
                                if success:
                                    (x, y, w, h) = [int(v) for v in box]
                                    startX, startY, endX, endY = int(x), int(y), int(x + w), int(y + h)
                                    # add the bounding box coordinates to the rectangles list
                                    rects.append((startX, startY, endX, endY))

                                # add the bounding box coordinates to the rectangles list
                                # rects.append((startX, startY, endX, endY))

                                QApplication.processEvents()
                        
                        # draw a horizontal line in the center of the frame -- once an
                        # object crosses this line we will determine whether they were
                        # moving 'up' or 'down'
                        self.line(frame, ((0, self.desired_height // 2), (self.desired_width, self.desired_height // 2)))
                        # self.putText(frame, "-Prediction border - Entrance-", (10, self.desired_height - ((i * 20) + 150)))

                        # use the centroid tracker to associate the (1) old object
                        # centroids with (2) the newly computed object centroids
                        objects = self.centroid_tracker.update(rects)

                        # loop over the tracked objects
                        for (objectID, centroid) in objects.items():
                            # check to see if a trackable object exists for the current
                            # object ID
                            to = self.trackable_objects.get(objectID, None)

                            # if there is no existing trackable object, create one
                            if to is None:
                                to = TrackableObject(objectID, centroid)

                            # otherwise, there is a trackable object so we can utilize it
                            # to determine direction
                            else:
                                # the difference between the y-coordinate of the *current*
                                # centroid and the mean of *previous* centroids will tell
                                # us in which direction the object is moving (negative for
                                # 'up' and positive for 'down')
                                y = [c[1] for c in to.centroids]
                                direction = centroid[1] - np.mean(y)
                                to.centroids.append(centroid)

                                # check to see if the object has been counted or not
                                if not to.counted:
                                    # if the direction is negative (indicating the object
                                    # is moving up) AND the centroid is above the center
                                    # line, count the object
                                    if direction < 0 and centroid[1] < self.desired_height // 2:
                                        self.total_up += 1
                                        self.empty.append(self.total_up)
                                        to.counted = True

                                    # if the direction is positive (indicating the object
                                    # is moving down) AND the centroid is below the
                                    # center line, count the object
                                    elif direction > 0 and centroid[1] > self.desired_height // 2:
                                        self.total_down += 1
                                        self.empty1.append(self.total_down)
                                        #print(empty1[-1])
                                        # if the people limit exceeds over threshold, send an email alert
                                        if sum(self.x) >= config.Threshold:
                                            cv2.putText(frame, "-ALERT: People limit exceeded-", (10, frame.shape[0] - 80),
                                                cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)
                                            if config.ALERT:
                                                print("[INFO] Sending email alert..")
                                                Mailer().send(config.MAIL)
                                                print("[INFO] Alert sent")

                                        to.counted = True
                                        
                                    self.x = []
                                    # compute the sum of total people inside
                                    self.x.append(len(self.empty1)-len(self.empty))

                            # store the trackable object in our dictionary
                            self.trackable_objects[objectID] = to

                            # draw both the ID of the object and the centroid of the
                            # object on the output frame
                            text = "ID {}".format(objectID)
                            self.putText(frame, text, (centroid[0] - 10, centroid[1] - 10))
                            self.circle(frame, (centroid[0], centroid[1]), 4)

                            QApplication.processEvents()

                        # construct a tuple of information we will be displaying on the
                        info = [
                            ("Up", self.total_up),
                            ("Down", self.total_down),
                            ("Status", status),
                            ("Up-Down Difference", abs(sum(self.x)))
                        ]

                        # Display the output
                        for (i, (k, v)) in enumerate(info):
                            text = "{}: {}".format(k, v)
                            self.putText(frame, text, (10, self.desired_height - ((i * 20) + 30)))

                            QApplication.processEvents()

                        # send current log data to the main thread to be saved
                        now = datetime.datetime.now()
                        export_data = {
                            'down': self.total_down, 
                            'up': self.total_up
                        }
                        logger_data = dict()
                        logger_data['timestamp'] = now.ctime()
                        logger_data['year'] = str(now.year)
                        logger_data['month'] = str(now.month)
                        logger_data['day'] = str(now.day)
                        logger_data['cam_id'] = self.camera_id_for_db
                        logger_data['cam_data'] = export_data
                        # check if the current log data is the same as the previous
                        same = all(
                            [
                                self.prev_logger_data['cam_data']['down'] == logger_data['cam_data']['down'],
                                self.prev_logger_data['cam_data']['up'] == logger_data['cam_data']['up']
                            ]
                        )
                        # send log data if it is different from the previous one
                        if not same:
                            self.send_logger_data.emit(logger_data)
                            self.prev_logger_data = logger_data

                        # increment the total number of frames processed thus far and
                        # then update the FPS counter
                        self.total_frames += 1
                        self.fps_estimator.update()

                        if config.Timer:
                            # Automatic timer to stop the live stream. Set to 8 hours (28800s).
                            self.end_time = time.time()
                            num_seconds=(self.end_time - self.start_time)
                            if num_seconds > 10:
                                break

                        # # stop the timer and display FPS information
                        # self.fps_estimator.stop()
                        # print("[INFO] elapsed time: {:.2f}".format(self.fps_estimator.elapsed()))
                        # print("[INFO] approx. FPS: {:.2f}".format(self.fps_estimator.fps()))

                    #########
                    # embed time in frame if enabled
                    if self.time_visible:
                        # create black background
                        frame[frame.shape[0]-18:frame.shape[0], 0:62] = self.black_surface_colored
                        if self.is_color():
                            rgb_image[rgb_image.shape[0]-18:rgb_image.shape[0], 0:62] = self.black_surface_colored
                            # write time
                            cv2.putText(rgb_image, time.strftime('%H:%M:%S', time.localtime(time.time())),
                                        (2, rgb_image.shape[0] - 5), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.4, (255, 255, 255), 1, cv2.LINE_AA)
                            cv2.putText(frame, time.strftime('%H:%M:%S', time.localtime(time.time())),
                                        (2, frame.shape[0] - 5), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.4, (255, 255, 255), 1, cv2.LINE_AA)
                        else:
                            gray_image[gray_image.shape[0]-18:gray_image.shape[0],
                                       0:62] = self.black_surface_grayscale
                            # write time
                            cv2.putText(gray_image, time.strftime('%H:%M:%S', time.localtime(time.time())),
                                        (2, gray_image.shape[0] - 5), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.4, (255, 255, 255), 1, cv2.LINE_AA)
                            cv2.putText(frame, time.strftime('%H:%M:%S', time.localtime(time.time())),
                                        (2, frame.shape[0] - 5), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.4, (255, 255, 255), 1, cv2.LINE_AA)

                    #########
                    # save video to file
                    # write the colored frame and write the time on it
                    self.save_video_stream_to_file(original_frame)

                    #########
                    # send the frame to window for display
                    # get grayscale and rgb images from frame
                    gray_image = self.convertToGRAY(frame)
                    rgb_image = frame.copy()

                    if not self.color:
                        # convert the grayscale image into a pyqt image
                        qimage = QImage(gray_image.data, gray_image.shape[1], gray_image.shape[0], QImage.Format_Grayscale8)
                    else:
                        # convert the bgr image into a pyqt image
                        qimage = QImage(rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QImage.Format_RGB888)
                    
                    # create the QPixmap from the QImage
                    qpixmap = QPixmap.fromImage(qimage)
                    # send the pixmap as a signal to the caller (the label in the mdi sub window)
                    self.change_pixmap.emit(qpixmap)

                    #########
                    # check if the video is streamig from a video file of a camera
                    if not str(self.camera_id).isdigit() and not str(self.camera_id).startswith('http') and not str(self.camera_id).startswith('rtsp'):
                        # if the stream is from a video file, delay the playback to normal speed relative to its fps
                        # and enhance the fps to increase speed during facial recognition
                        time.sleep(self.delay)
                else:
                    # stop other running processes
                    self.stop_saving_vid_to_disk()
                    self.abort_snapshot()
                    self.stop_capture()

                QApplication.processEvents()

            # if the given stream source was url, check if any frame was retrieved. If not, display a unique error message
            if not str(self.camera_id).isdigit() and str(self.camera_id).startswith('http') or str(self.camera_id).startswith('rtsp'):
                if not self.internet_conn_available():
                    self.change_pixmap.emit(QPixmap(self.resource_path('icons' + os.sep + 'conn_error.jpg')))
                elif self.frame_from_url_source is None:
                    self.change_pixmap.emit(QPixmap(self.resource_path('icons' + os.sep + 'no_vid_error.jpg')))
                else:
                    self.change_pixmap.emit(QPixmap(self.resource_path('icons' + os.sep + 'default_camera_view.png')))
            else:
                # set restart image after video from camera or local file is done playing or stopped by user
                self.change_pixmap.emit(QPixmap(self.resource_path('icons' + os.sep + 'default_camera_view.png')))
            # when the video stream is stopped, release the camera and its related resources
            if self.save_video:
                self.video_writer.release()
                self.is_file_named = False
            self.vid_capture.release()
        except Exception as e:
            print(e)
            #raise Exception("Camera not accessible")
            self.change_pixmap.emit(QPixmap(self.resource_path('icons' + os.sep + 'conn_error.jpg')))
