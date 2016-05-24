"""
@file comm_ethernet.py
"""

##
# @addtogroup ethernet ethernet
# @brief This is ethernet component
# @{
# @addtogroup comm_ethernet comm_ethernet
# @brief This is comm_ethernet module
# @{
##

import time
import os
import string
from oeqa.oetest import oeRuntimeTest
from oeqa.utils.helper import shell_cmd_timeout
from oeqa.utils.decorators import tag

@tag(TestType="EFT")
class CommEthernet(oeRuntimeTest):
    """
    @class CommEthernet
    """
    def get_ipv6(self):
        """
        @fn get_ipv6
        @param self
        @return
        """
        time.sleep(1)
        # Check ip address by ifconfig command
        interface = "nothing"
        (status, interface) = self.target.run("ifconfig | grep '^enp' | awk '{print $1}'")
        (status, output) = self.target.run("ifconfig %s | grep 'inet6 addr:' | awk '{print $3}'" % interface)
        if output.split('%')[0] == '':
            assertEqual(status, 0, msg="Target ipv6 address get fail: %s" % output)
        else:
            return output.split('%')[0]

    def get_ipv4(self):
        """
        @fn get_ipv4
        @param self
        @return
        """
        time.sleep(1)
        # Check ip address by ifconfig command
        interface = "nothing"
        (status, interface) = self.target.run("ifconfig | grep '^enp' | awk '{print $1}'")
        (status, output) = self.target.run("ifconfig %s | grep 'inet addr:' | awk '{print $2}'" % interface)
        if output.split(':')[1] == '':
            assertEqual(status, 0, msg="Target ipv4 address get fail: %s" % output)
        else:
            return output.split(':')[1]

    def get_interface(self):
        """
        @fn get_interface
        @param self
        @return
        """
        # if user takes -s option, it is host's IP, directly use it
        if '192.168.7.1' == self.target.server_ip:
            # Get target ip address prefix of LAN, for example, 192.168.8.100 is 192.168.8
            ipv4 = self.get_ipv4().split('.')
            prefix = "%s.%s.%s" % (ipv4[0], ipv4[1], ipv4[2])
        else:
            prefix = self.target.server_ip
        # Use this prefix to get corresponding interface of the host
        (status, ifconfig) = shell_cmd_timeout('ifconfig')
        for line in ifconfig.splitlines():
            if "inet addr:%s" % prefix in line:
                index = ifconfig.splitlines().index(line)
                return ifconfig.splitlines()[index - 1].split()[0]

        # if above return is not OK, there might be error, return Blank
        self.assertEqual(1, 0, msg="Host interface with %s is not found" % prefix)

    @tag(FeatureID="IOTOS-489")
    def test_ethernet_ipv6_ping(self):
        '''Ping other device via ipv6 address of the ethernet
        @fn test_ethernet_ipv6_ping
        @param self
        @return
        '''
        # Get target ipv6 address
        ip6_address = self.get_ipv6()
        # ping6 needs host's ethernet interface by -I, 
        # because default gateway is only for ipv4
        host_eth = self.get_interface()
        cmd = "ping6 -I %s %s -c 1" % (host_eth, ip6_address) 
        status, output = shell_cmd_timeout(cmd, timeout=60)
        ##
        # TESTPOINT: #1, test_ethernet_ipv6_ping
        #
        self.assertEqual(status, 0, msg="Error messages: %s" % output)

    @tag(FeatureID="IOTOS-489")
    def test_ethernet_ipv6_ssh(self):
        '''SSH other device via ipv6 address of the ethernet
        @fn test_ethernet_ipv6_ssh
        @param self
        @return
        '''
        # Get target ipv6 address
        ip6_address = self.get_ipv6()
        # Same as ping6, ssh with ipv6 also need host's ethernet interface
        # ssh root@<ipv6 address>%<eth>
        host_eth = self.get_interface()

        exp = os.path.join(os.path.dirname(__file__), "files/ipv6_ssh.exp")
        cmd = "expect %s %s %s %s" % (exp, ip6_address, "ostro", host_eth)
        status, output = shell_cmd_timeout(cmd, timeout=60)
        # In expect, it will input yes and password while login. And do 'ls /'
        # If see /home folder, it will return 2 as successful status.
        ##
        # TESTPOINT: #1, test_ethernet_ipv6_ssh
        #
        self.assertEqual(status, 2, msg="Error messages: %s" % output)

##
# @}
# @}
##

