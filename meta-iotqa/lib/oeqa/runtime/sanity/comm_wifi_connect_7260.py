"""
@file comm_wifi_connect.py
"""

##
# @addtogroup sanity sanity
# @brief This is sanity component
# @{
# @addtogroup comm_wifi_connect comm_wifi_connect
# @brief This is comm_wifi_connect module
# @{
##

import time
import os
from oeqa.runtime.wifi import wifi_7260
import string
import ConfigParser
from oeqa.oetest import oeRuntimeTest
from oeqa.utils.helper import shell_cmd_timeout
from oeqa.utils.decorators import tag

ssid_config = ConfigParser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "files/config.ini")
ssid_config.readfp(open(config_path))

@tag(TestType="FVT")
class CommWiFiConect(oeRuntimeTest):
    """
    @class CommWiFiConect
    """
    def setUp(self):
        ''' initialize wifi class
        @fn setUp
        @param self
        @return
        '''
        self.wifi = wifi_7260.WiFiFunction(self.target)

    def tearDown(self):
        ''' disable after testing
        @fn tearDown
        @param self
        @return
        '''
        # disable wifi
        self.wifi.disable_wifi()

    @tag(FeatureID="IOTOS-458")
    def test_wifi_connect(self):
        '''connmanctl to connect WPA2-PSK wifi AP
        @fn test_wifi_connect
        @param self
        @return
        '''
        ap_type = ssid_config.get("Connect","type") 
        ssid = ssid_config.get("Connect","ssid")
        pwd = ssid_config.get("Connect","passwd")

        self.wifi.execute_connection(ap_type, ssid, pwd)

##
# @}
# @}
##

