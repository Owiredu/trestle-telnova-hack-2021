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