import sys, os, sqlite3


class DbConnection():
    """
    This class handles database connection and creation of tables
    """

    def __init__(self):
        self.connection = sqlite3.connect(self.resource_path('databases//alpha.sqlite'))
        self.cursor = self.connection.cursor()
        self.create_public_data_table()
        self.create_recog_data_table()
        self.connection.commit()

    def create_recog_data_table(self):
        """
        This method creates the facial recognition table table if it does not exist
        """
        query = '''CREATE TABLE IF NOT EXISTS recog_data (
	ID TEXT NOT NULL,
	NAME TEXT NOT NULL,
	RECOG_TIME TEXT NOT NULL,
	VIDEO_SOURCE TEXT NOT NULL,
	TAG TEXT DEFAULT 'NORMAL',
	IMAGE_NAME TEXT NOT NULL
	);'''
        self.cursor.execute(query)

    def create_public_data_table(self):
        """
        This method creates the public database table if it does not exist
        """
        query = '''CREATE TABLE IF NOT EXISTS public_data (
	ID TEXT NOT NULL,
	NAME TEXT NOT NULL,
	AGE INT NOT NULL,
	DATE_OF_BIRTH TEXT NOT NULL,
	RESIDENCE TEXT NOT NULL,
	PHONE_NUMBER TEXT NOT NULL,
	EMAIL_ADDRESS TEXTNOT_NULL,
	OCCUPATION TEXT,
	POSTAL_ADDRESS TEXT,
	PHOTO BLOB NOT NULL,
	PRIMARY KEY(ID)
        );'''
        self.cursor.execute(query)

    def close_connection(self):
        """
        This method closes the database connection
        """
        self.connection.close()

    def resource_path(self, relative_path):  # argument types: String
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)
