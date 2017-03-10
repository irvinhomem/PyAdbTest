
import logging

class PyAdb(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        # self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)


    def adb_start(self):


    def adb_list_devices(self):

