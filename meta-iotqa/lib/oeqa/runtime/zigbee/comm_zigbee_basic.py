"""
@file comm_zigbee_basic.py
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
from oeqa.utils.decorators import tag

@tag(TestType="FVT")
class ZigBeeBasic(oeRuntimeTest):
    """
    @class ZigBeeBasic
    """
    def setUp(self):
        ''' initialize zigbee class 
        @fn setUp
        @param self
        @return
        '''
        self.zigbee = zigbee.ZigBeeFunction(self.target)

    def tearDown(self):
        ''' initialize zigbee class
        @fn setUp
        @param self
        @return
        '''
        self.zigbee.remove_atmel_mode()

    @tag(FeatureID="IOTOS-1220")
    def test_insert_atmel_module(self):
        '''Insert atmel module to enable 802.15.4
        @fn test_insert_atmel_module
        @param self
        @return
        '''
        self.zigbee.remove_cc2520_mode()
        self.zigbee.insert_atmel_mode()

##
# @}
# @}
##

