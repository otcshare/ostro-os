"""
@file zigbee.py
"""

##
# @addtogroup zigbee
# @brief This is zigbee component
# @{
# @addtogroup comm_zigbee
# @brief This is comm_zigbee module
# @{
##

import time
import os
import string
import subprocess
from oeqa.utils.helper import shell_cmd_timeout

class ZigBeeFunction(object):
    """
    @class ZigBeeFunction
    """
    platform = ""
    atmel_mod_name = ""
    cc2520_mod_name = ""
    log = ""
    def __init__(self, target):
        self.target = target
        self.init_platform()

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

    def init_platform(self):
        '''based on uname -a, check which platform and its module name'''
        """
        @fn 
        @param self
        @return
        """
        (status, output) = self.target.run('uname -a')
        if "intel-quark" in output:
            self.platform="Galileo"
            self.atmel_mod_name="spi-quark-board"
        elif "intel-corei7-64" in output:
            # Here assume case is not played on GB-BXBT, for uname arch are same
            self.platform="MinnowMax"
            self.atmel_mod_name="spi-minnow-board"
            self.cc2520_mod_name="spi-minnow-cc2520"
        else:
            assert False, "The platform does not support 6lowpan. check: %s" % output

    def insert_atmel_mode(self):
        ''' Insert atmel modules 
        @fn insert_atmel_mode
        @param self
        @return
        '''
        (status, output) = self.target.run('dmesg -c')
        (status, output) = self.target.run('modprobe %s' % self.atmel_mod_name)
        assert status == 0, "Error messages: %s" % output 
        # Check dmesg log, to see if the 802.15.4 is registered
        (status, output) = self.target.run('dmesg')
        if "802.15.4 chip registered" in output:
            pass
        else:
            assert False, "Not initialize 802.15.4 module. see dmesg log:\n%s" % output 

    def remove_atmel_mode(self):
        ''' Remove atmel modules
        @fn remove_atmel_mode
        @param self
        @return
        '''
        if self.platform == "Galileo":
            self.target.run('rmmod at86rf230')
            self.target.run('rmmod spi_quark_board')
            self.target.run('rmmod spi_quark_at86rf230')
        elif self.platform == "MinnowMax":
            self.target.run('rmmod spi_minnow_board')
            self.target.run('rmmod spi_minnow_at86rf230')           

        (status, output) = self.target.run('lsmod')
        if "spi_quark_at" in output or "spi_minnow_at" in output:
            assert False, "Fail to remove atmel modules:\n%s" % output

    def insert_cc2520_mode(self):
        ''' Insert cc2520 modules 
        @fn insert_cc2520_mode
        @param self
        @return
        '''
        (status, output) = self.target.run('modprobe %s' % self.cc2520_mod_name)
        assert status == 0, "Error messages: %s" % output 
        # Check dmesg log, to see if the 802.15.4 is registered
        (status, output) = self.target.run('lsmod')
        if "spi_minnow_cc2520" in output:
            pass
        else:
            assert False, "Not initialize cc2520 module. see lsmod:\n%s" % output

    def remove_cc2520_mode(self):
        ''' Remove cc2520 modules
        @fn remove_cc2520_mode
        @param self
        @return
        '''
        self.target.run('rmmod spi_minnow_cc2520')

        (status, output) = self.target.run('lsmod')
        if "cc2520" in output:
            assert False, "Fail to remove cc2520 modules:\n%s" % output

    def atmel_enable_lowpan0(self, ip_number):
        ''' enable atmel chipset on target 
        @fn atmel_enable_lowpan0
        @param self
        @param ip_number: a0:0:0:0:0:0:0:[ip_number]
        @return
        '''
        # get device ip for debug
        my_ip=self.target.ip
      
        # insert module
        (status, output) = self.target.run('modprobe %s' % self.atmel_mod_name)
        time.sleep(1)
        assert status == 0, "[%s] Insert atmel module fails: %s" % (my_ip, output)
        # set wpan0
        ip_set="ip link set wpan0 address a0:0:0:0:0:0:0:%s" % ip_number
        (status, output) = self.target.run(ip_set) 
        time.sleep(1)
        # set channel as 5
        wpan_set="iz set wpan0 777 800%s 5" % ip_number
        (status, output) = self.target.run(wpan_set) 
        time.sleep(1)
        # bring up wpan0
        (status, output) = self.target.run('ifconfig wpan0 up') 
        time.sleep(1)
        assert status == 0, "[%s] Bring up wpan0 fails: %s" % (my_ip, output)
        # add lowpan0 
        (status, output) = self.target.run('ip link add link wpan0 name lowpan0 type lowpan') 
        time.sleep(1)
        # bring up lowpan0
        (status, output) = self.target.run('ifconfig lowpan0 up') 
        time.sleep(1)
        assert status == 0, "[%s] Bring up lowpan0 fails: %s" % (my_ip, output)

    def get_lowpan0_ip(self):  
        ''' Get lowpan0 (ipv6) address 
        @fn get_lowpan0_ip
        @param self
        @param target_number: 0 stands for main_target, 1 stands for second target
        @return
        '''
        cmd="ifconfig lowpan0 | grep 'inet6 addr:'"
        (status, output) = self.target.run(cmd)
        return output.split('%')[0].split()[2]    

    def lowpan0_ping6_check(self, ipv6):
        ''' On main target, run ping6 to ping second's ipv6 address 
        @fn lowpan0_ping6_check
        @param self
        @param ipv6: second target ipv6 address
        @return
        '''
        cmd='ping6 -I lowpan0 -c 5 %s' % ipv6
        (status, output) = self.target.run(cmd)
        assert status == 0, "Ping second target lowpan0 ipv6 address fail: %s" % output

    def clean_up(self):
        ''' Clean up izchat process
        @fn clean_up
        @param self
        @return
        '''
        # Clean up izchat process
        self.target.run('killall izchat')
        time.sleep(1)
        # Turn down 6lowpan related network interfaces
        self.target.run('ifconfig lowpan0 down')
        time.sleep(1)
        self.target.run('ifconfig wpan0 down')
        time.sleep(1)

    def lowpan0_izchat_check(self, remote_ip):
        ''' On main target, run izchat to communicate with each other 
        @fn lowpan0_izchat_check
        @param self
        @param remote_ip: the ipv4 address of the remote device
        @return
        '''
        # By own ip6 address, identify src and tag
        if self.get_lowpan0_ip().split(':')[-1] == "1":
            src="8001"
            tar="8002"
        elif self.get_lowpan0_ip().split(':')[-1] == "2":
            src="8002"
            tar="8001"
        print '\n'    
        # Setup remote device to send a string for 5 times 
        send_expect = os.path.join(os.path.dirname(__file__), "files/izchat_send.exp")
        send_cmd = "expect %s 777 %s %s %s" % (send_expect, tar, src, remote_ip)
        subprocess.Popen(send_cmd, shell=True)

        # Setup device to receive the string
        receive_expect = os.path.join(os.path.dirname(__file__), "files/izchat_receive.exp")
        (status, output) = shell_cmd_timeout("expect %s 777 %s %s %s" % (receive_expect, src, tar, self.target.ip))
        assert status == 2, "Izchat with each other fails: %s" % output

##
# @}
# @}
##

