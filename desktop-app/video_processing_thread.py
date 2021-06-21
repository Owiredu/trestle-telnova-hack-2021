import os
import time
import cv2
import socket
import numpy
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtGui import QPixmap, QImage
from db_conn import DbConnection
from constants import *


#######################################################################


class VideoCaptureThread(QThread):
    """
    This is the thread that captures, processes, controls and delivers the video feeds to the mdi sub windows
    """

    change_pixmap = pyqtSignal(QPixmap, name='change_pixmap')

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
        self.black_surface_colored = numpy.zeros((18, 62, 3), numpy.uint8)
        self.black_surface_grayscale = numpy.zeros((18, 62), numpy.uint8)
        # boolean to show/hide time in frames
        self.time_visible = True
        # boolean to turn on/off people counting
        self.counting_enabled = False

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
                if self.is_color():
                    frame[frame.shape[0]-18:frame.shape[0],
                          0:62] = self.black_surface_colored
                else:
                    frame[frame.shape[0]-18:frame.shape[0], 0:62] = self.black_surface_grayscale
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

    def rectangle(self, img, rect):  # argument types: Mat, list
        """
        This method draws a rectangle around the detected face
        """
        (x, y, w, h) = rect
        cv2.rectangle(img, (x-10, y-10), (w+10, h+10),(0, 255, 0), 2, cv2.LINE_AA)

    def putText(self, img, subject_id, rect):  # argument types: Mat, String, list
        """
        This method writes the id of the recognized person with the rectangle about the face
        """
        (x, y, w, h) = rect
        cv2.putText(img, str(subject_id), (x-10, y-15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1, cv2.LINE_AA)

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
            # set the frame count for url stream sources
            self.frame_from_url_source = None
            # set loading image
            self.change_pixmap.emit(QPixmap(self.resource_path('icons' + os.sep + 'loading_vid.jpg')))
            # set model trained to false
            self.is_model_trained = False
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
                    if frame.shape[1] > 400:
                        frame = cv2.resize(frame, (400, 300))

                    #########
                    # get frame count frame if the video stream source is url
                    if not str(self.camera_id).isdigit() and str(self.camera_id).startswith('http') or str(self.camera_id).startswith('rtsp'):
                        self.frame_from_url_source = ret

                    #########
                    # get grayscale and rgb images from frame
                    gray_image = self.convertToGRAY(frame)
                    rgb_image = self.convertToRGB(frame)

                    #########
                    # save snapshot
                    if self.snapshot:
                        # if the snapshot method is called, then save the current frame
                        if self.is_color():
                            # write the rbg image
                            cv2.imwrite(self.image_path, frame)
                        else:
                            # write the grayscale image
                            cv2.imwrite(self.image_path, gray_image)
                        # end snapshot
                        self.abort_snapshot()

                    #########
                    # embed time in frame if enabled
                    if self.time_visible:
                        # create black background
                        if self.is_color():
                            rgb_image[rgb_image.shape[0]-18:rgb_image.shape[0],
                                      0:62] = self.black_surface_colored
                            # write time
                            cv2.putText(rgb_image, time.strftime('%H:%M:%S', time.localtime(time.time())),
                                        (2, rgb_image.shape[0] -
                                         5), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.4, (255, 255, 255), 1, cv2.LINE_AA)
                        else:
                            gray_image[gray_image.shape[0]-18:gray_image.shape[0],
                                       0:62] = self.black_surface_grayscale
                            # write time
                            cv2.putText(gray_image, time.strftime('%H:%M:%S', time.localtime(time.time())),
                                        (2, gray_image.shape[0] -
                                         5), cv2.FONT_HERSHEY_SIMPLEX,
                                        0.4, (255, 255, 255), 1, cv2.LINE_AA)

                    #########
                    # save video to file
                    if self.is_color():
                        # write the colored frame and write the time on it
                        frame_to_save = frame.copy()
                        self.save_video_stream_to_file(frame_to_save)
                    else:
                        # write the grayscaled frame and write the time on it
                        frame_to_save = gray_image.copy()
                        self.save_video_stream_to_file(frame_to_save)

                    #########
                    # send the frame to window for display
                    if not self.color:
                        # convert the grayscale image into a pyqt image
                        qimage = QImage(
                            gray_image.data, gray_image.shape[1], gray_image.shape[0], QImage.Format_Grayscale8)
                    else:
                        # convert the bgr image into a pyqt image
                        qimage = QImage(
                            rgb_image.data, rgb_image.shape[1], rgb_image.shape[0], QImage.Format_RGB888)
                    
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

            # if the given stream source was url, check if any frame was retrieved. If not, display a unique error message
            if not str(self.camera_id).isdigit() and str(self.camera_id).startswith('http') or str(self.camera_id).startswith('rtsp'):
                if not self.internet_conn_available():
                    self.change_pixmap.emit(QPixmap(self.resource_path('icons' + os.sep + 'conn_error.jpg')))
                elif self.frame_from_url_source is None:
                    self.change_pixmap.emit(QPixmap(self.resource_path('icons' + os.sep + 'no_vid_error.jpg')))
                else:
                    self.change_pixmap.emit(QPixmap(self.resource_path(
                        'icons' + os.sep + 'default_camera_view.png')))
            else:
                # set restart image after video from camera or local file is done playing or stopped by user
                self.change_pixmap.emit(QPixmap(self.resource_path('icons' + os.sep + 'default_camera_view.png')))
            # when the video stream is stopped, release the camera and its related resources
            if self.save_video:
                self.video_writer.release()
                self.is_file_named = False
            self.vid_capture.release()
        except:
            #raise Exception("Camera not accessible")
            self.change_pixmap.emit(
                QPixmap(self.resource_path('icons' + os.sep + 'conn_error.jpg')))
