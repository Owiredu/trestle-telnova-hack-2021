import sys
import os
import time
import cv2
import shutil
from PyQt5.QtWidgets import (QStyleFactory, QApplication, QMainWindow, QMdiSubWindow, QMessageBox, QWidget,
                             QFileDialog, QDialog, QListWidgetItem, QInputDialog)
from PyQt5.QtGui import QPixmap, QImage, QIcon
from PyQt5.QtCore import Qt, QDate, QDir, QSize
from PyQt5.QtMultimedia import QCameraInfo
from alpha_ui import Ui_MainWindow
from video_processing_thread import VideoCaptureThread
from logger_thread import LoggerThread
from post_update_thread import PostUpdateThread
from video_player_main import VideoPlayer
from add_new_stream_ui import Ui_addCameraDialog
from mdi_content_ui import Ui_mdiSubWIndowContent
from constants import *

# set the GUI style
QApplication.setStyle(QStyleFactory.create('Fusion'))

# store references to all video streaming threads
all_streaming_threads = []
# store instances of all video subwindows
all_video_subwins = []
# initialize the logger thread
logger_thread = LoggerThread()
logger_thread.start()
# initialize the update post thread
post_update_thread = PostUpdateThread()
post_update_thread.start()


########################################################################################################################################################################################


class Alpha(QMainWindow):
    """
    This is the main application thread
    """

####---------------------------------------------------------------------THE INITIALIZATION METHOD AND START UP CHECKS-----------------------------------------------------------------------------####
    def __init__(self):
        super().__init__()
        # get the form the generated code from the .ui file
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # set window icon and title
        self.setWindowTitle('Alpha')
        self.setWindowIcon(QIcon(self.resource_path('icons' + os.sep + 'alpha_icon.png')))
        # create the application directories if they do not exist
        self.prepare_dirs_for_app()
        # set the maximum number of cameras allowed
        self.max_num_of_streams_allowed = 100
        # set the camera view mode as default
        self.ui.stackedWidget.setCurrentWidget(self.ui.cameraViewPage)
        # initialize add new stream class
        self.add_stream_dialog = AddNewStream(self.ui.mdiArea, MdiSubWindow, self.resource_path, self.tile_camera_view)
        # initialize the path to the photo
        self.photo_path = self.resource_path('icons' + os.sep + 'default_profile_photo.png')
        # create an object to hold the image to print
        self.image_to_print = QImage(self.photo_path)
        # initialize the default photo for the image view gallery and load the images and videos if available
        self.images_pixmap = QPixmap(self.resource_path('icons' + os.sep + 'no_image_available.png')).scaled(800, 600, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.play_video_image = cv2.imread(self.resource_path('icons' + os.sep + 'play_video.png'), cv2.COLOR_BGR2RGB)
        self.video_thumbnails_pixmap = QPixmap(self.resource_path('icons' + os.sep + 'no_video_available.jpg')).scaled(800, 600, Qt.KeepAspectRatio, Qt.FastTransformation)
        self.load_snapshots_on_start_up()
        self.load_video_thumbnails_on_start_up()
        # connect the toolbar actions to their methods
        self.connect_actions_to_toolbars_widgets()
        # connect other widgets apart from the toolbar to their respective methods
        self.connect_actions_to_widgets()
        # instantiate the video player class
        self.video_player = VideoPlayer()
        # arrange the mdi window in the tiled mode as default
        self.tile_camera_view()

    def prepare_dirs_for_app(self):
        """
        This method ensures that all the required directories for running the application are available.
        If not it creates them
        """
        required_dir_names = [SAVED_VIDEOS_BASE_DIR, SNAPSHOTS_BASE_DIR, DATABASES_BASE_DIR]
        for dir_path in required_dir_names:
            os.makedirs(dir_path, exist_ok=True)

####---------------------------------------------------------------------CONNECTION OF WIDGETS TO EVENTS-----------------------------------------------------------------------------####

    def connect_actions_to_toolbars_widgets(self):
        """
        This method sets the actions for all the toolbar items
        """
        # actions for switch views
        self.ui.actionSurveillance_Mode.triggered.connect(self.switch_to_camera_view_mode)
        self.ui.actionSnapshot_Gallery.triggered.connect(self.switch_to_snapshot_gallery)
        self.ui.actionVideo_Gallery.triggered.connect(self.switch_to_video_gallery)
        # others
        self.ui.actionCascade_View.triggered.connect(self.cascade_camera_view)
        self.ui.actionTiled_View.triggered.connect(self.tile_camera_view)
        self.ui.actionStart_All_Streams.triggered.connect(self.start_all_cameras)
        self.ui.actionStop_All_Streams.triggered.connect(self.stop_all_cameras)
        self.ui.actionAdd_Stream.triggered.connect(self.add_new_video_stream_dialog)
        self.ui.actionEmbed_Time_For_All_Videos.toggled.connect(self.toggle_all_embedded_time)
        self.ui.actionSave_All_Videos.toggled.connect(self.save_all_video_streams)
        self.ui.actionAll_People_Counters.toggled.connect(self.enable_all_people_counters)
        self.ui.actionAll_Colored_Modes.toggled.connect(self.toggle_colored_and_grayscale)
        self.ui.actionAll_Snapshots.triggered.connect(self.take_all_snapshots)
        self.ui.actionHide_All_Video_Menus.toggled.connect(self.hide_all_video_menus)
        # HIDE THE ALL COLOR MODES MENU DUE TO CONTROVERSY IN ITS FUNCTION
        self.ui.actionAll_Colored_Modes.setVisible(False)

    def connect_actions_to_widgets(self):
        """
        This method connects all widgets apart from the toolbar to their respective actions
        """
        # for snapshot gallery view
        self.ui.currentImageLabel.mouseDoubleClickEvent = self.save_snapshot
        self.ui.imagesListWidget.keyPressEvent = self.image_list_widget_key_press_events
        self.ui.refreshSnapshotsButton.clicked.connect(self.refresh_snapshot_images)
        self.ui.imagesListWidget.currentItemChanged.connect(self.get_show_selected_image)
        self.ui.selectImageDateEdit.dateChanged.connect(self.load_snapshots_on_date_click)
        self.ui.imagesDateListWidget.currentItemChanged.connect(self.load_snapshots_on_date_select)
        self.ui.imagesDateListWidget.keyPressEvent = self.images_dir_list_widget_key_press_events
        self.ui.previousImageButton.clicked.connect(self.set_image_to_previous)
        self.ui.nextImageButton.clicked.connect(self.set_image_to_next)
        self.ui.saveSnapshotButton.clicked.connect(self.save_snapshot)
        self.ui.deleteSnapshotButton.clicked.connect(self.delete_snapshot_file)
        self.ui.deleteDateSnapshotsButton.clicked.connect(self.delete_snapshot_date)
        self.ui.deleteAllSnapshotsButton.clicked.connect(self.delete_all_snapshots)
        # for video gallery view
        self.ui.currentVideoLabel.mouseDoubleClickEvent = self.play_video
        self.ui.videosListWidget.keyPressEvent = self.video_list_widget_key_press_events
        self.ui.refreshVideosButton.clicked.connect(self.refresh_videos)
        self.ui.videosListWidget.currentItemChanged.connect(self.get_show_selected_video_thumbnail)
        self.ui.selectVideoDateEdit.dateChanged.connect(self.load_videos_on_date_click)
        self.ui.videosDateListWidget.currentItemChanged.connect(self.load_videos_on_date_select)
        self.ui.videosDateListWidget.keyPressEvent = self.videos_dir_list_widget_key_press_events
        self.ui.previousVideoButton.clicked.connect(self.set_video_to_previous)
        self.ui.nextVideoButton.clicked.connect(self.set_video_to_next)
        self.ui.playVideoButton.clicked.connect(self.play_video)
        self.ui.deleteVideoButton.clicked.connect(self.delete_video_file)
        self.ui.deleteDateVideosButton.clicked.connect(self.delete_video_date)
        self.ui.saveVideoButton.clicked.connect(self.save_video)
        self.ui.deleteAllVideosButton.clicked.connect(self.delete_all_videos)
        self.ui.analyseVideoButton.clicked.connect(self.analyse_video)

####---------------------------------------------------------------------TOOLBAR BUTTONS AND VIDEO STREAMING INTERFACE OPERATIONS-----------------------------------------------------------------------------####

    def switch_to_camera_view_mode(self):
        """
        This method switches view to the video stream view
        """
        self.ui.actionSurveillance_Mode.setChecked(True)
        self.ui.actionVideo_Gallery.setChecked(False)
        self.ui.actionSnapshot_Gallery.setChecked(False)
        self.ui.stackedWidget.setCurrentWidget(self.ui.cameraViewPage)

    def switch_to_snapshot_gallery(self):
        """
        This method switches view to the snapshot gallery view
        """
        self.ui.actionSurveillance_Mode.setChecked(False)
        self.ui.actionVideo_Gallery.setChecked(False)
        self.ui.actionSnapshot_Gallery.setChecked(True)
        self.ui.stackedWidget.setCurrentWidget(self.ui.snapshotGalleryPage)
        # if new images have been added, load the new images
        self.refresh_snapshot_images()

    def switch_to_video_gallery(self):
        """
        This method switches view to the video gallery view
        """
        self.ui.actionSurveillance_Mode.setChecked(False)
        self.ui.actionVideo_Gallery.setChecked(True)
        self.ui.actionSnapshot_Gallery.setChecked(False)
        self.ui.stackedWidget.setCurrentWidget(self.ui.videoGalleryPage)
        # if new videos have been added, load the new videos
        self.refresh_videos()

    def cascade_camera_view(self):
        """
        This method arranges the mdi sub windows in the cascade view
        """
        self.tiled_view_enabled = False
        self.ui.mdiArea.cascadeSubWindows()

    def tile_camera_view(self):
        """
        This method arranges the mdi sub windows in the tiled view
        """
        self.tiled_view_enabled = True
        self.ui.mdiArea.tileSubWindows()

    def start_all_cameras(self):
        """
        This method starts all the available video streams
        """
        for video_subwindow in all_video_subwins:
            video_subwindow.start_capture()
            QApplication.processEvents()
            time.sleep(0.1)

    def stop_all_cameras(self):
        """
        This method stops all the active video streams
        """
        for thread, video_subwindow in zip(all_streaming_threads, all_video_subwins):
            if thread.video_playing:
                video_subwindow.end_capture()

    def toggle_all_embedded_time(self):
        """
        This method enables and disables embedded time for all video streams
        """
        for video_subwindow in all_video_subwins:
            if self.ui.actionEmbed_Time_For_All_Videos.isChecked():
                video_subwindow.ui.embedTimeCheckBox.setChecked(True)
            else:
                video_subwindow.ui.embedTimeCheckBox.setChecked(False)

    def save_all_video_streams(self):
        """
        This method activates video recording for all the available streams
        """
        for video_subwindow in all_video_subwins:
            if self.ui.actionSave_All_Videos.isChecked():
                video_subwindow.ui.saveVideoCheckBox.setChecked(True)
            else:
                video_subwindow.ui.saveVideoCheckBox.setChecked(False)

    def enable_all_people_counters(self):
        """
        This method enables the people counting of all the streams
        """
        for video_subwindow in all_video_subwins:
            if self.ui.actionAll_People_Counters.isChecked():
                video_subwindow.ui.peopleCounterCheckbox.setChecked(True)
            else:
                video_subwindow.ui.peopleCounterCheckbox.setChecked(False)

    def toggle_colored_and_grayscale(self):
        """
        This method toggles the colored and grayscale modes for all the streams
        """
        for video_subwindow in all_video_subwins:
            if self.ui.actionAll_Colored_Modes.isChecked():
                video_subwindow.ui.coloredRadioButton.setChecked(True)
            else:
                video_subwindow.ui.grayscaleRadioButton.setChecked(True)

    def take_all_snapshots(self):
        """
        This method takes snapshots for all the streams
        """
        for video_subwindow in all_video_subwins:
            video_subwindow.take_snapshot()

    def hide_all_video_menus(self):
        """
        This method hides all the video menus
        """
        for video_subwindow in all_video_subwins:
            if self.ui.actionHide_All_Video_Menus.isChecked():
                video_subwindow.ui.optionsScrollArea.hide()
                video_subwindow.setWindowFlags(Qt.FramelessWindowHint)
                video_subwindow.frame_hidden = True
            else:
                video_subwindow.ui.optionsScrollArea.show()
                video_subwindow.setWindowFlags(Qt.WindowFullscreenButtonHint)
                video_subwindow.frame_hidden = False

    def add_new_video_stream_dialog(self):
        """
        This method opens the dialog for adding new video stream
        """
        if len(all_streaming_threads) < self.max_num_of_streams_allowed:
            self.add_stream_dialog.show()
        else:
            QMessageBox.information(self, 'Stream Notification', 'Maximum number of streams (' + str(self.max_num_of_streams_allowed) +
                                    ') reached. You can only replace an existing stream by closing it and starting the new one')

    def resizeEvent(self, event):
        """
        This method sets the camera view to tiled when the window is resized if it was already in tiled view
        """
        if self.tiled_view_enabled:
            self.tile_camera_view()

####---------------------------------------------------------------------SNAPSHOT GALLERY INTERFACE OPERATIONS-----------------------------------------------------------------------------####

    def load_snapshots_on_start_up(self):
        """
        This method gets the snapshot images into the snapshot gallery
        """
        try:
            # create an object to hold the directory names
            self.images_dir_names = []
            # create objects to hold the image names and the images' list widget item
            self.images_names = []
            self.image_items = []
            # get directory names into a list
            for dir_name in os.listdir(SNAPSHOTS_BASE_DIR):
                self.images_dir_names.append(dir_name)
            if len(self.images_dir_names) != 0:
                self.images_dir_names.sort()
                self.images_dir_names.reverse()
                # set the date to the most recent
                year, month, day = self.images_dir_names[0].split('-')
                self.ui.selectImageDateEdit.setDate(QDate(int(year), int(month), int(day)))
                # add the available dates to the date list widget and select the most recent
                self.ui.imagesDateListWidget.addItems(self.images_dir_names)
                self.ui.imagesDateListWidget.setCurrentRow(0)
                # get file names into a list
                for file_name in os.listdir(SNAPSHOTS_BASE_DIR + os.sep + self.images_dir_names[0]):
                    self.images_names.append(file_name)
                # set the files in the widget
                if len(self.images_names) == 0:
                    # if there is no image available, show the default image
                    self.ui.currentImageLabel.setPixmap(self.images_pixmap)
                else:
                    # sort the images from the most recently taken to the least recently taken
                    self.images_names.sort()
                    # if images are available, set them into the list widget item
                    for image in self.images_names:
                        item = QListWidgetItem(self.ui.imagesListWidget)
                        icon = QIcon()
                        icon.addPixmap(QPixmap(SNAPSHOTS_BASE_DIR + os.sep + self.images_dir_names[0] + os.sep + image), QIcon.Normal, QIcon.On)
                        item.setIcon(icon)
                        self.image_items.append(item)
                    # set the grid size of image list widget and add the list widget item containing the list widget
                    self.ui.imagesListWidget.setGridSize(QSize(110, 110))
                    self.ui.imagesListWidget.addItem(item)
                    # set the first image as selected and show it on the label
                    self.ui.imagesListWidget.setCurrentItem(self.image_items[-1])
                    self.get_show_selected_image()
            else:
                # if there is no image available, show the default image
                self.ui.currentImageLabel.setPixmap(self.images_pixmap)
        except IndexError:
            pass

    def load_snapshots_on_date_select(self):
        """
        This method loads the images in directory with the selected date into the images list widget
        when the date is selected from the date list item
        """
        try:
            # check if a snapshot directory is available
            if len(self.images_dir_names) != 0:
                # set the date to the selected one
                year, month, day = self.images_dir_names[self.ui.imagesDateListWidget.currentRow()].split('-')
                self.ui.selectImageDateEdit.setDate(QDate(int(year), int(month), int(day)))
                # get file names and image items into a list
                self.images_names.clear()
                for file_name in os.listdir(SNAPSHOTS_BASE_DIR + os.sep + self.images_dir_names[self.ui.imagesDateListWidget.currentRow()]):
                    self.images_names.append(file_name)
                # set the files in the widget
                if len(self.images_names) == 0:
                    self.image_items.clear()
                    item = QListWidgetItem(self.ui.imagesListWidget)
                    # if there is no image available, show the default image
                    self.images_pixmap = QPixmap(self.resource_path('icons' + os.sep + 'no_image_available.png')).scaled(800, 600, Qt.KeepAspectRatio, Qt.FastTransformation)
                    self.ui.currentImageLabel.setPixmap(self.images_pixmap)
                    # clear the image properties
                    self.ui.currentImageGroupBox.setTitle('FILE INFORMATION')
                else:
                    # sort the images from the most recently taken to the least recently taken
                    self.images_names.sort()
                    # clear the previous content of the image list widget
                    self.image_items.clear()
                    self.ui.imagesListWidget.clear()
                    # if images are available, set them into the list widget item
                    for image in self.images_names:
                        item = QListWidgetItem(self.ui.imagesListWidget)
                        icon = QIcon()
                        icon.addPixmap(QPixmap(SNAPSHOTS_BASE_DIR + os.sep + self.images_dir_names[self.ui.imagesDateListWidget.currentRow()] + os.sep + image), QIcon.Normal, QIcon.On)
                        item.setIcon(icon)
                        self.image_items.append(item)
                    # set the grid size of image list widget and add the list widget item containing the list widget
                    self.ui.imagesListWidget.setGridSize(QSize(110, 110))
                    self.ui.imagesListWidget.addItem(item)
                    # set the first image as selected and show it on the label
                    self.ui.imagesListWidget.setCurrentItem(
                        self.image_items[-1])
                    self.get_show_selected_image()
            else:
                try:
                    year, month, day = self.images_dir_names[self.ui.imagesDateListWidget.currentRow()].split('-')
                    self.ui.selectImageDateEdit.setDate(QDate(int(year), int(month), int(day)))
                except:
                    pass
        except IndexError:
            pass

    def load_snapshots_on_date_click(self):
        """
        This method loads the images in directory with the selected date into the images list widget
        when the date is selected from the date widget
        """
        try:
            # check if the selected date is available before proceeding
            if self.images_dir_names.__contains__(self.ui.selectImageDateEdit.date().toString(Qt.ISODate)):
                # if the selected date is a valid directory name, set open that directory and load it's images into the images list widget
                self.ui.imagesDateListWidget.setCurrentRow(self.images_dir_names.index(self.ui.selectImageDateEdit.text().strip()))
            else:
                QMessageBox.information(self, 'Date Error', 'Requested date is unavailable')
        except IndexError:
            pass

    def refresh_snapshot_images(self):
        """
        This method loads current taken snapshots and add then to the already loaded ones
        """
        try:
            # create an object to hold the directory names
            new_dir_names = []
            # get directory names into a list
            for dir_name in os.listdir(SNAPSHOTS_BASE_DIR):
                new_dir_names.append(dir_name)
            if len(new_dir_names) != 0:
                new_dir_names.sort()
                new_dir_names.reverse()
                # a new directory has been added, load it, set it as the current directory and load the images in it into the images list widget
                if self.images_dir_names != new_dir_names:
                    # set the new directory list
                    self.images_dir_names = new_dir_names
                    # set the date to the most recent
                    year, month, day = self.images_dir_names[0].split('-')
                    self.ui.selectImageDateEdit.setDate(QDate(int(year), int(month), int(day)))
                    # add the available dates to the date list widget and select the most recent
                    self.ui.imagesDateListWidget.clear()
                    self.ui.imagesDateListWidget.addItems(self.images_dir_names)
                    self.ui.imagesDateListWidget.setCurrentRow(0)
                    # load the files and select the most recent image
                    # get file names and image items into a list
                    self.images_names.clear()
                    for file_name in os.listdir(SNAPSHOTS_BASE_DIR + os.sep + self.images_dir_names[self.ui.imagesDateListWidget.currentRow()]):
                        self.images_names.append(file_name)
                    # set the files in the widget
                    if len(self.images_names) == 0:
                        self.image_items.clear()
                        item = QListWidgetItem(self.ui.imagesListWidget)
                        # if there is no image available, show the default image
                        self.images_pixmap = QPixmap(self.resource_path('icons' + os.sep + 'no_image_available.png')).scaled(800, 600, Qt.KeepAspectRatio, Qt.FastTransformation)
                        self.ui.currentImageLabel.setPixmap(self.images_pixmap)
                        # clear the image properties
                        self.ui.currentImageGroupBox.setTitle('FILE INFORMATION')
                    else:
                        # sort the images from the most recently taken to the least recently taken
                        self.images_names.sort()
                        # clear the previous content of the image list widget
                        self.image_items.clear()
                        self.ui.imagesListWidget.clear()
                        # if images are available, set them into the list widget item
                        for image in self.images_names:
                            item = QListWidgetItem(self.ui.imagesListWidget)
                            icon = QIcon()
                            icon.addPixmap(QPixmap(SNAPSHOTS_BASE_DIR + os.sep + self.images_dir_names[self.ui.imagesDateListWidget.currentRow()] + os.sep + image), QIcon.Normal, QIcon.On)
                            item.setIcon(icon)
                            self.image_items.append(item)
                        # set the grid size of image list widget and add the list widget item containing the list widget
                        self.ui.imagesListWidget.setGridSize(QSize(110, 110))
                        self.ui.imagesListWidget.addItem(item)
                        # set the first image as selected and show it on the label
                        self.ui.imagesListWidget.setCurrentItem(self.image_items[-1])
                        self.get_show_selected_image()
                else:
                    self.refresh_images_instantly()
        except IndexError:
            pass

    def refresh_images_instantly(self):
        """
        This method refreshes the list of images in the images list widget after an image is deleted or updated for the current folder
        """
        try:
            if len(self.images_dir_names) != 0:
                # get file names into a list
                self.images_names.clear()
                for file_name in os.listdir(SNAPSHOTS_BASE_DIR + os.sep + self.images_dir_names[self.ui.imagesDateListWidget.currentRow()]):
                    self.images_names.append(file_name)
                # set the files in the widget
                if len(self.images_names) == 0:
                    self.image_items.clear()
                    item = QListWidgetItem(self.ui.imagesListWidget)
                    # if there is no image available, show the default image
                    self.images_pixmap = QPixmap(self.resource_path('icons' + os.sep + 'no_image_available.png')).scaled(800, 600, Qt.KeepAspectRatio, Qt.FastTransformation)
                    self.ui.currentImageLabel.setPixmap(self.images_pixmap)
                    # clear the image properties
                    self.ui.currentImageGroupBox.setTitle('FILE INFORMATION')
                else:
                    # sort the images from the most recently taken to the least recently taken
                    self.images_names.sort()
                    # clear the previous content of the image list widget
                    self.image_items.clear()
                    self.ui.imagesListWidget.clear()
                    # if images are available, set them into the list widget item
                    for image in self.images_names:
                        item = QListWidgetItem(self.ui.imagesListWidget)
                        icon = QIcon()
                        icon.addPixmap(QPixmap(SNAPSHOTS_BASE_DIR + os.sep + self.images_dir_names[self.ui.imagesDateListWidget.currentRow()] + os.sep + image), QIcon.Normal, QIcon.On)
                        item.setIcon(icon)
                        self.image_items.append(item)
                    # set the grid size of image list widget and add the list widget item containing the list widget
                    self.ui.imagesListWidget.setGridSize(QSize(110, 110))
                    self.ui.imagesListWidget.addItem(item)
                    # set the first image as selected and show it on the label
                    self.ui.imagesListWidget.setCurrentItem(self.image_items[-1])
                    self.get_show_selected_image()
        except IndexError:
            pass

    def refresh_image_dir_list_instantly(self):
        """
        This method refreshes the list of directory in the date list widget after date folder is deleted
        """
        try:
            # get directory names (dates) into a list
            self.images_dir_names.clear()
            for dir_name in os.listdir(SNAPSHOTS_BASE_DIR):
                self.images_dir_names.append(dir_name)
            if len(self.images_dir_names) != 0:
                # sort the images from the most recently taken to the least recently taken
                self.images_dir_names.sort()
                self.images_dir_names.reverse()
                # clear the previous content of the image list widget
                self.ui.imagesDateListWidget.clear()
                # if directories are available, set them into the list widget item
                self.ui.imagesDateListWidget.addItems(self.images_dir_names)
                # set the first image as selected and show it on the label
                self.ui.imagesDateListWidget.setCurrentRow(0)
            else:
                # if the last folder is deleted, clear all image resources and reset the label to default
                self.ui.currentImageLabel.setPixmap(self.images_pixmap)
                self.images_names.clear()
                self.image_items.clear()
                self.ui.imagesListWidget.clear()
                self.images_dir_names.clear()
                self.ui.imagesDateListWidget.clear()
                self.images_pixmap = QPixmap(self.resource_path('icons' + os.sep + 'no_image_available.png')).scaled(800, 600, Qt.KeepAspectRatio, Qt.FastTransformation)
                # clear the image properties
                self.ui.currentImageGroupBox.setTitle('FILE INFORMATION')
        except IndexError:
            pass

    def get_show_selected_image(self):
        """
        This method sets the selected image to the label
        """
        try:
            # check if there is a snapshot directory
            if len(self.images_dir_names) != 0:
                # get the name of the image file
                image_file_name = self.images_names[self.ui.imagesListWidget.currentRow()]
                # split the file name to separate the time from the camera id
                file_name_split = image_file_name.split('_')
                # if the name of the camera id contains underscores too, join them again since they would also split
                camera_id = '_'.join(file_name_split[:-1])
                # get the time from the splitted file name
                time_taken = file_name_split[-1].split('.')[0]
                # load the image and set it as the current image
                self.images_pixmap = QPixmap(SNAPSHOTS_BASE_DIR + os.sep + self.images_dir_names[self.ui.imagesDateListWidget.currentRow()] +
                                             os.sep + image_file_name).scaled(800, 600, Qt.KeepAspectRatio, Qt.FastTransformation)
                self.ui.currentImageLabel.setPixmap(self.images_pixmap)
                # place the camera id of the camera used to capture the image and the time it was captured
                self.ui.currentImageGroupBox.setTitle('SOURCE ID: ' + camera_id + '\t\t|\t\t' + 'TIME OF CAPTURE: ' +
                                                      time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time_taken))))
            else:
                self.ui.currentImageLabel.setPixmap(
                    QPixmap(self.resource_path('icons' + os.sep + 'no_image_available.png')).scaled(800, 600, Qt.KeepAspectRatio, Qt.FastTransformation))
                # clear the image properties
                self.ui.currentImageGroupBox.setTitle('FILE INFORMATION')
        except IndexError:
            pass

    def set_image_to_previous(self):
        """
        This method sets the previous image as the current one
        """
        try:
            if len(self.images_dir_names) != 0:
                if len(self.images_names) != 0:
                    if self.ui.imagesListWidget.currentRow() > 0:
                        self.ui.imagesListWidget.setCurrentItem(self.image_items[self.ui.imagesListWidget.currentRow() - 1])
                        self.get_show_selected_image()
                    else:
                        self.ui.imagesListWidget.setCurrentItem(self.image_items[len(self.images_names) - 1])
                        self.get_show_selected_image()
        except IndexError:
            pass

    def set_image_dir_to_previous(self):
        """
        This method sets the previous directory as the current one
        """
        try:
            if len(self.images_dir_names) != 0:
                if self.ui.imagesDateListWidget.currentRow() > 0:
                    self.ui.imagesDateListWidget.setCurrentRow(self.ui.imagesDateListWidget.currentRow() - 1)
                else:
                    self.ui.imagesDateListWidget.setCurrentRow(len(self.images_dir_names) - 1)
        except IndexError:
            pass

    def set_image_to_next(self):
        """
        This method sets the next image as the current one
        """
        try:
            if len(self.images_dir_names) != 0:
                if len(self.images_names) != 0:
                    if self.ui.imagesListWidget.currentRow() < len(self.images_names) - 1:
                        self.ui.imagesListWidget.setCurrentItem(self.image_items[self.ui.imagesListWidget.currentRow() + 1])
                        self.get_show_selected_image()
                    else:
                        self.ui.imagesListWidget.setCurrentItem(self.image_items[0])
                        self.get_show_selected_image()
        except IndexError:
            pass

    def set_image_dir_to_next(self):
        """
        This method sets the next directory as the current one
        """
        try:
            if len(self.images_dir_names) != 0:
                if self.ui.imagesDateListWidget.currentRow() < len(self.images_dir_names) - 1:
                    self.ui.imagesDateListWidget.setCurrentRow(self.ui.imagesDateListWidget.currentRow() + 1)
                else:
                    self.ui.imagesDateListWidget.setCurrentRow(0)
        except IndexError:
            pass

    def save_snapshot(self, event):
        """
        This method saves a copy of the currently selected image
        """
        try:
            # get the selected file name
            selected_image_file_name = self.images_names[self.ui.imagesListWidget.currentRow()]
            # get the extension
            file_ext = selected_image_file_name.split('.')[-1]
            # read the image as bytes
            image_file = SNAPSHOTS_BASE_DIR + os.sep + self.images_dir_names[self.ui.imagesDateListWidget.currentRow()] + os.sep + selected_image_file_name
            # show the save dialog
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, 'Save Selected Image', QDir.homePath(), 'Image File (*.' + file_ext + ')', options=options)
            # save a copy of the file
            if file_name:
                file_name = file_name + ('' if file_name.endswith('.' + file_ext) else '.' + file_ext)
                shutil.copyfile(image_file, file_name)
                QMessageBox.information(self, 'Copy Completed', 'Successfully copied image to ' + file_name)
        except IndexError:
            pass
        except:
            QMessageBox.critical(self, 'Error', 'An error occurred while saving image')

    def delete_snapshot_file(self):
        """
        This method deletes the selected snapshot
        """
        try:
            # get the selected file name
            selected_image_file_name = self.images_names[self.ui.imagesListWidget.currentRow()]
            ret_val = QMessageBox.question(self, 'Delete', 'Do really want to delete selected image?')
            # delete file after confirmation
            if ret_val == QMessageBox.Yes:
                # get currently select image index
                image_index = self.ui.imagesListWidget.currentRow()
                # delete image
                os.remove(SNAPSHOTS_BASE_DIR + os.sep + self.images_dir_names[self.ui.imagesDateListWidget.currentRow()] + os.sep + selected_image_file_name)
                # refresh the images list widget
                self.refresh_images_instantly()
                # select the previous image if any else select the next image
                if len(self.images_names) > 1:
                    if image_index-1 >= 0:
                        self.ui.imagesListWidget.setCurrentRow(image_index - 1)
                    else:
                        self.ui.imagesListWidget.setCurrentRow(image_index)
        except IndexError:
            pass
        except:
            QMessageBox.critical(self, 'Delete Error', 'An error occurred while attempting to delete the currently selected image!')

    def delete_snapshot_date(self):
        """
        This method deletes all the snapshots of the selected date
        """
        try:
            # get the selected directory name
            selected_dir_name = self.images_dir_names[self.ui.imagesDateListWidget.currentRow()]
            dir_file_count = len(os.listdir(SNAPSHOTS_BASE_DIR + os.sep + selected_dir_name))
            if dir_file_count == 0:
                ret_val = QMessageBox.question(self, 'Delete directory', 'Delete ' + selected_dir_name + ' directory')
            else:
                ret_val = QMessageBox.question(self, 'Delete directory', 'Delete ' + selected_dir_name + ' directory along with ' +
                                               str(dir_file_count) + ' snapshot files')
            # delete file after confirmation
            if ret_val == QMessageBox.Yes:
                # get currently select image index
                dir_index = self.ui.imagesDateListWidget.currentRow()
                # delete image
                shutil.rmtree(SNAPSHOTS_BASE_DIR + os.sep + selected_dir_name)
                # refresh the images list widget
                self.refresh_image_dir_list_instantly()
                # select the previous image if any else select the next image
                if len(self.images_dir_names) > 1:
                    if dir_index-1 >= 0:
                        self.ui.imagesDateListWidget.setCurrentRow(dir_index - 1)
                    else:
                        self.ui.imagesDateListWidget.setCurrentRow(dir_index)
        except IndexError:
            pass
        except:
            QMessageBox.critical(self, 'Delete Error', 'An error occurred while attempting to delete the currently selected directory!')

    def delete_all_snapshots(self):
        """
        This method deletes all the snapshots
        """
        try:
            ret_val = QMessageBox.question(self, 'Delete All Snapshots',  'Do you want to delete ALL snapshots?')
            # delete after confirmation
            if ret_val == QMessageBox.Yes:
                # delete recording date directories
                for dir_name in os.listdir(SNAPSHOTS_BASE_DIR):
                    shutil.rmtree(SNAPSHOTS_BASE_DIR + os.sep + dir_name)
                # refresh the recordings list widget
                self.refresh_image_dir_list_instantly()
        except IndexError:
            pass
        except:
            QMessageBox.critical(self, 'Delete Error', 'An error occurred while attempting to delete all snapshots')

    def image_list_widget_key_press_events(self, event):
        """
        This method adds key events to the image list widget
        """
        # get the key
        key_pressed = event.key()
        if key_pressed == Qt.Key_Left:
            self.set_image_to_previous()
        if key_pressed == Qt.Key_Right:
            self.set_image_to_next()
        if key_pressed == Qt.Key_Delete:
            self.delete_snapshot_file()

    def images_dir_list_widget_key_press_events(self, event):
        """
        This method adds key events to the date list widget
        """
        # get the key
        key_pressed = event.key()
        if key_pressed == Qt.Key_Up:
            self.set_image_dir_to_previous()
        if key_pressed == Qt.Key_Down:
            self.set_image_dir_to_next()
        if key_pressed == Qt.Key_Delete:
            self.delete_snapshot_date()

####---------------------------------------------------------------------VIDEO GALLERY INTERFACE OPERATIONS-----------------------------------------------------------------------------####

    def load_video_thumbnails_on_start_up(self):
        """
        This method gets the video thumbnails into the videos gallery
        """
        try:
            # create an object to hold the directory names
            self.videos_dir_names = []
            # create objects to hold the image names and the videos' list widget item
            self.videos_names = []
            self.video_items = []
            # get directory names into a list
            for dir_name in os.listdir(SAVED_VIDEOS_BASE_DIR):
                self.videos_dir_names.append(dir_name)
            if len(self.videos_dir_names) != 0:
                self.videos_dir_names.sort()
                self.videos_dir_names.reverse()
                # set the date to the most recent
                year, month, day = self.videos_dir_names[0].split('-')
                self.ui.selectVideoDateEdit.setDate(QDate(int(year), int(month), int(day)))
                # add the available dates to the date list widget and select the most recent
                self.ui.videosDateListWidget.addItems(self.videos_dir_names)
                self.ui.videosDateListWidget.setCurrentRow(0)

                # get file names into a list
                for file_name in os.listdir(SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[0]):
                    self.videos_names.append(file_name)
                # set the files in the widget
                if len(self.videos_names) == 0:
                    # if there is no video available, show the default image
                    self.ui.currentVideoLabel.setPixmap(self.video_thumbnails_pixmap)
                else:
                    # sort the images from the most recently taken to the least recently taken
                    self.videos_names.sort()
                    # if images are available, set them into the list widget item
                    for video in self.videos_names:
                        item = QListWidgetItem(self.ui.videosListWidget)
                        icon = QIcon()
                        # load video thumbnails with video capture and set them as the icons
                        vid_capture = cv2.VideoCapture(SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[0] + os.sep + video)
                        ret, frame = vid_capture.read()
                        if ret:
                            frame = cv2.resize(frame, (800, 600))
                            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            img_width = rgb_image.shape[1]
                            img_height = rgb_image.shape[0]
                            self.embed_play_icon(rgb_image, img_width, img_height)
                            qimage = QImage(rgb_image.data, img_width, img_height, QImage.Format_RGB888)
                            qpixmap = QPixmap.fromImage(qimage)
                            icon.addPixmap(qpixmap, QIcon.Normal, QIcon.On)
                            vid_capture.release()
                            item.setIcon(icon)
                            self.video_items.append(item)
                    # set the grid size of video list widget and add the list widget item containing the list widget
                    self.ui.videosListWidget.setGridSize(QSize(110, 110))
                    self.ui.videosListWidget.addItem(item)
                    # set the first image as selected and show it on the label
                    self.ui.videosListWidget.setCurrentItem(self.video_items[-1])
                    self.get_show_selected_video_thumbnail()
            else:
                # if there is no video available, show the default image
                self.ui.currentVideoLabel.setPixmap(self.video_thumbnails_pixmap)
        except IndexError:
            pass

    def play_video(self, event):
        """
        This method plays the selected video
        """
        try:
            file_path = SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[self.ui.videosDateListWidget.currentRow()] + os.sep + self.videos_names[self.ui.videosListWidget.currentRow()]
            self.video_player.open_file(file_path)
            self.video_player.show()
        except:
            pass

    def save_video(self):
        '''
        This method saves a copy of the currently selected video
        '''
        try:
            video_file_path = SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[self.ui.videosDateListWidget.currentRow()] + os.sep + self.videos_names[self.ui.videosListWidget.currentRow()]
            # get the extension
            file_ext = video_file_path.split('.')[-1]
            # show the save dialog
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, 'Save Selected Video', '', 'Video File (*.' + file_ext + ')', options=options)
            # save a copy of the file
            if file_name:
                file_name = file_name + ('' if file_name.endswith('.' + file_ext) else '.' + file_ext)
                shutil.copyfile(video_file_path, file_name)
                QMessageBox.information(self, 'Copy Completed', 'Successfully copied video to ' + file_name)
        except:
            pass

    def analyse_video(self):
        """
        This method loads the selected video into the camera view for analysis
        """
        try:
            # get the stream name
            win_name, ret = QInputDialog.getText(self, 'Stream Name', 'Enter stream name:', text=str(time.time()).replace('.', ''))
            if ret:
                if win_name.strip() != '':
                    # check if invalid symbols are present in the name of the stream
                    unaccepted_naming_chars = ['/', '\\', '\\\\', '//']
                    invalid_name = False
                    for item in unaccepted_naming_chars:
                        if win_name.__contains__(item):
                            invalid_name = True
                    # if the name is valid, proceed to add stream else show error message
                    if not invalid_name:
                        if len(all_streaming_threads) < self.max_num_of_streams_allowed:
                            # get the file path
                            video_file_path = SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[self.ui.videosDateListWidget.currentRow()] + os.sep + self.videos_names[self.ui.videosListWidget.currentRow()]
                            # add the video stream
                            new_sub_win = MdiSubWindow(video_file_path, win_name, self.resource_path, self.ui.mdiArea)
                            self.ui.mdiArea.addSubWindow(new_sub_win)
                            new_sub_win.show()
                            # add sub window to all videos sub windows list
                            all_video_subwins.append(new_sub_win)
                            # set the view to tiled
                            self.tile_camera_view()
                            # switch view to camera
                            self.ui.stackedWidget.setCurrentWidget(self.ui.cameraViewPage)
                        else:
                            QMessageBox.information(self, 'Stream Notification', 'Maximum number of streams (' + str(self.max_num_of_streams_allowed) +
                                                    ') reached. You can only replace an existing stream by closing it and starting the new one')
                    else:
                        QMessageBox.critical(self, 'Invalid Name', r'Stream name must not contain "/", "//", "\" or "\\"')
                else:
                    QMessageBox.critical(self, 'Invalid Name', r'Please name the video stream')
        except:
            pass

    def load_videos_on_date_select(self):
        """
        This method loads the videos in directory with the selected date into the videos list widget
        when the date is selected from the date list item
        """
        try:
            # check if a video directory is available
            if len(self.videos_dir_names) != 0:
                # set the date to the selected one
                year, month, day = self.videos_dir_names[self.ui.videosDateListWidget.currentRow()].split('-')
                self.ui.selectVideoDateEdit.setDate(QDate(int(year), int(month), int(day)))
                # get file names and video items into a list
                self.videos_names.clear()
                for file_name in os.listdir(SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[self.ui.videosDateListWidget.currentRow()]):
                    self.videos_names.append(file_name)
                # set the files in the widget
                if len(self.videos_names) == 0:
                    self.video_items.clear()
                    item = QListWidgetItem(self.ui.videosListWidget)
                    # if there is no video available, show the default video
                    self.video_thumbnails_pixmap = QPixmap(self.resource_path('icons' + os.sep + 'no_video_available.jpg'))
                    self.ui.currentVideoLabel.setPixmap(self.video_thumbnails_pixmap)
                    # clear the video properties
                    self.ui.currentVideoGroupBox.setTitle('FILE INFORMATION')
                else:
                    # sort the videos from the most recently taken to the least recently taken
                    self.videos_names.sort()
                    # clear the previous content of the video list widget
                    self.video_items.clear()
                    self.ui.videosListWidget.clear()
                    # if videos are available, set them into the list widget item
                    for video in self.videos_names:
                        item = QListWidgetItem(self.ui.videosListWidget)
                        icon = QIcon()
                        vid_capture = cv2.VideoCapture(SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[self.ui.videosDateListWidget.currentRow()] + os.sep + video)
                        ret, frame = vid_capture.read()
                        if ret:
                            frame = cv2.resize(frame, (800, 600))
                            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            img_width = rgb_image.shape[1]
                            img_height = rgb_image.shape[0]
                            self.embed_play_icon(rgb_image, img_width, img_height)
                            qimage = QImage(rgb_image.data, img_width, img_height, QImage.Format_RGB888)
                            qpixmap = QPixmap.fromImage(qimage)
                            vid_capture.release()
                            icon.addPixmap(qpixmap, QIcon.Normal, QIcon.On)
                            item.setIcon(icon)
                            self.video_items.append(item)
                    # set the grid size of video list widget and add the list widget item containing the list widget
                    self.ui.videosListWidget.setGridSize(QSize(110, 110))
                    self.ui.videosListWidget.addItem(item)
                    # set the first video as selected and show it on the label
                    self.ui.videosListWidget.setCurrentItem(self.video_items[-1])
                    self.get_show_selected_video_thumbnail()
        except IndexError:
            pass

    def load_videos_on_date_click(self):
        """
        This method loads the videos in directory with the selected date into the videos list widget
        when the date is selected from the date widget
        """
        try:
            # check if the selected date is available before proceeding
            if self.videos_dir_names.__contains__(self.ui.selectVideoDateEdit.text().strip()):
                # if the selected date is a valid directory name, set open that directory and load it's videos into the videos list widget
                self.ui.videosDateListWidget.setCurrentRow(self.videos_dir_names.index(self.ui.selectVideoDateEdit.text().strip()))
            else:
                QMessageBox.information(self, 'Date Error', 'Requested date is unavailable')
        except IndexError:
            pass

    def refresh_videos(self):
        """
        This method loads currently taken videos and adds then to the already loaded ones
        """
        try:
            # create an object to hold the directory names
            new_dir_names = []
            # get directory names into a list
            for dir_name in os.listdir(SAVED_VIDEOS_BASE_DIR):
                new_dir_names.append(dir_name)
            if len(new_dir_names) != 0:
                new_dir_names.sort()
                new_dir_names.reverse()
                # a new directory has been added, load it, set it as the current directory and load the videos in it into the images list widget
                if self.videos_dir_names != new_dir_names:
                    # set the new directory list
                    self.videos_dir_names = new_dir_names
                    # set the date to the most recent
                    year, month, day = self.videos_dir_names[0].split('-')
                    self.ui.selectVideoDateEdit.setDate(QDate(int(year), int(month), int(day)))
                    # add the available dates to the date list widget and select the most recent
                    self.ui.videosDateListWidget.clear()
                    self.ui.videosDateListWidget.addItems(self.videos_dir_names)
                    self.ui.videosDateListWidget.setCurrentRow(0)
                    # load the files and select the most recent video
                    # get file names and video items into a list
                    self.videos_names.clear()
                    for file_name in os.listdir(SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[self.ui.videosDateListWidget.currentRow()]):
                        self.videos_names.append(file_name)
                    # set the files in the widget
                    if len(self.videos_names) == 0:
                        self.video_items.clear()
                        item = QListWidgetItem(self.ui.videosListWidget)
                        # if there is no video available, show the default video
                        self.video_thumbnails_pixmap = QPixmap(self.resource_path('icons' + os.sep + 'no_video_available.jpg'))
                        self.ui.currentVideoLabel.setPixmap(self.video_thumbnails_pixmap)
                        # clear the video properties
                        self.ui.currentVideoGroupBox.setTitle('FILE INFORMATION')
                    else:
                        # sort the videos from the most recently taken to the least recently taken
                        self.videos_names.sort()
                        # clear the previous content of the video list widget
                        self.video_items.clear()
                        self.ui.videosListWidget.clear()
                        # if videos are available, set them into the list widget item
                        for video in self.videos_names:
                            item = QListWidgetItem(self.ui.videosListWidget)
                            icon = QIcon()
                            vid_capture = cv2.VideoCapture(SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[self.ui.videosDateListWidget.currentRow()] + os.sep + video)
                            ret, frame = vid_capture.read()
                            if ret:
                                frame = cv2.resize(frame, (800, 600))
                                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                                img_width = rgb_image.shape[1]
                                img_height = rgb_image.shape[0]
                                self.embed_play_icon(rgb_image, img_width, img_height)
                                qimage = QImage(rgb_image.data, img_width, img_height, QImage.Format_RGB888)
                                qpixmap = QPixmap.fromImage(qimage)
                                icon.addPixmap(qpixmap, QIcon.Normal, QIcon.On)
                                vid_capture.release()
                                item.setIcon(icon)
                                self.video_items.append(item)
                        # set the grid size of video list widget and add the list widget item containing the list widget
                        self.ui.videosListWidget.setGridSize(QSize(110, 110))
                        self.ui.videosListWidget.addItem(item)
                        # set the first video as selected and show it on the label
                        self.ui.videosListWidget.setCurrentItem(self.video_items[-1])
                        self.get_show_selected_video_thumbnail()
                else:
                    self.refresh_videos_instantly()
        except IndexError:
            pass

    def refresh_videos_instantly(self):
        """
        This method refreshes the list of videos in the videos list widget after an video is deleted or updated for the current folder
        """
        try:
            if len(self.videos_dir_names) != 0:
                # get file names into a list
                self.videos_names.clear()
                for file_name in os.listdir(SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[self.ui.videosDateListWidget.currentRow()]):
                    self.videos_names.append(file_name)
                # set the files in the widget
                if len(self.videos_names) == 0:
                    self.video_items.clear()
                    item = QListWidgetItem(self.ui.videosListWidget)
                    # if there is no video available, show the default video
                    self.video_thumbnails_pixmap = QPixmap(self.resource_path('icons' + os.sep + 'no_video_available.jpg'))
                    self.ui.currentVideoLabel.setPixmap(self.video_thumbnails_pixmap)
                    # clear the video properties
                    self.ui.currentVideoGroupBox.setTitle('FILE INFORMATION')
                else:
                    # sort the videos from the most recently taken to the least recently taken
                    self.videos_names.sort()
                    # clear the previous content of the video list widget
                    self.video_items.clear()
                    self.ui.videosListWidget.clear()
                    # if videos are available, set them into the list widget item
                    for video in self.videos_names:
                        item = QListWidgetItem(self.ui.videosListWidget)
                        icon = QIcon()
                        vid_capture = cv2.VideoCapture(SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[self.ui.videosDateListWidget.currentRow()] + os.sep + video)
                        ret, frame = vid_capture.read()
                        if ret:
                            frame = cv2.resize(frame, (800, 600))
                            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            img_width = rgb_image.shape[1]
                            img_height = rgb_image.shape[0]
                            self.embed_play_icon(rgb_image, img_width, img_height)
                            qimage = QImage(rgb_image.data, img_width, img_height, QImage.Format_RGB888)
                            qpixmap = QPixmap.fromImage(qimage)
                            icon.addPixmap(qpixmap, QIcon.Normal, QIcon.On)
                            vid_capture.release()
                            item.setIcon(icon)
                            self.video_items.append(item)
                    # set the grid size of video list widget and add the list widget item containing the list widget
                    self.ui.videosListWidget.setGridSize(QSize(110, 110))
                    self.ui.videosListWidget.addItem(item)
                    # set the first video as selected and show it on the label
                    self.ui.videosListWidget.setCurrentItem(self.video_items[-1])
                    self.get_show_selected_video_thumbnail()
        except IndexError:
            pass

    def refresh_video_dir_list_instantly(self):
        """
        This method refreshes the list of directory in the date list widget after date folder is deleted
        """
        try:
            # get directory names (dates) into a list
            self.videos_dir_names.clear()
            for dir_name in os.listdir(SAVED_VIDEOS_BASE_DIR):
                self.videos_dir_names.append(dir_name)
            if len(self.videos_dir_names) != 0:
                # sort the videos from the most recently taken to the least recently taken
                self.videos_dir_names.sort()
                self.videos_dir_names.reverse()
                # clear the previous content of the video list widget
                self.ui.videosDateListWidget.clear()
                # if directories are available, set them into the list widget item
                self.ui.videosDateListWidget.addItems(self.videos_dir_names)
                # set the first video as selected and show it on the label
                self.ui.videosDateListWidget.setCurrentRow(0)
            else:
                # if the last folder is deleted, clear all image resources and reset the label to default
                self.videos_names.clear()
                self.video_items.clear()
                self.ui.videosListWidget.clear()
                self.videos_dir_names.clear()
                self.ui.videosDateListWidget.clear()
                self.video_thumbnails_pixmap = QPixmap(self.resource_path('icons' + os.sep + 'no_video_available.jpg'))
                self.ui.currentVideoLabel.setPixmap(self.video_thumbnails_pixmap)
                # clear the video properties
                self.ui.currentVideoGroupBox.setTitle('FILE INFORMATION')
        except IndexError:
            pass

    def get_show_selected_video_thumbnail(self):
        """
        This method sets the selected video to the label
        """
        try:
            # check if there is a videos directory
            if len(self.videos_dir_names) != 0:
                # get the name of the video file
                video_file_name = self.videos_names[self.ui.videosListWidget.currentRow()]
                # split the file name to separate the time from the camera id
                file_name_split = video_file_name.split('_')
                # if the name of the camera id contains underscores too, join them again since they would also split
                camera_id = '_'.join(file_name_split[:-1])
                # get the time from the splitted file name
                time_taken = file_name_split[-1].split('.')[0]
                # load the video thumbnail and set it as the current video
                vid_capture = cv2.VideoCapture(SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[self.ui.videosDateListWidget.currentRow()] + os.sep + video_file_name)
                ret, frame = vid_capture.read()
                if ret:
                    frame = cv2.resize(frame, (800, 600))
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img_width = rgb_image.shape[1]
                    img_height = rgb_image.shape[0]
                    self.embed_play_icon(rgb_image, img_width, img_height)
                    qimage = QImage(rgb_image.data, img_width, img_height, QImage.Format_RGB888)
                    qpixmap = QPixmap.fromImage(qimage)
                    vid_capture.release()
                    self.videos_thumbnails_pixmap = qpixmap
                    self.ui.currentVideoLabel.setPixmap(self.videos_thumbnails_pixmap)
                    # place the camera id of the camera used to capture the video and the time it was captured
                    self.ui.currentVideoGroupBox.setTitle('SOURCE ID: ' + camera_id + '\t\t|\t\t' + 'TIME OF CAPTURE: ' +
                                                          time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time_taken))))
            else:
                self.ui.currentVideoLabel.setPixmap(QPixmap(self.resource_path('icons' + os.sep + 'no_video_available.jpg')))
                # clear the video properties
                self.ui.currentVideoGroupBox.setTitle('FILE INFORMATION')
        except IndexError:
            pass

    def set_video_to_previous(self):
        """
        This method sets the previous video as the current one
        """
        try:
            if len(self.videos_dir_names) != 0:
                if len(self.videos_names) != 0:
                    if self.ui.videosListWidget.currentRow() > 0:
                        self.ui.videosListWidget.setCurrentItem(self.video_items[self.ui.videosListWidget.currentRow() - 1])
                        self.get_show_selected_video_thumbnail()
                    else:
                        self.ui.videosListWidget.setCurrentItem(self.video_items[len(self.videos_names) - 1])
                        self.get_show_selected_video_thumbnail()
        except IndexError:
            pass

    def set_video_dir_to_previous(self):
        """
        This method sets the previous directory as the current one
        """
        try:
            if len(self.videos_dir_names) != 0:
                if self.ui.videosDateListWidget.currentRow() > 0:
                    self.ui.videosDateListWidget.setCurrentRow(self.ui.videosDateListWidget.currentRow() - 1)
                else:
                    self.ui.videosDateListWidget.setCurrentRow(len(self.videos_dir_names) - 1)
        except IndexError:
            pass

    def set_video_to_next(self):
        """
        This method sets the next video as the current one
        """
        try:
            if len(self.videos_dir_names) != 0:
                if len(self.videos_names) != 0:
                    if self.ui.videosListWidget.currentRow() < len(self.videos_names) - 1:
                        self.ui.videosListWidget.setCurrentItem(self.video_items[self.ui.videosListWidget.currentRow() + 1])
                        self.get_show_selected_video_thumbnail()
                    else:
                        self.ui.videosListWidget.setCurrentItem(self.video_items[0])
                        self.get_show_selected_video_thumbnail()
        except IndexError:
            pass

    def set_video_dir_to_next(self):
        """
        This method sets the next directory as the current one
        """
        try:
            if len(self.videos_dir_names) != 0:
                if self.ui.videosDateListWidget.currentRow() < len(self.videos_dir_names) - 1:
                    self.ui.videosDateListWidget.setCurrentRow(self.ui.videosDateListWidget.currentRow() + 1)
                else:
                    self.ui.videosDateListWidget.setCurrentRow(0)
        except IndexError:
            pass

    def delete_video_file(self):
        """
        This method deletes the selected video file
        """
        try:
            # get the selected file name
            selected_video_file_name = self.videos_names[self.ui.videosListWidget.currentRow()]
            ret_val = QMessageBox.question(self, 'Delete', 'Do really want to delete selected video?')
            # delete file after confirmation
            if ret_val == QMessageBox.Yes:
                # get currently select video index
                video_index = self.ui.videosListWidget.currentRow()
                # delete video
                os.remove(SAVED_VIDEOS_BASE_DIR + os.sep + self.videos_dir_names[self.ui.videosDateListWidget.currentRow()] + os.sep + selected_video_file_name)
                # refresh the videos list widget
                self.refresh_videos_instantly()
                # select the previous video if any else select the next video
                if len(self.videos_names) > 1:
                    if video_index-1 >= 0:
                        self.ui.videosListWidget.setCurrentRow(video_index - 1)
                    else:
                        self.ui.videosListWidget.setCurrentRow(video_index)
        except IndexError:
            pass
        except:
            QMessageBox.critical(self, 'Delete Error', 'An error occurred while attempting to delete the currently selected video!')

    def delete_video_date(self):
        """
        This method deletes all the videos in the selected date
        """
        try:
            # get the selected directory name
            selected_dir_name = self.videos_dir_names[self.ui.videosDateListWidget.currentRow()]
            dir_file_count = len(os.listdir(SAVED_VIDEOS_BASE_DIR + os.sep + selected_dir_name))
            if dir_file_count == 0:
                ret_val = QMessageBox.question(self, 'Delete directory', 'Delete ' + selected_dir_name + ' directory')
            else:
                ret_val = QMessageBox.question(self, 'Delete directory', 'Delete ' + selected_dir_name + ' directory along with ' +
                                               str(dir_file_count) + ' video files')
            # delete file after confirmation
            if ret_val == QMessageBox.Yes:
                # get currently selected video index
                dir_index = self.ui.videosDateListWidget.currentRow()
                # delete video
                shutil.rmtree(SAVED_VIDEOS_BASE_DIR + os.sep + selected_dir_name)
                # refresh the videos list widget
                self.refresh_video_dir_list_instantly()
                # select the previous image if any else select the next video
                if len(self.videos_dir_names) > 1:
                    if dir_index-1 >= 0:
                        self.ui.videosDateListWidget.setCurrentRow(dir_index - 1)
                    else:
                        self.ui.videosDateListWidget.setCurrentRow(dir_index)
        except IndexError:
            pass
        except:
            QMessageBox.critical(self, 'Delete Error', 'An error occurred while attempting to delete the currently selected directory!')

    def delete_all_videos(self):
        """
        This method deletes all the videos
        """
        try:
            ret_val = QMessageBox.question(self, 'Delete All Saved Videos',  'Do you want to delete ALL saved videos?')
            # delete after confirmation
            if ret_val == QMessageBox.Yes:
                # delete recording date directories
                for dir_name in os.listdir(SAVED_VIDEOS_BASE_DIR):
                    shutil.rmtree(SAVED_VIDEOS_BASE_DIR + os.sep + dir_name)
                # refresh the recordings list widget
                self.refresh_video_dir_list_instantly()
        except IndexError:
            pass
        except:
            QMessageBox.critical(self, 'Delete Error', 'An error occurred while attempting to delete all saved videos')

    def video_list_widget_key_press_events(self, event):
        """
        This method adds key events to the video list widget
        """
        # get the key
        key_pressed = event.key()
        if key_pressed == Qt.Key_Left:
            self.set_video_to_previous()
        if key_pressed == Qt.Key_Right:
            self.set_video_to_next()
        if key_pressed == Qt.Key_Delete:
            self.delete_video_file()

    def videos_dir_list_widget_key_press_events(self, event):
        """
        This method adds key events to the date list widget
        """
        # get the key
        key_pressed = event.key()
        if key_pressed == Qt.Key_Up:
            self.set_video_dir_to_previous()
        if key_pressed == Qt.Key_Down:
            self.set_video_dir_to_next()
        if key_pressed == Qt.Key_Delete:
            self.delete_video_date()

####---------------------------------------------------------------------OTHER GENERAL OPERATIONS-----------------------------------------------------------------------------####

    # argument types: Mat, int, int
    def embed_play_icon(self, rgb_image, img_width, img_height):
        """
        This method places the play icon in the first frame of every video to be displayed in the videos and motion recordings gallery
        """
        # get the region of interest from the frame
        roi = rgb_image[int(img_width/2)-150:int(img_width/2)-50, int(img_height/2)+50:int(img_height/2)+150]
        # convert frame to grayscale
        img2gray = cv2.cvtColor(self.play_video_image, cv2.COLOR_BGR2GRAY)
        # create a mask for embedding the icon
        ret, mask = cv2.threshold(img2gray, 10, 255, cv2.THRESH_BINARY)
        mask_inv = cv2.bitwise_not(mask)
        # Now black-out the area of image in ROI
        img1_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
        # Take only region of image from image.
        img2_fg = cv2.bitwise_and(self.play_video_image, self.play_video_image, mask=mask)
        # Put image in ROI and modify the main image
        dst = cv2.add(img1_bg, img2_fg)
        rgb_image[int(img_width/2)-150:int(img_width/2)-50, int(img_height/2)+50:int(img_height/2)+150] = dst

    def resource_path(self, relative_path):  # argument types: String
        """
        This method genrates the relative paths to all the resources used in the application
        including image files, source file, media files and what have you. It is very
        necessary because it preserves the path to the resources after producing the
        executable for the application
        """
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def closeEvent(self, event):
        """
        This method cleans up memory releases all resources when application is closed
        """
        ret_val = QMessageBox.question(self, 'Confirm Exit', 'Do you really want to quit Alpha?', QMessageBox.Yes | QMessageBox.No)
        if ret_val == QMessageBox.Yes:
            # close add new stream dialog if open
            self.add_stream_dialog.close()
            # close the video player when open
            self.video_player.close()
            # close all video streaming threads
            for thread, video_subwindow in zip(all_streaming_threads, all_video_subwins):
                if thread.video_playing:
                    video_subwindow.end_capture()
            # close window
            event.accept()
            # close python interpreter
            sys.exit(0)
        else:
            event.ignore()


############################################################################################ THE VIDEO STREAMING CUSTOM WIDGET CLASS ############################################################################################


# this holds a list of ids of recognized faces purposely for searching and rearrangement of the table
currently_recog_id_list = []


class MdiSubWindow(QMdiSubWindow, QWidget):
    """
    This is a custom mdi sub window that recieves that video feed on a separate thread for every instance
    """

    def __init__(self, camera_id, win_name, resource_path_func, parent_mdi):
        # argument types: String or int, String, Function, MdiArea, QTableWidget, QLineEdit
        super().__init__()
        # initialize the sub window widget generated code and setup
        self.ui = Ui_mdiSubWIndowContent()
        self.ui.setupUi(self)
        self.setStyleSheet("QMdiSubWindow{background-color: #333333;border: 4px solid #101010;border-radius: 10px;}" +
                           "QMdiSubWindow::title {height: 10px;background-color: #333333;}")
        # create the parent widget object
        self.widget_parent = QWidget()
        # get a reference to the resource_path method
        self.resource_path = resource_path_func
        # set the sub window name using the camera name and index
        self.win_name = win_name
        self.sub_win_name = win_name  # + '-' + str(camera_id)
        self.ui.sourceIdLabel.setText(self.sub_win_name)
        # self.setWindowTitle(self.sub_win_name)
        # initialize the video capture thread
        self.vid_cap_thread = VideoCaptureThread(camera_id, win_name, self.resource_path)
        self.vid_cap_thread.send_logger_data.connect(self.handle_logger_data)
        # add the thread to the list of video streaming threads
        all_streaming_threads.append(self.vid_cap_thread)
        # set the minimum size the for the sub window
        self.setMinimumSize(200, 150)
        # set the preferred size of the sub window
        self.resize(320, 240)
        # set default image
        self.ui.displayLabel.setPixmap(QPixmap(self.resource_path('icons' + os.sep + 'default_camera_view.png')))
        # set the image returned by the signal to the label
        self.vid_cap_thread.change_pixmap.connect(self.ui.displayLabel.setPixmap)
        self.previously_recognized_id = ''
        # add the root layout from the generated code to parent widget
        self.widget_parent.setLayout(self.ui.gridLayout)
        # add the parent widget to the mdi sub window
        self.setWidget(self.widget_parent)
        # turn on video capture switch
        self.vid_cap_thread.start_capture()
        # turn off the snapshot switch
        self.vid_cap_thread.abort_snapshot()
        # get reference to parent mdi window
        self.parent_mdi_area = parent_mdi
        # add events to buttons, checkboxes and radio buttons
        self.ui.startButton.clicked.connect(self.start_capture)
        self.ui.endButton.clicked.connect(self.end_capture)
        self.ui.snapshotButton.clicked.connect(self.take_snapshot)
        self.ui.coloredRadioButton.toggled.connect(self.switch_to_colored)
        self.ui.grayscaleRadioButton.toggled.connect(self.switch_to_grayscale)
        self.ui.embedTimeCheckBox.toggled.connect(self.toggle_embedded_time)
        self.ui.saveVideoCheckBox.toggled.connect(self.save_video)
        self.ui.peopleCounterCheckbox.toggled.connect(self.start_stop_counting)
        # hide and show the options frame when the display label is double clicked
        self.frame_hidden = False   # monitor if frame is hidden or not
        self.ui.displayLabel.mouseDoubleClickEvent = self.hide_options_frame

    def handle_logger_data(self, send_logger_data_signal):
        """
        Handles the logger from the video threads
        """
        # add the data to the logger thread's queue
        logger_thread.enqueue(send_logger_data_signal)

    def start_capture(self):
        """
        This method starts the video streaming thread
        """
        self.save_video()
        self.vid_cap_thread.abort_snapshot()
        self.vid_cap_thread.start_capture()
        self.vid_cap_thread.start()

    def end_capture(self):
        """
        This method stops the video streaming thread
        """
        self.vid_cap_thread.stop_saving_vid_to_disk()
        self.vid_cap_thread.abort_snapshot()
        self.vid_cap_thread.stop_capture()

    def start_stop_counting(self):
        """
        This method enables facial recogntion
        """
        if self.ui.peopleCounterCheckbox.isChecked():
            self.vid_cap_thread.start_counting()
        else:
            self.vid_cap_thread.stop_counting()

    def take_snapshot(self):
        """
        This method takes a snapshot
        """
        if self.win_name[-1].isdigit():
            self.vid_cap_thread.take_snapshot(self.win_name.split('/')[-1])
        else:
            self.vid_cap_thread.take_snapshot(self.win_name)

    def toggle_embedded_time(self):
        """
        This method enables and disables the embedded time
        """
        self.vid_cap_thread.toggle_embedded_time()

    def switch_to_grayscale(self):
        """
        This method switches the video stream from colored to grayscale
        """
        self.vid_cap_thread.to_grayscale()

    def switch_to_colored(self):
        """
        This method switches the video stream from grayscale to colored
        """
        self.vid_cap_thread.to_colored()

    def save_video(self):
        """
        This method save the video stream to the local disk
        """
        if self.ui.saveVideoCheckBox.isChecked():
            if self.win_name[-1].isdigit():
                self.vid_cap_thread.activate_vid_saving_to_disk(self.win_name.split('/')[-1])
            else:
                self.vid_cap_thread.activate_vid_saving_to_disk(self.win_name)
        else:
            self.vid_cap_thread.stop_saving_vid_to_disk()

    def hide_options_frame(self, event):
        """
        This method hides and shows the options frame when the display label is double clicked
        """
        if self.frame_hidden:
            self.ui.optionsScrollArea.show()
            self.setWindowFlags(Qt.WindowFullscreenButtonHint)
            self.frame_hidden = False
        else:
            self.ui.optionsScrollArea.hide()
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.frame_hidden = True

    def closeEvent(self, event):
        """
        This method handles closing requests on the sub window and stops the video streaming before
        closing the sub window
        """
        # request a confirmation to close video stream
        ret_val = QMessageBox.question(self, 'Confirm Exit', 'Do you really want to quit ' + self.sub_win_name + '?')
        if ret_val == QMessageBox.Yes:
            # if confirmed, stop camera stream and turn off snapshot in case it is on
            self.vid_cap_thread.stop_capture()
            self.vid_cap_thread.abort_snapshot()
            # remove this threads sub window from the subwindow list
            all_video_subwins.pop(all_streaming_threads.index(self.vid_cap_thread))
            # remove thread from thread list
            all_streaming_threads.remove(self.vid_cap_thread)
            # close the sub window
            event.accept()
        else:
            # if declined, keep the stream running
            event.ignore()


############################################################################################ THE ADD NEW STREAM CLASS ############################################################################################


class AddNewStream(QDialog):
    """
    This class adds a new video stream to the camera view
    """

    def __init__(self, mdi_area_obj, mdi_sub_win_obj, resource_path_func, tile_window_view_func):
        # argument types: MdiArea, MdiSubWindow, Function, Function, QTableWidget, QLineEdit
        """
        This class adds a new streaming source as selected by the user
        """
        super().__init__()
        self.ui = Ui_addCameraDialog()
        self.ui.setupUi(self)
        # get mdiArea and mdi sub window objects as well as resource path and tiled window view methods
        self.mdi_area = mdi_area_obj
        self.mdi_sub_win = mdi_sub_win_obj
        self.resource_path = resource_path_func
        self.tile_window_view = tile_window_view_func
        # set maximum number of streams allowed
        self.max_num_of_streams_allowed = 100
        # set window icon
        self.setWindowIcon(QIcon(self.resource_path('icons' + os.sep + 'alpha_icon.png')))
        # load cameras into combobox
        self.load_usb_cameras()
        # connect buttons to actions
        self.ui.addStreamButton.clicked.connect(self.get_new_stream_source)
        self.ui.reloadCamerasButton.clicked.connect(self.load_usb_cameras)
        self.ui.usbSourceRadioButton.toggled.connect(self.select_usb_cam)
        self.ui.chooseFileButton.clicked.connect(self.choose_file)
        # set the multiple streams list separator
        self.multi_streams_list_sep = '||$$^^&&**||'

    def get_new_stream_source(self):
        """
        This method adds the selected video stream to the camera view
        """
        if self.ui.streamNameField.text().strip() != '':
            if len(all_streaming_threads) < self.max_num_of_streams_allowed:
                # check if invalid symbols are present in the name of the stream
                unaccepted_naming_chars = ['/', '\\', '\\\\', '//']
                invalid_name = False
                for item in unaccepted_naming_chars:
                    if self.ui.streamNameField.text().__contains__(item):
                        invalid_name = True
                # if the name is valid, proceed to add stream else show error message
                if not invalid_name:
                    if self.ui.usbSourceRadioButton.isChecked():
                        if self.ui.camerasCombobox.currentText().strip() != '':
                            # get the name of the stream
                            stream_name = self.ui.streamNameField.text()
                            # check if the stream name already exists
                            name_exists = False
                            for sub_win in all_video_subwins:
                                if sub_win.win_name == stream_name.strip():
                                    name_exists = True
                            if not name_exists:
                                # get the index of the camera and use it as the stream id
                                list_of_cameras = QCameraInfo.availableCameras()
                                camera_name = self.ui.camerasCombobox.currentText()
                                for camera in list_of_cameras:
                                    if camera.description().split(':')[0] == camera_name:
                                        camera_index = int(camera.position())
                                        new_sub_win = self.mdi_sub_win(camera_index, stream_name, self.resource_path, self.mdi_area)
                                        self.mdi_area.addSubWindow(new_sub_win)
                                        new_sub_win.show()
                                        # add sub window to all videos sub windows list
                                        all_video_subwins.append(new_sub_win)
                                        break
                            else:
                                QMessageBox.critical(self, 'Invalid Name', 'Stream name already exists')
                        else:
                            QMessageBox.information(self, 'Select stream source', 'No stream source selected. Cancel operation or select stream source')
                    elif self.ui.urlSourceRadioButton.isChecked():
                        # get the name of the stream and the url
                        stream_name = self.ui.streamNameField.text()
                        url = self.ui.urlAddressField.text().strip()
                        # check if the stream name already exists
                        name_exists = False
                        for sub_win in all_video_subwins:
                            if sub_win.win_name == stream_name.strip():
                                name_exists = True
                        if not name_exists:
                            new_sub_win = self.mdi_sub_win(url, stream_name, self.resource_path, self.mdi_area)
                            self.mdi_area.addSubWindow(new_sub_win)
                            new_sub_win.show()
                            # add sub window to all videos sub windows list
                            all_video_subwins.append(new_sub_win)
                        else:
                            QMessageBox.critical(self, 'Invalid Name', 'Stream name already exists')
                    # tile the window view
                    self.tile_window_view()
                else:
                    QMessageBox.critical(self, 'Invalid Name', r'Stream name must not contain "/", "//", "\" or "\\"')
            else:
                QMessageBox.information(self, 'Stream Notification', 'Maximum number of streams (' + str(self.max_num_of_streams_allowed) +
                                        ') reached. You can only replace an existing stream by closing it and starting the new one')
        else:
            QMessageBox.critical(self, 'Invalid Name', r'Please name the video stream')

    def choose_file(self):
        """
        This method selects the video from a file on the local drive
        """
        # open the file explorer to select any number of videos
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Video File', QDir.homePath(),
                                                   'Video Files (*.mp4 *.avi *.flv *.ogg *.3gp *.ma4 *.mkv *.mov *.mpeg *.mpg)',
                                                   options=options)
        if file_path:
            self.ui.urlAddressField.setText(file_path)
            self.ui.streamNameField.setText(file_path.split('/')[-1])

    def load_usb_cameras(self):
        """
        This method loads all the connected usb cameras
        """
        list_of_cameras = QCameraInfo.availableCameras()
        camera_names = [camera.description().split(':')[0] for camera in list_of_cameras]
        self.ui.camerasCombobox.clear()
        self.ui.camerasCombobox.addItems(camera_names)

    def select_usb_cam(self):
        """
        This method sets the selected usb camera as the stream source
        """
        self.ui.streamNameField.setText(self.ui.camerasCombobox.currentText())


############################################################################################ THE MAIN APPLICAITON THREAD STARTER ############################################################################################


if __name__ == '__main__':
    # get the qt application thread
    app = QApplication(sys.argv)
    # grab the main window
    mainWindow = Alpha()
    # show the main window
    mainWindow.showMaximized()
    # exit the qt application thread when main window is closed
    sys.exit(app.exec_())
