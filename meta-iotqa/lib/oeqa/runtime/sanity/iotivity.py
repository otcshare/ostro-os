"""
@file iotivity.py
"""

##
# @addtogroup sanity sanity
# @brief This is sanity component
# @{
# @addtogroup iotivity iotivity
# @brief This is iotivity module
# @{
##

import os
import time
import string
from oeqa.oetest import oeRuntimeTest
from oeqa.utils.helper import shell_cmd_timeout
from oeqa.utils.helper import run_as, add_group, add_user, remove_user
from oeqa.utils.decorators import tag

@tag(TestType="FVT", FeatureID="IOTOS-498,IOTOS-450,IOTOS-1019,IOTOS-1004")
class IOtvtClient(oeRuntimeTest):
    """
    @class IOtvtClient
    """
    @classmethod
    def setUpClass(cls):
        '''Test simpleserver and simpleclient.
        @fn setUpClass
        @param cls
        @return
        '''
        cls.tc.target.run("killall simpleserver")
        cls.tc.target.run("killall simpleclient")
        # add group and non-root user
        add_group("tester")
        add_user("iotivity-tester", "tester")

        # set up firewall
        (status, output) = cls.tc.target.run("cat /proc/sys/net/ipv4/ip_local_port_range")
        port_range = output.split()

        cls.tc.target.run("/usr/sbin/ip6tables -w -A INPUT -s fe80::/10 -p udp -m udp --dport 5683 -j ACCEPT")
        cls.tc.target.run("/usr/sbin/ip6tables -w -A INPUT -s fe80::/10 -p udp -m udp --dport 5684 -j ACCEPT")
        cls.tc.target.run("/usr/sbin/ip6tables -w -A INPUT -s fe80::/10 -p udp -m udp --dport %s:%s -j ACCEPT" % (port_range[0], port_range[1]))

        # start server
        server_cmd = "/opt/iotivity/examples/resource/cpp/simpleserver > /tmp/svr_output &"
        run_as("iotivity-tester", server_cmd)
        time.sleep(1)
        # start client to get info
        client_cmd = "/opt/iotivity/examples/resource/cpp/simpleclient > /tmp/output &"
        run_as("iotivity-tester", client_cmd)
        print ("\npatient... simpleclient needs long time for its observation")
        time.sleep(60)
        # If there is no 'Observe is used', give a retry.
        (status, output) = cls.tc.target.run('cat /tmp/output')
        if "Observe is used." in output:
            pass
        else:
            cls.tc.target.run("killall simpleserver")
            cls.tc.target.run("killall simpleclient")
            time.sleep(2)
            (status, output) = cls.tc.target.run(server_cmd)
            cls.tc.target.run(client_cmd)
            time.sleep(60)
        # Retry ends.

    @classmethod
    def tearDownClass(cls):
        '''kill on Target
        @fn tearDownClass
        @param cls
        @return
        '''
        remove_user("iotivity-tester")
        cls.tc.target.run("killall simpleserver")
        cls.tc.target.run("killall simpleclient")

    def test_iotvt_findresource(self):
        '''Target finds resource, registered by Host
        @fn test_iotvt_findresource
        @param self
        @return
        '''
        (status, output) = self.target.run('cat /tmp/output')
        ret = 0
        if "DISCOVERED Resource" in output:
            pass
        else:
           ret = 1
        ##
        # TESTPOINT: #1, test_iotvt_findresource
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)

    def test_iotvt_getstate(self):
        '''Target gets resource state
        @fn test_iotvt_getstate
        @param self
        @return
        '''
        (status, output) = self.target.run('cat /tmp/output')
        ret = 0
        if "GET request was successful" in output:
            pass
        else:
           ret = 1
        ##
        # TESTPOINT: #1, test_iotvt_getstate
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)

    def test_iotvt_observer(self):
        '''Target sets observer
        @fn test_iotvt_observer
        @param self
        @return
        '''
        (status, output) = self.target.run('cat /tmp/output')
        ret = 0
        if "Observe is used." in output:
            pass
        else:
           ret = 1
        ##
        # TESTPOINT: #1, test_iotvt_observer
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)

    def test_iotvt_setstate(self):
        '''Target sets resource state
        @fn test_iotvt_setstate
        @param self
        @return
        '''
        (status, output) = self.target.run('cat /tmp/output')
        ret = 0
        if "PUT request was successful" in output:
            pass
        else:
           ret = 1
        ##
        # TESTPOINT: #1, test_iotvt_setstate
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)

    def test_iotvt_regresource(self):
        '''After several seconds, server should not crash
        @fn test_iotvt_regresource
        @param self
        @return
        '''
        time.sleep(2)
        # check if simpleserver is there
        (status, output) = self.target.run('ps -ef')
        ##
        # TESTPOINT: #1, test_iotvt_regresource
        #
        self.assertEqual(output.count("simpleserver"), 1, msg="Error messages: %s" % output)

##
# @}
# @}
##

