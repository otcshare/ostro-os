"""
@file comm_zigbee_cc2520.py
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
class ZigBeeCC2520(oeRuntimeTest):
    """
    @class ZigBeeCC2520
    """
    def setUp(self):
        ''' initialize zigbee class 
        @fn setUp
        @param self
        @return
        '''
        self.zigbee = zigbee.ZigBeeFunction(self.target)

    def tearDown(self):
        ''' teardown cc2520 class 
        @fn setUp
        @param self
        @return
        '''
        self.zigbee.remove_cc2520_mode()

    @tag(FeatureID="IOTOS-763")
    def test_insert_cc2520_module(self):
        '''Insert cc2520 module
        @fn test_insert_cc2520_module
        @param self
        @return
        '''
        self.zigbee.remove_atmel_mode()
        self.zigbee.insert_cc2520_mode()

##
# @}
# @}
##

