"""
@file comm_bt_6lowpan.py
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
from oeqa.runtime.bluetooth import bluetooth
from oeqa.oetest import oeRuntimeTest
from oeqa.utils.helper import shell_cmd_timeout
from oeqa.utils.decorators import tag

@tag(TestType="FVT")
class CommBT6LowPAN(oeRuntimeTest):
    """
    @class CommBT6LowPAN
    """
    def setUp(self):
        """
        @fn setUp
        @param self
        @return
        """
        self.bt = bluetooth.BTFunction(self.target)
        self.bt.target_hciconfig_init()

    @tag(FeatureID="IOTOS-762")
    def test_bt_insert_6lowpan_module(self):
        '''Insert 6lowpan module
        @fn test_bt_insert_6lowpan_module
        @param self
        @return
        '''
        self.bt.insert_6lowpan_module()

    @tag(FeatureID="IOTOS-762")
    def test_bt_enable_6lowpan_ble(self):
        '''Enable 6lowpan over BLE
        @fn test_bt_enable_6lowpan_ble
        @param self
        @return
        '''
        self.bt.enable_6lowpan_ble()

##
# @}
# @}
##

