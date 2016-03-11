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
        wifi = wifi.WiFiFunction(cls.tc.target)

        ap_type = ssid_config.get("Connect","type")
        ssid = ssid_config.get("Connect","ssid")
        pwd = ssid_config.get("Connect","passwd")

        wifi.execute_connection(ap_type, ssid, pwd)
        
        # Clean up all iotivity related daemons
        cls.tc.target.run("killall presenceserver presenceclient devicediscoveryserver devicediscoveryclient")        
        cls.tc.target.run("killall fridgeserver fridgeclient garageserver garageclient groupserver groupclient")
        cls.tc.target.run("killall roomserver roomclient simpleserver simpleclient simpleserverHQ simpleclientHQ")
        cls.tc.target.run("killall simpleclientserver threadingsample")
        # Do simpleclient test
        client_cmd = "/opt/iotivity/examples/resource/cpp/simpleclient > /tmp/output &"
        cls.tc.target.run(client_cmd)
        print "\npatient... simpleclient needs long time for its observation"
        time.sleep(70)

    @classmethod
    def tearDownClass(cls):
        '''disable wifi, it will block ethernet connection when rebooting
        @fn tearDownClass
        @param cls
        @return
        '''
        wifi = wifi.WiFiFunction(cls.tc.target)
        wifi.disable_wifi()

    def test_iotvt_wifi_findresource(self):
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

    def test_iotvt_wifi_getstate(self):
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

    def test_iotvt_wifi_observer(self):
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

    def test_iotvt_wifi_setstate(self):
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

