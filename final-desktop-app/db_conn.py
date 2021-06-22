import os, sqlite3
from constants import DATABASES_BASE_DIR


class DbConnection():
    """
    This class handles database connection and creation of tables
    """

    def __init__(self):
        self.connection = sqlite3.connect(DATABASES_BASE_DIR + os.sep + 'alpha.sqlite')
        self.cursor = self.connection.cursor()
        self.connection.commit()

    def close_connection(self):
        """
        This method closes the database connection
        """
        self.connection.close()
