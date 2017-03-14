
import logging
import subprocess
#import multiprocessing as mp
import os
import platform
import getpass
import ctypes
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

        self.android_sdk_path = ''
        self.adb_executable_loc = self.find_adb_location()
        # self.android_sdk_path set in function above

        if self.adb_executable_loc == '':
            self.logger.info("ADB not found!")
            exit()


    def find_adb_location(self):
        # Check OS
        os_name = os.name
        self.logger.debug("OS Name = %s " % os_name)
        # Check platform
        plat_system = platform.system()
        self.logger.debug("Platform System = %s " % plat_system)
        plat_platform = platform.platform()
        self.logger.debug("Platform Platform = %s " % plat_platform)
        plat_release = platform.release()
        self.logger.debug("Platform Release = %s " % plat_release)
        plat_version = platform.version()
        self.logger.debug("Platform Version = %s " % plat_version)

        # Check possible locations irrespective of OS
        # Get user name
        user_name = getpass.getuser()
        self.logger.debug("Username = %s " % user_name)
        # Get Home Directory
        #homedir = os.environ['HOME']
        homedir = os.path.expanduser('~')
        self.logger.debug("Home Directory = %s " % homedir)

        # Check under Root Dir
        #path_exists = False
        adb_loc = ''
        under_win_sdk_loc = os.path.join('platform-tools', 'adb.exe')
        under_linux_sdk_loc = os.path.join('platform-tools', 'adb')
        android_sdk_dir = os.path.join("Android", 'sdk')
        app_data_local_path = os.path.join("AppData","Local")
        win_user_dir = os.path.join(homedir, app_data_local_path, android_sdk_dir)
        self.logger.debug("Windows User Dir: %s" % win_user_dir)
        if plat_system == "Windows":
            # root_dir = os.getenv('SystemDrive')
            root_dir = os.path.abspath(os.sep)
            windows_root_loc = os.path.join(root_dir, android_sdk_dir)
            self.logger.debug("Windows C: Drive = %s " % windows_root_loc)
            if os.path.exists(windows_root_loc):
                adb_loc = os.path.join(windows_root_loc, under_win_sdk_loc)
            elif os.path.exists(os.path.join(win_user_dir)):
                adb_loc = os.path.join(win_user_dir, under_win_sdk_loc)

        # Check if they match

        # If they don't check config file

        # Store ADB runtime config location
            if adb_loc != '':
                if os.path.exists(adb_loc):
                    self.logger.debug("Need to store local ADB loc: %s" % adb_loc)
                    # Set Android SDK Path (By getting the Grand-Parent Dir)
                    self.android_sdk_path = os.path.abspath(os.path.join(
                        os.path.abspath(os.path.join(adb_loc, os.path.pardir)),
                        os.path.pardir))
                    self.logger.debug("Android SDK Path: %s" % self.android_sdk_path)
                else:
                    self.logger.debug("Something wrong with ADB path: %s" % adb_loc)
            else:
                self.logger.info("Android SDK / ADB path not found")

        # Return boolean or path?
        return adb_loc


    def adb_start(self):
        # If ADB location has been found use it
        cmd = [self.adb_executable_loc, 'root']
        #self.adb_process = subprocess.call(cmd)
        #self.adb_process = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        #adb_process = subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True)
        adb_process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        #self.adb_process = mp.Process("ADB service", subprocess.call(cmd))
        #adb_serv = self.adb_process.start()
        #for line in self.adb_process:
        #    self.logger.info("Started: %s" % str(line))
        self.logger.info("Started ADB: \n Output (if any): %s" % str(adb_process.stdout))
        #self.logger.info("Started ADB: \n Error Output (if any): %s" % str(adb_process.stderr))


    def adb_list_devices(self):
        cmd = [self.adb_executable_loc, 'devices']
        #list_devices_output = subprocess.call(cmd)
        #list_devices_output = subprocess.run(cmd, universal_newlines=True, stdout=subprocess.PIPE, shell=True)
        list_devices_output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        self.logger.info("Devices Output: \n %s" % str(list_devices_output.stdout))
        #self.logger.info("Devices Error Output (if any): \n %s" % str(list_devices_output.stderr))

    def adb_get_packages_installed(self):
        cmd = [self.adb_executable_loc, '-e', 'shell', 'pm', 'list', 'packages', '-f']
        all_packages_output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        self.logger.info("Devices Output: \n %s" % str(all_packages_output.stdout))

        # Parse output to return a list of some sort.
        # If stripped-line contains starts with the word "package:", extract items as a List of Dictionaries
        line_list = str(all_packages_output.stdout).split("\n")
        packages_list = []

        for line in line_list:
            if line.strip().startswith('package:'):
                package_info = dict()
                package_info['path'] =line.lstrip('package:').split("=")[0]
                package_info['pkg_name'] = line.lstrip('package:').split("=")[1]
                packages_list.append(package_info)

        self.logger.debug("List number: %s" % str(len(packages_list)))
        if len(packages_list) > 2:
            self.logger.debug("Line #1: Path: %s" % str(packages_list[0]['path']))
            self.logger.debug("Line #1: Name: %s" % str(packages_list[0]['pkg_name']))
            self.logger.debug("Line #2: Path: %s" % str(packages_list[1]['path']))
            self.logger.debug("Line #2: Name: %s" % str(packages_list[1]['pkg_name']))
            self.logger.debug("Line #3: Path: %s" % str(packages_list[2]['path']))
            self.logger.debug("Line #3: Name: %s" % str(packages_list[2]['pkg_name']))

        return packages_list

    def adb_list_running_apps:

    def adb_get_main_activity:

    def parse_manifest_xml:

adb_proc = PyAdb()
adb_proc.adb_start()
adb_proc.adb_list_devices()
adb_proc.adb_get_packages_installed()



