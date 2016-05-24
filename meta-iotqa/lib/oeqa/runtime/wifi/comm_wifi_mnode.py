"""
@file comm_wifi_mnode.py
"""

##
# @addtogroup wifi
# @brief This is component
# @{
# @addtogroup comm_wifi_mnode
# @brief This is comm_wifi module
# @{
##

import time
import os
import string
import wifi
import ConfigParser
from oeqa.oetest import oeRuntimeTest
from oeqa.utils.helper import shell_cmd_timeout
from oeqa.utils.decorators import tag

ssid_config = ConfigParser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "files/config.ini")
ssid_config.readfp(open(config_path))

@tag(TestType="EFT")
class CommWiFiMNode(oeRuntimeTest):
    """
    @class CommWiFiMNode
    """
    @classmethod
    def setUpClass(cls):
        ''' initialize wifi class 
        @fn setUp
        @param self
        @return
        '''
        wifi1 = wifi.WiFiFunction(cls.tc.targets[0])
        wifi2 = wifi.WiFiFunction(cls.tc.targets[1])

        # Connect to same WiFi AP
        ap_type = "hidden"
        ssid = ssid_config.get("Connect","ssid_80211n")
        pwd = ssid_config.get("Connect","passwd_80211n")
        wifi1.execute_connection(ap_type, ssid, pwd)
        wifi2.execute_connection(ap_type, ssid, pwd)

    @classmethod
    def tearDownClass(cls):
        '''disable wifi, it will block ethernet connection when rebooting
        @fn tearDownClass
        @param cls
        @return
        '''
        wifi1 = wifi.WiFiFunction(cls.tc.targets[0])
        wifi2 = wifi.WiFiFunction(cls.tc.targets[1])
        wifi1.disable_wifi()
        wifi2.disable_wifi()

    def setUp(self):
        ''' init wifi1 and wifi2 
        @fn setUp
        @param self
        @return
        '''
        # init wifi1 and wifi2
        self.wifi1 = wifi.WiFiFunction(self.targets[0])
        self.wifi2 = wifi.WiFiFunction(self.targets[1])

    @tag(FeatureID="IOTOS-457")
    def test_wifi_ssh(self):
        '''One device ssh to another via WiFi
        @fn test_wifi_ssh
        @param self
        @return
        '''
        # Check wifi1 to ssh to wifi2
        self.wifi1.ipv4_ssh_to(self.wifi2.get_wifi_ipv4())

    @tag(FeatureID="IOTOS-457")
    def test_wifi_scp_file(self):
        '''One device scp a file to another device via WiFi
        @fn test_wifi_scp_file
        @param self
        @return
        '''
        # Check wifi1 to scp /etc/os-release to wifi2
        self.wifi1.ipv4_ssh_to(self.wifi2.get_wifi_ipv4())
        file_path = "/etc/os-release"
        self.wifi1.scp_to(file_path, self.wifi2.get_wifi_ipv4())
        # Compare md5sum
        (status, md5sum1) = self.wifi1.target.run('md5sume %s' % file_path)
        (status, md5sum2) = self.wifi2.target.run('md5sume /tmp/%s' % file_path.split('/')[-1])
        if md5sum1 == md5sum2:
            pass
        else:
            self.assertEqual(0, 1, msg="md5sum checking fail: original %s, remote is %s" % (md5sum1, md5sum2))

    @tag(FeatureID="IOTOS-458")
    def test_wifi_scp_multiple_files(self):
        '''Stability: one device scp thousands of small files 
           to another
        @fn test_wifi_scp_multiple_files
        @param self
        @return
        '''
        # clean files on both sides
        self.wifi2.target.run('rm -f /home/root/*')
        self.wifi1.ipv4_ssh_to(self.wifi2.get_wifi_ipv4())
        # create 1000 files under /tmp/1000/ on target1
        script = os.path.join(os.path.dirname(__file__), "files/create_1000_files.sh")
        self.wifi1.target.copy_to(script, "/tmp/")
        self.wifi1.target.run('sh /tmp/create_1000_files.sh')

        # scp them to target2 /tmp/ folder
        (status, file_number_old) = self.wifi2.target.run('ls /home/root/ | wc -l')
        file_path = '/tmp/1000/*'
        self.wifi1.scp_to(file_path, self.wifi2.get_wifi_ipv4())

        # check if /tmp/ files number increase 1000 on target2
        (status, file_number_new) = self.wifi2.target.run('ls /home/root/ | wc -l')
        if int(file_number_new) - int(file_number_old) == 1000:
            pass
        else:
            self.assertEqual(0, 1, msg="1000 file scp fail: original number %s, new number %s" % (file_number_old, file_number_new))

    @tag(FeatureID="IOTOS-458")
    def test_wifi_scp_big_file(self):
        '''Stability: one device scp 500M size file to another 
        @fn test_wifi_scp_big_file
        @param self
        @return
        '''
        self.wifi1.ipv4_ssh_to(self.wifi2.get_wifi_ipv4())
        file_path = '/home/root/big_file'
        # create a big file, size is 500M
        (status, patition) = self.wifi1.target.run('mount | grep " \/ "')
        self.wifi1.target.run('dd if=%s of=%s bs=1M count=500' % (patition.split()[0], file_path))

        # scp it to target2 /home/root/ folder
        self.wifi2.target.run('rm -f /home/root/*')
        self.wifi1.scp_to(file_path, self.wifi2.get_wifi_ipv4())

        # check if md5sume is consistent
        (status, md5sum1) = self.wifi1.target.run('md5sum %s' % file_path)
        (status, md5sum2) = self.wifi2.target.run('md5sum /home/root/%s' % file_path.split('/')[-1])
        if md5sum1.split()[0] == md5sum2.split()[0]:
            pass
        else:
            self.assertEqual(0, 1, msg="md5sum checking fail: original %s, remote is %s" % (md5sum1.split()[0], md5sum2.split()[0]))

    @tag(FeatureID="IOTOS-458")
    def test_wifi_avaliable_after_longtime_idle(self):
        '''Stability: check if wifi is still workable after a long time idle
        @fn test_wifi_avaliable_after_longtime_idle
        @param self
        @return
        '''
        # Re-connect wifi although setUpClass already did it
        ap_type = "hidden"
        ssid = ssid_config.get("Connect","ssid_80211n")
        pwd = ssid_config.get("Connect","passwd_80211n")
        self.wifi1.execute_connection(ap_type, ssid, pwd)
        self.wifi2.execute_connection(ap_type, ssid, pwd)

        # idle for half hour, then check basic ssh_to function
        time.sleep(1800)
        self.wifi1.ipv4_ssh_to(self.wifi2.get_wifi_ipv4())

##
# @}
# @}
##

