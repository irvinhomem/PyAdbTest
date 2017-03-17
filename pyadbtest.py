
import logging
import subprocess
#import multiprocessing as mp
import os
import platform
import getpass
import ctypes
import json
import axmlparserpy.axmlprinter as axmlprinter
#import axmlparserpy.apk as apk
import xml.dom.minidom as minidom
from xml.etree import ElementTree as ET

#import axmlparserpy.bytecode
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

        config_file_path = os.path.join('config', 'APK_PATH.txt')
        #config_file_path = os.path.join('config/APK_PATH.txt')

        self.apk_files_path = self.read_config_file(config_file_path)
        self.android_sdk_path = ''
        self.adb_executable_loc = self.find_adb_location()
        # self.android_sdk_path set in function above
        self.aapt_loc = self.set_aapt_loc()

        if self.adb_executable_loc == '':
            self.logger.info("ADB not found!")
            exit()

    def read_config_file(self, configPath):
        self.logger.debug("Config Path: %s" % str(configPath))
        with open(configPath) as data_file:
            data = json.load(data_file)
            self.logger.debug("APK Config Path: %s" % str(data['config']['apk_path']))

        return str(data['config']['apk_path'])

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

    def adb_list_running_apps(self):
        return

    def aapt_get_activity_list(self, apk_file_name):
        activity_listing = self.parse_manifest_xml(os.path.join(self.apk_files_path, apk_file_name))
        return

    def aapt_get_main_activity(self):
        return

    def set_aapt_loc(self):
        build_tools_path = os.path.join(self.android_sdk_path, 'build-tools')
        self.logger.debug("Build Tools Path: %s" % str(build_tools_path))
        sub_dirs = self.get_immediate_subdirectories(build_tools_path)

        sorted_list = sorted(sub_dirs)
        self.logger.debug("Largest Number/Alphabetically Dir: %s" % str(sorted_list[len(sorted_list)-1]))
        largest = sorted_list[len(sorted_list)-1]

        aapt_loc =''
        if platform.system() == "Windows":
            aapt_loc = os.path.join(self.android_sdk_path, 'build-tools', largest, 'aapt.exe')
        else:
            aapt_loc = os.path.join(self.android_sdk_path, 'build-tools', largest, 'aapt')

        self.logger.debug("AAPT Location set to: %s" % str(aapt_loc))

        return aapt_loc

    def get_immediate_subdirectories(self, a_dir):
        return [name for name in os.listdir(a_dir)
                if os.path.isdir(os.path.join(a_dir, name))]

    def use_AXML_Printer(self, apk_name):
        manifest_path = os.path.join(self.apk_files_path, apk_name, 'AndroidManifest.xml')
        ap = axmlprinter.AXMLPrinter(open(manifest_path,'rb').read())
        buff = minidom.parseString(ap.getBuff()).toxml()
        self.logger.debug('==================================')
        self.logger.debug(buff)
        self.logger.debug('==================================')

        #namespaces = {'owl': 'http://www.w3.org/2002/07/owl#'}
        namespaces = {'android': 'http://schemas.android.com/apk/res/android'}

        xml_doc = ET.fromstring(ap.getBuff())
        self.logger.debug("XML ROOT Tag: %s" % xml_doc.tag)
        self.logger.debug('Number of child elements: %i' % len(list(xml_doc)))
        self.logger.debug('Android APK main Package: %s' % xml_doc.get('package'))
        self.logger.debug('Version code: %s' % xml_doc.get('{http://schemas.android.com/apk/res/android}versionCode'))
        #self.logger.debug('XML NAMESPACE: %s' % xml_doc.get('xmlns:android'))


        for child in xml_doc:
            self.logger.debug('Child: [%s] \n Attribute: [%s]' % (str(child.tag), str(child.attrib)))
        #buff.getElementsByTagName


        self.logger.debug('*****************')
        self.logger.debug("This doesn't work")
        for activity in xml_doc.findall('application/activity', namespaces):
            activity_name = activity.get('name')
            self.logger.debug("APP ACTIVITY Name: %s" % activity_name)

        self.logger.debug('*****************')
        for activity in xml_doc.findall('application/activity'):
            activity_name = activity.get('{http://schemas.android.com/apk/res/android}name')
            self.logger.debug("APP ACTIVITY Name: %s" % activity_name)

        self.logger.debug('*****************')

        for activity in xml_doc.findall('.//activity'):
            activity_name = activity.get('{http://schemas.android.com/apk/res/android}name')
            self.logger.debug("With xPath ACTIVITY Name: %s" % activity_name)

        self.logger.debug('*****************')

        for activity in xml_doc.findall('uses-permission'):
            activity_name = activity.get('{http://schemas.android.com/apk/res/android}name')
            self.logger.debug("PERMISSIONS Name: %s" % activity_name)

        self.logger.debug('*****************')

    def parse_manifest_xml(self, apk_file_path):
        cmd = [self.aapt_loc, 'dump', 'xmltree', apk_file_path, 'AndroidManifest.xml']
        apk_xml_output = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                             universal_newlines=True, shell=True)

        self.logger.debug("APK Manifest A-XML: \n %s" % str(apk_xml_output.stdout))

        # Parse A-XML output
        lines_list = str(apk_xml_output.stdout).split("\n")
        self.logger.debug("A-XML # Lines: %s" % str(len(lines_list)))

        AXML_elements = []
        last_parent_element = None
        prev_lead_space = 0
        prev_lead_space_idx = 0
        for idx, line in enumerate(lines_list):
            # Count number of spaces prefixing each line
            spacenum = len(line) - len(line.lstrip(' '))
            self.logger.debug('Current Line LEADSPACE: %s' % str(spacenum))
            AXML_Item = self.determine_AXML_Item_type(line, spacenum)
            #self.logger.debug("AXML ITEM TYPE: %s" % str(AXML_Item['type']))
            if AXML_Item['type'] == 'N:':
                last_parent_element = AXML_Item
                self.logger.debug("Got FIRST item: %s" % str(AXML_Item['name']))
            elif AXML_Item['type'] in ('E:', 'A:') :
                self.logger.debug("Got item: %s : Type: %s" % (str(AXML_Item['name']), str(AXML_Item['type'])))
                self.logger.debug("Current Item Lead Space: [%s] :: Last PARENT (%s) Lead space: [%s]" %
                                  (str(AXML_Item['leadspace']), str(last_parent_element['name']), str(last_parent_element['leadspace'])))
                #if AXML_Item['type'] == 'E:' and (AXML_Item['leadspace'] > last_parent_element['leadspace']):
                if (AXML_Item['leadspace'] > last_parent_element['leadspace']):
                    #if AXML_Item['type'] in ('E:', 'N:'):
                    if last_parent_element['type'] in ('E:', 'N:'):
                        last_parent_element['child_items'].append(AXML_Item)
                        self.logger.debug("APPENDED: CHILD [%s] to PARENT [%s]" % (AXML_Item['name'], last_parent_element['name']))
                        # Change focus of last_parent to the current element in case it has children following
                        last_parent_element = AXML_Item
                        AXML_elements.append(last_parent_element)
                    #elif AXML_Item['type'] == 'A:':
                    #    last_parent_element['child_items'].append(AXML_Item)
                elif AXML_Item['leadspace'] == last_parent_element['leadspace']:
                    AXML_elements.append(AXML_Item)
                    #last_parent_element['child_items'].append(AXML_Item)

                # if AXML_Item['leadspace'] > prev_lead_space:
                #     # Child "element" or "attribute"
                #     if len(AXML_elements) == 0:
                #         AXML_elements.append(AXML_Item)
                #         prev_lead_space = AXML_Item['leadspace']
                #         #prev_lead_space_idx =
                #     elif len(AXML_elements) > 0:
                #     AXML_elements.insert()
                # else:

                #AXML_elements.append(AXML_Item)

                # curr_parent =  None
                # if line.lstrip().startswith("E:"):
                #     element_item['leadspace'] = spacenum
                #     element_item['type'] = line.lstrip().split(' ')[0]
                #     if curr_parent == None:
                #         element_item['curr_parent'] = element_item
                #     else:
                #         element_item['curr_parent'] = curr_parent
                #
                #     elements.append(element_item)
                #     #for idx, single_element in enumerate(elements):
                #     if (element_item['leadspace'] - elements[()]['leadspace'] == 2):
                #         if line.lstrip().startswith("E:"):
                #             element_item['attribute'] = (line.lstrip().split('=')[0], line.lstrip().split('=')[0])
                #         elif line.lstrip().startswith("A:"):
                #             element_item['child_element'] = line.lstrip().split(' ')[0]

        self.logger.debug("Element Count: %i" % len(AXML_elements))


        return

    def determine_AXML_Item_type(self, line, lead_space_num):
        AXML_item = dict()
        if line.lstrip().startswith("E:"):
            AXML_item['type'] = 'E:'
            AXML_item['leadspace'] = lead_space_num
            AXML_item['name'] = line.lstrip().split(' ')[1]
            AXML_item['AXML_line_num'] = line.lstrip().split('(')[1]
            AXML_item['child_items'] = []
        elif line.lstrip().startswith("A:"):
            AXML_item['type'] = 'A:'
            AXML_item['leadspace'] = lead_space_num
            AXML_item['name'] = line.lstrip().split('=')[0]
            AXML_item['attr_value'] = line.lstrip().split('=')[1]
        elif line.lstrip().startswith("N:"):
            AXML_item['type'] = 'N:'
            AXML_item['leadspace'] = lead_space_num
            AXML_item['name'] = line.lstrip().split('=')[0]
            AXML_item['schema_url'] = line.lstrip().split('=')[1]
            AXML_item['child_items'] = []
        else:
            AXML_item['type'] = 'Unknown'
        return AXML_item

    def parse_manifest_using_ClassyShark(self):
        # www.classyshark.com
        return

adb_proc = PyAdb()
#adb_proc.adb_start()
#adb_proc.adb_list_devices()
#adb_proc.adb_get_packages_installed()

adb_proc.aapt_get_activity_list('app-debug.apk')
#adb_proc.aapt_get_activity_list('eu.chainfire.supersu_2.79-279_minAPI7(nodpi)_apkmirror.com.apk')

#adb_proc.use_AXML_Printer('app-debug')
adb_proc.use_AXML_Printer('eu.chainfire.supersu_2.79-279_minAPI7(nodpi)_apkmirror.com')




