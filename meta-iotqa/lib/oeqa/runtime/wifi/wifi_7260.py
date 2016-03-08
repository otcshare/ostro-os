"""
@file wifi.py
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
import string
from oeqa.utils.helper import shell_cmd_timeout

class WiFiFunction(object):
    """
    @class WiFiFunction
    """
    service = ""
    log = ""
    def __init__(self, target):
        self.target = target

    def target_collect_info(self, cmd):
        """
        @fn target_collect_info
        @param self
        @param  cmd
        @return
        """
        (status, output) = self.target.run(cmd)
        self.log = self.log + "\n\n[Debug] Command output --- %s: \n" % cmd
        self.log = self.log + output

    def enable_wifi(self):
        """
        @fn enable_wifi
        @param self
        @return
        """
        # un-block software rfkill lock
        self.target.run('rfkill unblock all')
        # Enable WiFi
        self.target.run('connmanctl disable wifi')
        time.sleep(2)
        (status, output) = self.target.run('connmanctl enable wifi')
        assert status == 0, "Error messages: %s" % output 
        # Use sleep because wifi_enable will trigger auto-connect (to last AP)
        time.sleep(30)

    def disable_wifi(self):
        ''' disable wifi after testing 
        @fn disable_wifi
        @param self
        @return
        '''
        (status, output) = self.target.run('connmanctl disable wifi')
        assert status == 0, "Error messages: %s" % output 
        # sleep some seconds to ensure disable is done
        time.sleep(5)

    def scan_wifi(self, ap_type, ssid):
        """
        @fn scan_wifi
        @param self
        @param ap_type: hidden or broadcast
        @return service string of AP
        """
        if (ap_type == "hidden"):
            ssid = "hidden_managed_psk"

        # Retry 4 times scan if needed
        retry = 0
        while (retry < 4):
            self.target.run('connmanctl disable wifi')
            time.sleep(1)
            self.target.run('connmanctl enable wifi')
            time.sleep(1)
            (status, output) = self.target.run('connmanctl scan wifi')
            assert status == 0, "Error messages: %s" % output 
            (status, output) = self.target.run("connmanctl services | grep %s" % ssid)
            retry = retry + 1
            if (status == 0):
                break
            else:
                self.target_collect_info("connmanctl services")
        # Collect info
        self.target_collect_info("ifconfig")
        assert status == 0, "Not found hidden AP service" + self.log

        if (ap_type == "hidden"):
            return output.strip()
        elif (ap_type == "broadcast"):
            return output.split(" ")[-1]

    def connect_wifi(self, ap_type, ssid, pwd):
        '''connmanctl to connect wifi AP
        @fn connect_wifi
        @param self
        @return
        '''
        target_ip = self.target.ip 
        service = self.scan_wifi(ap_type, ssid)
        # Do connection
        if (ap_type == "broadcast"):
            exp = os.path.join(os.path.dirname(__file__), "files/wifi_connect_7260.exp")
            cmd = "expect %s %s %s %s %s" % (exp, target_ip, "connmanctl", service, pwd)
        elif (ap_type == "hidden"):
            exp = os.path.join(os.path.dirname(__file__), "files/wifi_hidden_connect_7260.exp")
            cmd = "expect %s %s %s %s %s %s" % (exp, target_ip, "connmanctl", service, ssid, pwd)
        else:
            assert False, "ap_type must be broadcast or hidd n, check config"
        # execute connection expect script
        status, output = shell_cmd_timeout(cmd, timeout=60)
        assert status == 2, "Error messages: %s" % output 

    def wifi_ip_check(self):
        '''check if the target gets ip address
        @fn wifi_ip_check
        @param self
        @return
        '''
        time.sleep(3)
        # Check ip address by ifconfig command
        wifi_interface = "nothing"
        (status, wifi_interface) = self.target.run("ifconfig | grep '^wlp\|^wlan' | awk '{print $1}'")
        (status, output) = self.target.run("ifconfig %s | grep 'inet addr:'" % wifi_interface)
        assert status == 0, "Error messages: %s" % output 
        # Collect info
        self.target_collect_info("ifconfig")

        assert status == 0, "IP check failed" + self.log

    def check_internet_connection(self):
        # wget internet content
        self.target.run("rm -f index.html")
        time.sleep(1)
        (status, output) = self.target.run("wget http://www.baidu.com/")
        self.target_collect_info("route")
        assert status == 0, "Error messages: %s" % self.log

    def execute_connection(self, ap_type, ssid, pwd):
        '''do a full round of wifi connection without disable
        @fn execut_connection
        @param self
        @param ap_type: must be broadcast or hidden
        @param ssid
        @param pwd
        @return
        '''
        self.enable_wifi()
        self.connect_wifi(ap_type, ssid, pwd)
        self.wifi_ip_check()                

##
# @}
# @}
##

