#[PROTEXCAT]
#\License: ALL RIGHTS RESERVED
#\Author: Wang, Jing <jing.j.wang@intel.com>

'''base os test module
@file baseos.py
'''

##
# @addtogroup sanity sanity
# @brief This is sanity component
# @{
# @addtogroup baseos baseos
# @brief This is baseos module
# @{
##

from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag
import re

@tag(TestType="FVT", FeatureID="IOTOS-638")
class BaseOsTest(oeRuntimeTest):
    '''Base os health check
    @class BaseOsTest
    '''
    def test_baseos_dmesg(self):
        '''check dmesg command
        @fn test_baseos_dmesg
        @param self
        @return
        '''
        (status, output) = self.target.run('dmesg')
        ##
        # TESTPOINT: #1, test_baseos_dmesg
        #
        self.assertEqual(status, 0, msg="Error messages: %s" % output)

    def test_baseos_lsmod(self):
        '''check lsmod command
        @fn test_baseos_lsmod
        @param self
        @return
        '''
        (status, output) = self.target.run('lsmod')
        ##
        # TESTPOINT: #1, test_baseos_lsmod
        #
        # lsmod should show at least 1 module
        if output.count('\n') > 0:
            pass
        else:
            status=1
        self.assertEqual(status, 0, msg="Error messages: %s" % output)

    def test_baseos_ps(self):
        '''check ps command
        @fn test_baseos_ps
        @param self
        @return
        '''
        (status, output) = self.target.run('ps')
        ##
        # TESTPOINT: #1, test_baseos_ps
        #
        # ps should show at least 1 process
        if output.count('\n') > 0:
            pass
        else:
            status=1
        self.assertEqual(status, 0, msg="Error messages: %s" % output)

    def test_baseos_df(self):
        '''check df command
        @fn test_baseos_df
        @param self
        @return
        '''
        (status, output) = self.target.run('df')
        ##
        # TESTPOINT: #1, test_baseos_df
        #
        # df should show at least 1 mounting point
        if output.count('\n') > 0:
            pass
        else:
            status=1
        self.assertEqual(status, 0, msg="Error messages: %s" % output)

    def test_baseos_systemd_process(self):
        '''check systemd process
        @fn test_baseos_systemd_process
        @param self
        @return
        '''
        (status, output) = self.target.run("ls -l /proc/1/exe")
        ##
        # TESTPOINT: #1, test_baseos_systemd_process
        #
        if output.endswith("systemd"):
            pass
        else:
            status=1
        self.assertEqual(status, 0, msg="Error messages: %s" % output)

    def test_baseos_systemd_boot_error(self):
        ''' check systemd boot journal error''' 
        known_issues_list = [
            "GPT: Use GNU Parted to correct GPT errors",
            # IOTOS-1575 [Edison] wpa_supplicant error during system booting
            "Failed to open config file '/etc/wpa_supplicant/wpa_supplicant-wlan0.conf'",
            # ignore kernel errors
            "^\w{3,} \d{,2} \d{2}:\d{2}:\d{2} \S+ kernel:",
            # IOTOS-1691 Ethernet relevant errors at system startup
            "Error changing net interface name \S+ to \S+: Device or resource busy",
            "open error Permission denied for /var/lib/connman/ethernet_\S+_cable/data",
            ]
        self.longMessage = True
        cmd = "journalctl -ab"
        (status, output) = self.target.run("journalctl -ab")
        self.assertEqual(status, 0, "Fail to run %s,status is %s, output is: %s\n" 
                                              % (cmd,status,output))

        self.assertTrue(output.strip(), "No systemd journal log")
        journal = output
        errors = []
        for line in output.split('\n'):
            if 'error' in line.lower():
                flag = 0
                for issue in known_issues_list:
                    if re.search(issue, line.strip()) :
                        flag = 1
                        break
                if flag == 0 :
                    errors.append(line)

        self.assertEqual(0, len(errors), "Errors in boot log:\n %s, \nFull log:\n %s" 
                                 % ("\n".join(errors), journal))
##
# @}
# @}
##

