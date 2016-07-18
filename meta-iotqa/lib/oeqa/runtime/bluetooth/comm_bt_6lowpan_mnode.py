"""
@file comm_bt_6lowpan_mnode.py
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

@tag(TestType="EFT")
class CommBT6LowPanMNode(oeRuntimeTest):
    """
    @class CommBT6LowPanMNode
    """
    def setUp(self):
        """
        @fn setUp
        @param self
        @return
        """
        self.bt1 = bluetooth.BTFunction(self.targets[0])
        self.bt2 = bluetooth.BTFunction(self.targets[1])
         
        self.bt1.target_hciconfig_init()
        self.bt2.target_hciconfig_init()

    def tearDown(self):
        """
        @fn tearDown
        @param self
        @return
        """
        self.bt1.disable_6lowpan_ble()
        self.bt2.disable_6lowpan_ble()

    @tag(FeatureID="IOTOS-762")
    def test_bt_connect_6lowpan(self):
        '''Setup two devices with BLE
        @fn test_bt_connect_6lowpan
        @param self
        @return
        '''
        self.bt1.connect_6lowpan_ble(self.bt2)

    @tag(FeatureID="IOTOS-762")
    def test_bt_6lowpan_ping6_out(self):
        '''Setup two devices with BLE, and ping each other
        @fn test_bt_6lowpan_ping6_out
        @param self
        @return
        '''
        self.bt1.connect_6lowpan_ble(self.bt2)
        # first device to ping second device
        self.bt1.bt0_ping6_check(self.bt2.get_bt0_ip())

    @tag(FeatureID="IOTOS-762")
    def test_bt_6lowpan_be_pinged(self):
        '''Setup two devices with BLE, and ping each other
        @fn test_bt_6lowpan_be_pinged
        @param self
        @return
        '''
        self.bt1.connect_6lowpan_ble(self.bt2)
        # first device to ping second device
        self.bt2.bt0_ping6_check(self.bt1.get_bt0_ip())

    @tag(FeatureID="IOTOS-762")
    def test_bt_6lowpan_ssh_to(self):
        '''Setup two devices with BLE, and ssh to remote
        @fn test_bt_6lowpan_ssh_to
        @param self
        @return
        '''
        self.bt1.connect_6lowpan_ble(self.bt2)
        # first device to ping second device
        self.bt1.bt0_ssh_check(self.bt2.get_bt0_ip())

    @tag(FeatureID="IOTOS-762")
    def test_bt_6lowpan_be_ssh(self):
        '''Setup two devices with BLE, and remote ssh to self
        @fn test_bt_6lowpan_be_ssh
        @param self
        @return
        '''
        self.bt1.connect_6lowpan_ble(self.bt2)
        # first device to ping second device
        self.bt2.bt0_ssh_check(self.bt1.get_bt0_ip())

##
# @}
# @}
##
