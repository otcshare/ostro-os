"""
@file comm_bt_command.py
"""

##
# @addtogroup bluetooth bluetooth
# @brief This is bluetooth component
# @{
# @addtogroup comm_bt_command comm_bt_command
# @brief This is comm_bt_command module
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

@tag(TestType="FVT")
class CommBTTest(oeRuntimeTest):
    """
    @class CommBTTest
    """
    def setUp(self):
        """
        @fn setUp
        @param self
        @return
        """
        self.bt = bluetooth.BTFunction(self.target)
        self.bt.target_hciconfig_init()

    @tag(FeatureID="IOTOS-453")
    def test_bt_power_on(self):
        '''enable bluetooth device
        @fn test_bt_power_on
        @param self
        @return
        '''
        self.target.run('hciconfig hci0 down')
        self.bt.ctl_power_on()

    @tag(FeatureID="IOTOS-453")
    def test_bt_power_off(self):
        '''disable bluetooth device
        @fn test_bt_power_off
        @param self
        @return
        '''
        self.target.run('hciconfig hci0 up')
        self.bt.ctl_power_off()

    @tag(FeatureID="IOTOS-453")
    def test_bt_visable_on(self):
        '''enable visibility
        @fn test_bt_visable_on
        @param self
        @return
        '''
        self.target.run('hciconfig hci0 noscan')
        self.bt.ctl_visable_on()

    @tag(FeatureID="IOTOS-453")
    def test_bt_visable_off(self):
        '''disable visibility
        @fn test_bt_visable_off
        @param self
        @return
        '''
        self.target.run('hciconfig hci0 piscan')
        self.bt.ctl_visable_off()

    @tag(TestType="EFT", FeatureID="IOTOS-453")
    def test_bt_change_name(self):
        '''change BT device name
        @fn test_bt_change_name
        @param self
        @return
        '''
        new_name="iot-bt-test"
        self.target.run('hciconfig hci0 name %s' % new_name)
        name = self.bt.get_name()
        if name == new_name:
            pass
        else:
           self.assertEqual(1, 0, msg="Bluetooth set name fails. Current name is: %s" % name)

##
# @}
# @}
##

