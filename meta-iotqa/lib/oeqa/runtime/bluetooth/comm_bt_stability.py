"""
@file comm_bt_stability.py
"""

##
# @addtogroup bluetooth
# @brief This is bluetooth component
# @{
# @addtogroup comm_bt_stability
# @brief This is comm_bt_stability module
# @{
##

import os
import time
import subprocess
from oeqa.runtime.bluetooth import bluetooth
from oeqa.oetest import oeRuntimeTest
from oeqa.utils.helper import shell_cmd_timeout
from oeqa.utils.helper import get_files_dir
from oeqa.utils.decorators import tag

@tag(TestType="EFT")
class BTStabilityTest(oeRuntimeTest):
    """
    @class BTStabilityTest
    """
    def setUp(self):
        ''' initialize bluetooth class 
        @fn setUp
        @param self
        @return
        '''
        self.bt = bluetooth.BTFunction(self.target)

    @tag(FeatureID="IOTOS-453")
    def test_bt_onoff_multiple_time(self):
        '''bluetoothctl to power on/off for multiple times
        @fn test_bt_onoff_multiple_time
        @param self
        @return
        '''
        time=200
        for i in range(1, time):
            self.bt.ctl_power_on()
            self.bt.ctl_power_off()
            if i % 20 == 0:
                print ("Finish %d times, successful." % i)

    @tag(FeatureID="IOTOS-453")
    def test_bt_visable_onoff_multiple_time(self):
        '''bluetoothctl to turn discoverable on/off for multiple times
        @fn test_bt_visable_onoff_multiple_time
        @param self
        @return
        '''
        self.bt.ctl_power_on()
        time=200
        for i in range(1, time):
            self.bt.ctl_visable_on()
            self.bt.ctl_visable_off()
            if i % 20 == 0:
                print ("Finish %d times, successful." % i)

##
# @}
# @}
##

