import os

# application version
APP_VERSION = '1.0.0'

# the applications storage directory
APP_STORAGE_DIR = os.path.join(os.path.expanduser('~'), '.alpha_c')

# base directory of the saved videos
SAVED_VIDEOS_BASE_DIR = os.path.join(APP_STORAGE_DIR, 'saved_videos')

# base directory of the snapshots
SNAPSHOTS_BASE_DIR = os.path.join(APP_STORAGE_DIR, 'snapshots')

# base directory of databases
DATABASES_BASE_DIR = os.path.join(APP_STORAGE_DIR, 'databases')

# classes of detectable objects
CLASSES = [
    "background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"
    ]

# format for the logger data transmitted from the video thread to the logger thread
# logger_data = {
# 	'date_id': '',
# 	'cam_id': '',
# 	'cam_data': {'enter': 0, 'exit': 0, 'current_in': 0}
# }