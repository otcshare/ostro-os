"""
@file comm_connect.py
"""

##
# @addtogroup wifi
# @brief This is component
# @{
# @addtogroup comm_connect comm_connect
# @brief This is comm_connect module
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
        self.wifi = wifi.WiFiFunction(self.target)

    def tearDown(self):
        ''' disable after testing 
        @fn tearDown
        @param self
        @return
        '''
        # disable wifi
        self.wifi.disable_wifi()

    @tag(FeatureID="IOTOS-457")
    def test_connect_80211b(self):
        '''connmanctl to connect 802.11b AP
        @fn test_connect_80211b
        @param self
        @return
        '''
        ap_type = "hidden"
        ssid = ssid_config.get("Connect","ssid_80211b")
        pwd = ssid_config.get("Connect","passwd_80211b")

        self.wifi.execute_connection(ap_type, ssid, pwd)

    @tag(FeatureID="IOTOS-457")
    def test_connect_80211g(self):
        '''connmanctl to connect 802.11g AP
        @fn test_connect_80211g
        @param self
        @return
        '''
        ap_type = "hidden"
        ssid = ssid_config.get("Connect","ssid_80211g")
        pwd = ssid_config.get("Connect","passwd_80211g")

        self.wifi.execute_connection(ap_type, ssid, pwd)

    @tag(FeatureID="IOTOS-457")
    def test_connect_80211n(self):
        '''connmanctl to connect 802.11n AP
        @fn test_connect_80211n
        @param self
        @return
        '''
        ap_type = "hidden"
        ssid = ssid_config.get("Connect","ssid_80211n")
        pwd = ssid_config.get("Connect","passwd_80211n")

        self.wifi.execute_connection(ap_type, ssid, pwd)

    @tag(FeatureID="IOTOS-458")
    def test_connect_wpapsk(self):
        '''connmanctl to connect WPA-PSK AP (set by ssid_80211b AP)
        @fn test_connect_wpapsk
        @param self
        @return
        '''
        ap_type = "hidden"
        ssid = ssid_config.get("Connect","ssid_80211b")
        pwd = ssid_config.get("Connect","passwd_80211b")

        self.wifi.execute_connection(ap_type, ssid, pwd)

    @tag(FeatureID="IOTOS-458")
    def test_connect_wpa2psk(self):
        '''connmanctl to connect WPA2-PSK AP (set by ssid_80211g AP)
        @fn test_connect_wpa2psk
        @param self
        @return
        '''
        ap_type = "hidden"
        ssid = ssid_config.get("Connect","ssid_80211g")
        pwd = ssid_config.get("Connect","passwd_80211g")

        self.wifi.execute_connection(ap_type, ssid, pwd)

    @tag(FeatureID="IOTOS-490")
    def test_connect_wpa2psk_broadcast(self):
        '''connmanctl to connect WPA2-PSK AP (not hidden)
        @fn test_connect_wpa2psk_broadcast
        @param self
        @return
        '''
        ap_type = "broadcast"
        ssid = ssid_config.get("Connect","ssid_broadcast")
        pwd = ssid_config.get("Connect","passwd_broadcast")

        self.wifi.execute_connection(ap_type, ssid, pwd)

    @tag(FeatureID="IOTOS-528")
    def test_connect_internet(self):
        '''connmanctl to connect to internet, by broadcast AP
        @fn test_connect_internet
        @param self
        @return
        '''
        ap_type = "broadcast"
        ssid = ssid_config.get("Connect","ssid_broadcast")
        pwd = ssid_config.get("Connect","passwd_broadcast")
        url = ssid_config.get("Internet","url")

        self.wifi.execute_connection(ap_type, ssid, pwd)
        self.wifi.check_internet_connection(url)

    @tag(FeatureID="IOTOS-458")
    def test_connect_wep(self):
        '''connmanctl to connect to WEP encryption AP
        @fn test_connect_wep
        @param self
        @return
        '''
        ap_type = "hidden-wep"
        ssid = ssid_config.get("Connect","ssid_wep")
        pwd = ssid_config.get("Connect","passwd_wep")

        self.wifi.execute_connection(ap_type, ssid, pwd)

    @tag(FeatureID="IOTOS-458")
    def test_connect_80211ac(self):
        '''connmanctl to connect to 802.11ac AP
        @fn test_connect_80211ac
        @param self
        @return
        '''
        ap_type = "hidden"
        ssid = ssid_config.get("Connect","ssid_80211ac")
        pwd = ssid_config.get("Connect","passwd_80211ac")

        self.wifi.execute_connection(ap_type, ssid, pwd)

    @tag(FeatureID="IOTOS-458")
    def test_connect_save_password(self):
        '''When connecting to an AP connected before, do not need input password
        @fn test_connect_save_password
        @param self
        @return
        '''
        # Connect to 80211n AP firstly
        ap_type = "hidden"
        ssid_n = ssid_config.get("Connect","ssid_80211n")
        pwd_n = ssid_config.get("Connect","passwd_80211n")

        self.wifi.execute_connection(ap_type, ssid_n, pwd_n)
        # Connect to 80211g AP
        ssid_g = ssid_config.get("Connect","ssid_80211g")
        pwd_g = ssid_config.get("Connect","passwd_80211g")
        self.wifi.execute_connection(ap_type, ssid_g, pwd_g)

        # Then, connect back to 80211n, without inputting password
        self.wifi.connect_without_password(ssid_n)
        

##
# @}
# @}
##

