
import logging
import subprocess
import os
import platform
#from com.android.monkeyrunner import MonkeyRunner, MonkeyDevice


class PyAdb(object):

    def __init__(self):
        # Configure Logging
        logging.basicConfig(level=logging.INFO)
        # logging.basicConfig(level=logging.WARNING)
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.INFO)
        self.logger.setLevel(logging.DEBUG)
        # self.logger.setLevel(logging.WARNING)

        self.find_adb_location();

    def find_adb_location(self):
        # Check OS
        os_name = os.name
        self.logger.debug("OS Name = %s " % os_name)
        # Check platform
        platform.system()
        platform.platform()
        platform.release()
        platform.version()
        # Check possible locations irrespective of OS
        # Get user name


        # Check if they match

        # If they don't check config file

        # Store ADB runtime config location

        # Return boolean or path?


    def adb_start(self):
        # If ADB location has been found use it
        cmd = ['adb', 'root']
        start_output = subprocess.call(cmd)
        self.logger.info("Start: %s" % str(start_output))


    def adb_list_devices(self):
        cmd = ['adb', 'devices']
        subprocess.call(cmd)

adb_proc = PyAdb()

# adb_proc.adb_start()
# adb_proc.adb_list_devices()



