"""
@file iotvt_wifi.py
"""

##
# @addtogroup iotivity iotivity
# @brief This is iotivity component
# @{
# @addtogroup iotvt_wifi iotvt_wifi
# @brief This is iotvt_wifi module
# @{
##

import os
import time
import string
from oeqa.runtime.wifi import wifi
import ConfigParser
from oeqa.oetest import oeRuntimeTest
from oeqa.utils.helper import shell_cmd_timeout
from oeqa.utils.helper import run_as, add_group, add_user, remove_user
from oeqa.utils.decorators import tag

ssid_config = ConfigParser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "../sanity/files/config.ini")
ssid_config.readfp(open(config_path))

@tag(TestType="FVT", FeatureID="IOTOS-499")
class IOtvtWiFi(oeRuntimeTest):
    """
    @class IOtvtWiFi
    """
    @classmethod
    def setUpClass(cls):
        '''Connect to WiFi AP, which contains simpleserver running on it
        @fn setUpClass
        @param cls
        @return
        '''
        client_wifi = wifi.WiFiFunction(cls.tc.targets[0])
        server_wifi = wifi.WiFiFunction(cls.tc.targets[1])

        ap_type = ssid_config.get("Connect","type")
        ssid = ssid_config.get("Connect","ssid")
        pwd = ssid_config.get("Connect","passwd")

        # Connect wifi of two devices
        client_wifi.execute_connection(ap_type, ssid, pwd)
        server_wifi.execute_connection(ap_type, ssid, pwd)
        
        # Init main target
        run_as("root", "killall presenceserver presenceclient devicediscoveryserver devicediscoveryclient", target=cls.tc.targets[0])
        run_as("root", "killall fridgeserver fridgeclient garageserver garageclient groupserver groupclient", target=cls.tc.targets[0])
        run_as("root", "killall roomserver roomclient simpleserver simpleclient simpleserverHQ simpleclientHQ", target=cls.tc.targets[0])
        run_as("root", "killall simpleclientserver threadingsample", target=cls.tc.targets[0])
        # Init second target
        run_as("root", "killall presenceserver presenceclient devicediscoveryserver devicediscoveryclient", target=cls.tc.targets[1])
        run_as("root", "killall fridgeserver fridgeclient garageserver garageclient groupserver groupclient", target=cls.tc.targets[1])
        run_as("root", "killall roomserver roomclient simpleserver simpleclient simpleserverHQ simpleclientHQ", target=cls.tc.targets[1])
        run_as("root", "killall simpleclientserver threadingsample", target=cls.tc.targets[1])
        # Clean output file on two targets, main is client part and second is server part
        run_as("root", "rm -f /tmp/svr_output", target=cls.tc.targets[1])
        run_as("root", "rm -f /tmp/output", target=cls.tc.targets[0])
        # add group and non-root user on both sides
        add_group("tester", target=cls.tc.targets[0])
        add_user("iotivity-tester", "tester", target=cls.tc.targets[0])
        add_group("tester", target=cls.tc.targets[1])
        add_user("iotivity-tester", "tester", target=cls.tc.targets[1])
        # Setup firewall accept for multicast, on both sides
        run_as("root", "/usr/sbin/iptables -w -A INPUT -p udp --dport 5683 -j ACCEPT", target=cls.tc.targets[0])
        run_as("root", "/usr/sbin/iptables -w -A INPUT -p udp --dport 5684 -j ACCEPT", target=cls.tc.targets[0])
        run_as("root", "/usr/sbin/iptables -w -A INPUT -p udp --dport 5683 -j ACCEPT", target=cls.tc.targets[1])
        run_as("root", "/usr/sbin/iptables -w -A INPUT -p udp --dport 5684 -j ACCEPT", target=cls.tc.targets[1])

        # check if image contains iotivity example applications
        (status, output) = run_as("root", "ls /opt/iotivity/examples/resource/", target=cls.tc.targets[0])
        if "cpp" in output:
            pass
        else:
            assert 1 == 0, 'There is no iotivity exmaple app installed in target0'
        (status, output) = run_as("root", "ls /opt/iotivity/examples/resource/", target=cls.tc.targets[1])
        if "cpp" in output:
            pass
        else:
            assert 1 == 0, 'There is no iotivity exmaple app installed in target1'

        for i in range(3):
            # Do simpleclient test
            server_cmd = "/opt/iotivity/examples/resource/cpp/simpleserver > /tmp/srv_output &"
            run_as("iotivity-tester", server_cmd, target=cls.tc.targets[1])
            client_cmd = "/opt/iotivity/examples/resource/cpp/simpleclient > /tmp/output &"
            run_as("iotivity-tester", client_cmd, target=cls.tc.targets[0])
            print "\npatient... simpleclient needs long time for its observation"
            time.sleep(70)
            (status, output) = run_as("iotivity-tester", 'cat /tmp/output', target=cls.tc.targets[0])
            if "Observe is used." in output:
                break 
            # if not pass, will retry. Clean the app
            run_as("root", "killall simpleserver simpleclient", target=cls.tc.targets[0])
            time.sleep(1)
            run_as("root", "killall simpleserver simpleclient", target=cls.tc.targets[1])
            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        '''disable wifi, it will block ethernet connection when rebooting
        @fn tearDownClass
        @param cls
        @return
        '''
        client_wifi = wifi.WiFiFunction(cls.tc.targets[0])
        server_wifi = wifi.WiFiFunction(cls.tc.targets[1])
        client_wifi.disable_wifi()
        server_wifi.disable_wifi()
       
        run_as("root", "killall simpleserver simpleclient", target=cls.tc.targets[0])
        time.sleep(1)
        run_as("root", "killall simpleserver simpleclient", target=cls.tc.targets[1])
        time.sleep(1)

    def test_mnode_iotvt_wifi_findresource(self):
        '''Target finds resource, registered by Host
        @fn test_iotvt_wifi_findresource
        @param self
        @return
        '''
        (status, output) = self.target.run('cat /tmp/output')
        ret = 0
        if "DISCOVERED Resource" in output:
            pass
        else:
           ret = 1
        ##
        # TESTPOINT: #1, test_iotvt_wifi_findresource
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)

    def test_mnode_iotvt_wifi_getstate(self):
        '''Target gets resource state
        @fn test_iotvt_wifi_getstate
        @param self
        @return
        '''
        (status, output) = self.target.run('cat /tmp/output')
        ret = 0
        if "GET request was successful" in output:
            pass
        else:
           ret = 1
        ##
        # TESTPOINT: #1, test_iotvt_wifi_getstate
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)

    def test_mnode_iotvt_wifi_observer(self):
        '''Target sets observer
        @fn test_iotvt_wifi_observer
        @param self
        @return
        '''
        (status, output) = self.target.run('cat /tmp/output')
        ret = 0
        if "Observe is used." in output:
            pass
        else:
           ret = 1
        ##
        # TESTPOINT: #1, test_iotvt_wifi_observer
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)

    def test_mnode_iotvt_wifi_setstate(self):
        '''Target sets resource state
        @fn test_iotvt_wifi_setstate
        @param self
        @return
        '''
        (status, output) = self.target.run('cat /tmp/output')
        ret = 0
        if "PUT request was successful" in output:
            pass
        else:
           ret = 1
        ##
        # TESTPOINT: #1, test_iotvt_wifi_setstate
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)

##
# @}
# @}
##

