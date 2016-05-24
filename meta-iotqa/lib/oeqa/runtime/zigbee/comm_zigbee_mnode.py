"""
@file comm_zigbee_mnode.py
"""

##
# @addtogroup zigbee
# @brief This is component
# @{
# @addtogroup comm_zigbee
# @brief This is comm_zigbee module
# @{
##

import time
import os
import string
import zigbee
from oeqa.oetest import oeRuntimeTest
from oeqa.utils.helper import shell_cmd_timeout
from oeqa.utils.helper import run_as
from oeqa.utils.decorators import tag

@tag(TestType="EFT")
class ZigBeeMNode(oeRuntimeTest):
    """
    @class ZigBeeMNode
    """
    def setUp(self):
        ''' initialize zigbee case
        @fn setUp
        @param self
        @return
        '''
        self.zigbee1 = zigbee.ZigBeeFunction(self.targets[0])
        self.zigbee1.clean_up()
        self.zigbee1.remove_cc2520_mode()        
        self.zigbee2 = zigbee.ZigBeeFunction(self.targets[1])
        self.zigbee2.clean_up()
        self.zigbee2.remove_cc2520_mode()        

    def tearDown(self):
        ''' tearDown zigbee case
        @fn tearDown
        @param self
        @return
        '''
        self.zigbee1.clean_up()
        self.zigbee2.clean_up()
        self.zigbee1.remove_atmel_mode()
        self.zigbee2.remove_atmel_mode()

    @tag(FeatureID="IOTOS-1220")
    def test_zigbee_atmel_ping6_out(self):
        '''Setup two devices with atmel, and ping each other
        @fn test_zigbee_atmel_ping6_out
        @param self
        @return
        '''
        self.zigbee1.atmel_enable_lowpan0(1)
        self.zigbee2.atmel_enable_lowpan0(2)
        # first device to ping second device
        self.zigbee1.lowpan0_ping6_check(self.zigbee2.get_lowpan0_ip())

    @tag(FeatureID="IOTOS-1220")
    def test_zigbee_atmel_be_pinged(self):
        '''Setup two devices with atmel, and ping each other
        @fn test_zigbee_atmel_be_pinged
        @param self
        @return
        '''
        self.zigbee1.atmel_enable_lowpan0(1)
        self.zigbee2.atmel_enable_lowpan0(2)
        # first device to ping second device
        self.zigbee2.lowpan0_ping6_check(self.zigbee1.get_lowpan0_ip())

    @tag(FeatureID="IOTOS-1220")
    def test_zigbee_atmel_izchat_receive(self):
        '''Setup two devices with atmel, and use izchat to communicate 
           with each other
        @fn test_zigbee_atmel_izchat_receive
        @param self
        @return
        '''
        self.zigbee1.atmel_enable_lowpan0(1)
        self.zigbee2.atmel_enable_lowpan0(2)
        # first device to izchat with second device
        self.zigbee1.lowpan0_izchat_check(self.targets[1].ip)

    @tag(FeatureID="IOTOS-1220")
    def test_zigbee_atmel_izchat_send(self):
        '''Setup two devices with atmel, and use izchat to communicate 
           with each other
        @fn test_zigbee_atmel_izchat_send
        @param self
        @return
        '''
        self.zigbee1.atmel_enable_lowpan0(1)
        self.zigbee2.atmel_enable_lowpan0(2)
        # Second device to izchat with first device
        self.zigbee2.lowpan0_izchat_check(self.targets[0].ip)

##
# @}
# @}
##

