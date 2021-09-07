import sys, time, os, shutil
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
import vlc
from video_player_ui import Ui_videoPlayerMainWindow


class VideoPlayer(QMainWindow):
    '''
    This is the embedded video player for the application
    '''
    
    def __init__(self):
        super().__init__()
        self.ui = Ui_videoPlayerMainWindow()
        self.ui.setupUi(self)
        # create a timer for updating the user interface
        self.timer = QTimer(self)
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.update)
        # load  icons
        self.play_icon = QIcon(QPixmap(self.resource_path('icons' + os.sep + 'play.png')))
        self.pause_icon = QIcon(QPixmap(self.resource_path('icons' + os.sep + 'pause.gif')))
        self.repeat_on_icon = QIcon(QPixmap(self.resource_path('icons' + os.sep + 'repeat_on.png')))
        self.repeat_off_icon = QIcon(QPixmap(self.resource_path('icons' + os.sep + 'repeat_off.png')))
        # creating a basic vlc instance
        self.instance = vlc.Instance()
        # creating an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()
        # set paused to false to play the video when window opens and set stop button click checker
        self.isPaused = False
        self.stop_clicked = False
        # connect buttons to actions
        self.ui.playPauseButton.clicked.connect(self.play_pause)
        self.ui.saveButton.clicked.connect(self.save_copy)
        self.ui.stopButton.clicked.connect(self.manual_stop)
        self.ui.progressSlider.sliderMoved.connect(self.set_position)
        self.ui.repeatButton.toggled.connect(self.visualize_repeat_state)
        self.ui.videoRateComboBox.currentTextChanged.connect(self.set_playback_rate)

    def play(self):
        '''
        This method plays the media
        '''
        self.stop_clicked = False
        self.mediaplayer.play()
        self.ui.playPauseButton.setIcon(self.pause_icon)
        self.ui.playPauseButton.setToolTip('Pause (SPACE BAR)')
        self.timer.start()
        self.isPaused = False

    def pause(self):
        '''
        This method pauses playback
        '''
        self.mediaplayer.pause()
        self.ui.playPauseButton.setIcon(self.play_icon)
        self.ui.playPauseButton.setToolTip('Play (SPACE BAR)')
        self.isPaused = True

    def play_pause(self):
        '''
        This method pauses or plays playback as appropriate
        '''
        if self.mediaplayer.is_playing():
            self.pause()
        else:
            self.play()

    def forward(self):
        """
        This method moves the video forward by 5 secs
        """
        try:
            # if the current time is equal to 5 secs less than the total duration,
            # ignore action else increase the time by 5 secs
            if self.mediaplayer.get_time() >= self.media.get_duration() - 5000:
                return
            else:
                self.mediaplayer.set_time(self.mediaplayer.get_time() + 5000)
        except:
            pass

    def backward(self):
        """
        This method moves the video backward by 5 secs
        """
        try:
            # if the current time is less than 5 secs set the time to 0
            # else reduce the current time by 5 secs
            if self.mediaplayer.get_time() < 5000:
                self.mediaplayer.set_time(0)
            else:
                self.mediaplayer.set_time(self.mediaplayer.get_time() - 5000)
        except:
            pass


    def stop(self):
        '''
        This method stops the player
        '''
        self.mediaplayer.stop()
        self.ui.playPauseButton.setIcon(self.play_icon)
        self.ui.playPauseButton.setToolTip('Play (SPACE BAR)')
        try:
            self.ui.currentTimeLabel.setText(time.strftime('%H:%M:%S', time.localtime(self.media.get_duration() / 1000)))
        except:
            pass

    def manual_stop(self):
        '''
        This method stops the player when the button is clicked
        '''
        self.stop_clicked = True
        self.stop()

    def open_file(self, video_file_path):  # argument types: String
        '''
        This method opens the video file
        '''
        # get the file path
        self.video_file_path = video_file_path
        # create the media
        self.media = self.instance.media_new(video_file_path)
        # put the media in the media player
        self.mediaplayer.set_media(self.media)
        # parse the metadata of the file
        self.media.parse()
        # split the file name to separate the time from the camera id
        self.video_file_name = video_file_path.split(os.sep)[-1]
        file_name_split = self.video_file_name.split('_')
        # if the name of the camera id contains underscores too, join them again since they would also split
        camera_id = '_'.join(file_name_split[:-1])
        # get the time from the splitted file name
        time_taken = file_name_split[-1].split('.')[0]
        # set the window title to the camera id and time taken
        self.setWindowTitle('SOURCE ID: ' + camera_id + ' | ' + 'TIME OF CAPTURE: ' +
                            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time_taken))))
        # set the duration of the media into the duration label
        self.ui.totalDurationLabel.setText(time.strftime('%H:%M:%S',
                                                         time.localtime(self.media.get_duration() / 1000)))
        # give the id of the QFrame (or similar object) to vlc, different platforms have different functions for this
        if sys.platform.startswith('linux'): # for Linux using the X Server
            self.mediaplayer.set_xwindow(self.ui.videoFrame.winId())
        elif sys.platform == "win32": # for Windows
            self.mediaplayer.set_hwnd(self.ui.videoFrame.winId())
        elif sys.platform == "darwin": # for MacOS
            self.mediaplayer.set_nsobject(int(self.ui.videoFrame.winId()))
        self.play()

    def save_copy(self):
        '''
        This method saves a copy of the currently selected video
        '''
        try:
            # get the extension
            file_ext = self.video_file_name.split('.')[-1]
            # show the save dialog
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, 'Save Selected Video', '', 'Video File (*.' + file_ext + ')',
                                                       options=options)
            # save a copy of the file
            if file_name:
                file_name = file_name + '.' + file_ext
                shutil.copyfile(self.video_file_path, file_name)
                QMessageBox.information(self, 'Copy Completed', 'Successfully copied video to ' + file_name)
        except:
            QMessageBox.critical(self, 'Error', 'Unable to load video', QMessageBox.Close)

    def set_position(self, position):  # argument types: int
        '''
        This method sets the position of the player
        '''
        self.mediaplayer.set_position(position / 1000.0)

    def set_playback_rate(self, text):
        """
        This method sets the playback rate
        """
        self.mediaplayer.set_rate(float(text.split()[-1]))

    def update(self):
        '''
        This method updates the progress slider, handles replays and stops playback
        '''
        # set the current time into the current time label
        self.ui.currentTimeLabel.setText(time.strftime('%H:%M:%S', time.localtime(self.mediaplayer.get_time() / 1000)))
        # set the slider to the desired position
        self.ui.progressSlider.setValue(self.mediaplayer.get_position() * 1000.0)

        if not self.mediaplayer.is_playing():
            # if nothing is playing, stop the timer
            self.timer.stop()
            if not self.isPaused:
                # stop the video video and set reset the play-pause button when the video ends
                self.stop()
                # if stop action was done manually with the button click, then stop the video
                # and do not replay or move to next if it is a playlist
                if not self.stop_clicked:
                    # if the repeat button is checked start playing the again
                    if self.ui.repeatButton.isChecked():
                        self.play()

    def visualize_repeat_state(self):
        '''
        This method changes the icon and tooltip of the repeat button when modes are switched
        '''
        if self.ui.repeatButton.isChecked():
            self.ui.repeatButton.setIcon(self.repeat_on_icon)
            self.ui.repeatButton.setToolTip('Repeat ON (R)')
        else:
            self.ui.repeatButton.setIcon(self.repeat_off_icon)
            self.ui.repeatButton.setToolTip('Repeat OFF (R)')


    def resource_path(self, relative_path):  # argument types: String
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    def keyPressEvent(self, event):
        key_pressed = event.key()
        # press F key to open a media file
        if key_pressed == Qt.Key_D:
            self.save_copy()
        # press the Space Bar to toggle pause and play
        elif key_pressed == Qt.Key_Space:
            self.play_pause()
        # press the S key to stop the media playback
        elif key_pressed == Qt.Key_S:
            self.manual_stop()
        # press the R key to toggle the repeat button
        elif key_pressed == Qt.Key_R:
            self.ui.repeatButton.toggle()
        # press the right arrow key to move forward by 5 seconds
        elif key_pressed == Qt.Key_Right:
            self.forward()
        # press the left arrow key to move backwarrd by 5 seconds
        elif key_pressed == Qt.Key_Left:
            self.backward()

    def closeEvent(self, event) -> None:
        self.manual_stop()
        return super().closeEvent(event)
