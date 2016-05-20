"""
@file iotvt_integration_mnode.py
"""

##
# @addtogroup iotivity iotivity
# @brief This is iotivity component
# @{
# @addtogroup iotvt_integration iotvt_integration
# @brief This is iotvt_integration module
# @{
##

import os
import time
import string
import subprocess
from oeqa.oetest import oeRuntimeTest
from oeqa.utils.helper import get_files_dir
from oeqa.utils.helper import shell_cmd_timeout
from oeqa.utils.helper import run_as, add_group, add_user, remove_user
from oeqa.utils.decorators import tag

@tag(TestType="EFT", FeatureID="IOTOS-754,IOTOS-1019,IOTOS-1004")
class IOtvtIntegrationMNode(oeRuntimeTest):
    """
    @class IOtvtIntegrationMNode
    """
    @classmethod
    def setUpClass(cls):
        '''Clean all the server and client firstly
        @fn setUpClass
        @param cls
        @return
        '''
        # Init main target
        run_as("root", "killall presenceserver presenceclient devicediscoveryserver devicediscoveryclient", target=cls.tc.targets[0])        
        run_as("root", "killall fridgeserver fridgeclient garageserver garageclient groupserver groupclient", target=cls.tc.targets[0])
        run_as("root", "killall roomserver roomclient simpleserver simpleclient simpleserverHQ simpleclientHQ", target=cls.tc.targets[0])
        run_as("root", "killall simpleclientserver threadingsample", target=cls.tc.targets[0])
        # Init second target
        run_as("root", "killall presenceserver presenceclient devicediscoveryserver devicediscoveryclient", target=cls.tc.targets[1])        
        run_as("root", "killall fridgeserver fridgeclient garageserver garageclient groupserver groupclient", target=cls.tc.targets[1])
        run_as("root", "killall roomserver roomclient simpleserver simpleclient simpleserverHQ simpleclientHQ", target=cls.tc.targets[1])
        run_as("root", "killall simpleclientserver threadingsample", target=cls.tc.targets[1])
        # Clean output file on two targets, main is client part and second is server part
        run_as("root", "rm -f /tmp/svr_output", target=cls.tc.targets[1])
        run_as("root", "rm -f /tmp/output", target=cls.tc.targets[0])
        # add group and non-root user on both sides
        add_group("tester", target=cls.tc.targets[0])
        add_user("iotivity-tester", "tester", target=cls.tc.targets[0])
        add_group("tester", target=cls.tc.targets[1])
        add_user("iotivity-tester", "tester", target=cls.tc.targets[1])
        # Setup firewall accept for multicast, on both sides
        run_as("root", "/usr/sbin/iptables -w -A INPUT -p udp --dport 5683 -j ACCEPT", target=cls.tc.targets[0])
        run_as("root", "/usr/sbin/iptables -w -A INPUT -p udp --dport 5684 -j ACCEPT", target=cls.tc.targets[0])
        run_as("root", "/usr/sbin/iptables -w -A INPUT -p udp --dport 5683 -j ACCEPT", target=cls.tc.targets[1])
        run_as("root", "/usr/sbin/iptables -w -A INPUT -p udp --dport 5684 -j ACCEPT", target=cls.tc.targets[1])
        # check if image contains iotivity example applications
        (status, output) = run_as("root", "ls /opt/iotivity/examples/resource/", target=cls.tc.targets[0])
        if "cpp" in output:
            pass
        else:
            assert 1 == 0, 'There is no iotivity exmaple app installed in target0'
        (status, output) = run_as("root", "ls /opt/iotivity/examples/resource/", target=cls.tc.targets[1])
        if "cpp" in output:
            pass
        else:
            assert 1 == 0, 'There is no iotivity exmaple app installed in target1'

    @classmethod
    def tearDownClass(cls):
        '''Clean user
        @fn setUpClass
        @param cls
        @return
        '''
        remove_user("iotivity-tester", target=cls.tc.targets[0])
        remove_user("iotivity-tester", target=cls.tc.targets[1])

    def get_server_ipv6(self):
        """
        @fn get_server_ipv6
        @param self
        @return
        """
        time.sleep(1)
        # Check ip address by ifconfig command
        interface = "nothing"
        (status, interface) = run_as("root", "ifconfig | grep '^enp'", target=self.targets[1])
        (status, output) = run_as("root", "ifconfig %s | grep 'inet6 addr:'" % interface.split()[0], target=self.targets[1])
        return output.split('%')[0].split()[-1]

    def presence_check(self, para):
        '''this is a function used by presence test
        @fn presence_check
        @param self
        @return
        '''
        # start server
        server_cmd = "/opt/iotivity/examples/resource/cpp/presenceserver > /tmp/svr_output &"
        (status, output) = run_as("iotivity-tester", server_cmd, target=self.targets[1])
        time.sleep(1)
        # start client to get info
        client_cmd = "/opt/iotivity/examples/resource/cpp/presenceclient -t %d > /tmp/output &" % para
        run_as("iotivity-tester", client_cmd, target=self.targets[0])
        # Some platform is too slow, it needs more time to sleep. E.g. MinnowMax
        time.sleep(60)
        (status, output) = run_as("iotivity-tester", "cat /tmp/output", target=self.targets[0])
        run_as("root", "killall presenceserver presenceclient", target=self.targets[0]) 
        run_as("root", "killall presenceserver presenceclient", target=self.targets[1]) 
        time.sleep(3)
        return output.count("Received presence notification from : %s" % self.targets[1].ip) + \
               output.count("Received presence notification from : %s" % self.get_server_ipv6())

    def test_mnode_fridge(self):
        '''
            Test fridgeserver and fridgeclient. 
            The server registers resource with 2 doors and 1 light, client connects to the 
            server and fetch the information to print out. 
        @fn test_fridge
        @param self
        @return
        '''
        # ensure env is clean
        # start server
        server_cmd = "/opt/iotivity/examples/resource/cpp/fridgeserver > /tmp/svr_output &"
        (status, output) = run_as("iotivity-tester", server_cmd, target=self.targets[1])
        time.sleep(1)
        # start client to get info
        client_cmd = "/opt/iotivity/examples/resource/cpp/fridgeclient > /tmp/output &"
        run_as("iotivity-tester", client_cmd, target=self.targets[0])
        time.sleep(5)
        (status, output) = run_as("iotivity-tester", 'cat /tmp/output', target=self.targets[0])
        # judge if the values are correct
        ret = 0
        if "Name of device: Intel Powered 2 door, 1 light refrigerator" in output and \
           "Delete ID is 0 and resource URI is /device" in output:
            pass
        else:
            ret = 1
        # kill server and client
        run_as("root", "killall fridgeserver fridgeclient", target=self.targets[0])        
        run_as("root", "killall fridgeserver fridgeclient", target=self.targets[1])        
        time.sleep(3)       
        ##
        # TESTPOINT: #1, test_fridge
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)                      

    def test_mnode_garage(self):
        '''
            Test garageserver and garageclient. 
            While server and client communication, remove one attribute Name from 
            OCRepresentation. Then the attribute number of OCRepresentation should 
            reduce 1. 
        @fn test_garage
        @param self
        @return
        '''
        # start server
        server_cmd = "/opt/iotivity/examples/resource/cpp/garageserver > /tmp/svr_output &"
        (status, output) = run_as("iotivity-tester", server_cmd, target=self.targets[1])
        time.sleep(1)
        # start client to get info
        client_cmd = "/opt/iotivity/examples/resource/cpp/garageclient > /tmp/output &"
        run_as("iotivity-tester", client_cmd, target=self.targets[0])
        time.sleep(5)
        (status, output) = run_as("iotivity-tester", 'cat /tmp/output', target=self.targets[0])
        # judge if the values are correct
        ret = 0
        if "GET request was successful" in output and \
           "attribute: name, was removed successfully from rep2." in output and \
           "Number of attributes in rep2: 6" in output and \
           "PUT request was successful" in output:
            pass
        else:
            ret = 1
        # kill server and client
        run_as("root", "killall garageserver garageclient", target=self.targets[0])        
        run_as("root", "killall garageserver garageclient", target=self.targets[1])        
        time.sleep(3)       
        ##
        # TESTPOINT: #1, test_garage
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)                      

    def test_mnode_group(self):
        '''
            groupclient has 4 main operations. Only option1 is doable.
            In option (user inputs 1), it will set ActionSet value of rep. This case
            is to check if the set operation is done. 
        @fn test_group
        @param self
        @return
        '''
        # start light server and group server
        lightserver_cmd = "/opt/iotivity/examples/resource/cpp/lightserver > /tmp/svr_output &"
        (status, output) = run_as("root", lightserver_cmd, target=self.targets[1])
        time.sleep(2)
        ssh_cmd = "ssh root@%s -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=ERROR" % self.targets[1].ip
        groupserver_cmd = "/opt/iotivity/examples/resource/cpp/groupserver > /dev/null 2>&1"
        subprocess.Popen("%s %s" % (ssh_cmd, groupserver_cmd), shell=True)
        time.sleep(3)
        
        # start client to get info, here needs user input. So use expect
        exp_cmd = os.path.join(os.path.dirname(__file__), "files/group_client.exp")
        status, output = shell_cmd_timeout("expect %s %s" % (exp_cmd, self.target.ip), timeout=200)
        # kill server and client
        run_as("root", "killall lightserver groupserver groupclient", target=self.targets[0])        
        run_as("root", "killall lightserver groupserver groupclient", target=self.targets[1])        
        time.sleep(3)       
        ##
        # TESTPOINT: #1, test_group
        #
        self.assertEqual(status, 2, msg="expect excution fail\n %s" % output)

    def test_mnode_presence_unicast(self):
        '''
            Presence test is complex. It contains 6 sub-tests. 
            Main goal (client) is to observe server resource presence status (presence/stop).
            Every change will trigger a Received presence notification on client side. 
            To each client observation mode:
            -t 1 Unicast                    --- it will receive 7 notifications
            -t 2 Unicast with one filter    --- it will receive 5 notifications
            -t 3 Unicast with two filters   --- it will receive 6 notifications
            -t 4 Multicast                  --- it will receive 7 notifications
            -t 5 Multicast with one filter  --- it will receive 5 notifications
            -t 6 Multicast with two filters --- it will receive 6 notifications
        @fn test_presence_unicast
        @param self
        @return
        '''
        number = self.presence_check(1)
        ##
        # TESTPOINT: #1, test_presence_unicast
        #
        assert number > 0, "type 1 should have no notifications"

    def test_mnode_presence_unicast_one_filter(self):
        ''' See instruction in test_presence_unicast. 
        @fn test_presence_unicast_one_filter
        @param self
        @return
        '''
        number = self.presence_check(2)
        ##
        # TESTPOINT: #1, test_presence_unicast_one_filter
        #
        assert number > 0, "type 2 should have no notifications"

    def test_mnode_presence_unicast_two_filters(self):
        ''' See instruction in test_presence_unicast. 
        @fn test_presence_unicast_two_filters
        @param self
        @return
        '''
        number = self.presence_check(3)
        ##
        # TESTPOINT: #1, test_presence_unicast_two_filters
        #
        assert number > 0, "type 3 should have no notifications"

    def test_mnode_presence_multicast(self):
        ''' See instruction in test_presence_unicast. 
        @fn test_presence_multicast
        @param self
        @return
        '''
        number = self.presence_check(4)
        ##
        # TESTPOINT: #1, test_presence_multicast
        #
        assert number > 0, "type 4 should have no notifications"

    def test_mnode_presence_multicast_one_filter(self):
        ''' See instruction in test_presence_unicast. 
        @fn test_presence_multicast_one_filter
        @param self
        @return
        '''
        number = self.presence_check(5)
        ##
        # TESTPOINT: #1, test_presence_multicast_one_filter
        #
        assert number > 0, "type 5 should have no notifications"

    def test_mnode_presence_multicast_two_filters(self):
        ''' See instruction in test_presence_unicast. 
        @fn test_presence_multicast_two_filters
        @param self
        @return
        '''
        number = self.presence_check(6)
        ##
        # TESTPOINT: #1, test_presence_multicast_two_filters
        #
        assert number > 0, "type 6 should have no notifications"
 
    def test_mnode_room_default_collection(self):
        ''' 
            When number is 1 and request is put, light and fan give response individually.
            So, there is no 'In Server CPP entity handler' output. Each respone is given by
            light or fan. 
        @fn test_room_default_collection
        @param self
        @return
        '''
        # start server
        server_cmd = "/opt/iotivity/examples/resource/cpp/roomserver 1 > /tmp/svr_output &"
        (status, output) = run_as("iotivity-tester", server_cmd, target=self.targets[1])
        time.sleep(1)
        # start client to get info
        client_cmd = "/opt/iotivity/examples/resource/cpp/roomclient > /tmp/output &"
        run_as("iotivity-tester", client_cmd, target=self.targets[0])
        time.sleep(5)
        (status, output) = run_as("iotivity-tester", "cat /tmp/svr_output", target=self.targets[1])
        # kill server and client
        run_as("root", "killall roomserver roomclient", target=self.targets[0])     
        run_as("root", "killall roomserver roomclient", target=self.targets[1])     
        time.sleep(3)   
        ##
        # TESTPOINT: #1, test_room_default_collection
        #
        self.assertEqual(output.count("In Server CPP entity handler"), 0, msg="CPP entity handler is: %s" % output)

    def test_mnode_room_application_collection(self):
        ''' 
            When number is 2 and request is put, room entity handler give light and fan 
            response. So, there are 3 responses output: In Server CPP entity handler.
            In the middle one, it will handle light and fan. 
        @fn test_room_application_collection
        @param self
        @return
        '''
        # start server
        server_cmd = "/opt/iotivity/examples/resource/cpp/roomserver 2 > /tmp/svr_output &"
        run_as("iotivity-tester", server_cmd, target=self.targets[1])
        time.sleep(1)
        # start client to get info
        client_cmd = "/opt/iotivity/examples/resource/cpp/roomclient > /tmp/output &"
        run_as("iotivity-tester", client_cmd, target=self.targets[0])
        time.sleep(6)
        (status, output) = run_as("iotivity-tester", "cat /tmp/svr_output", target=self.targets[1])
        # kill server and client
        run_as("root", "killall roomserver roomclient", target=self.targets[0])        
        run_as("root", "killall roomserver roomclient", target=self.targets[1])        
        time.sleep(3)
        ##
        # TESTPOINT: #1, test_room_application_collection
        #
        self.assertEqual(output.count("In Server CPP entity handler"), 3, msg="CPP entity handler is: %s" % output)                      

    def test_mnode_simple(self):
        '''
            Test simpleserver and simpleclient. 
            After finding resource, simpleclient will do: GET, PUT, POST, Observer sequencely. 
        @fn test_simple
        @param self
        @return
        '''
        for i in range(3):
            # start server
            server_cmd = "/opt/iotivity/examples/resource/cpp/simpleserver > /tmp/svr_output &"
            (status, output) = run_as("iotivity-tester", server_cmd, target=self.targets[1])
            time.sleep(1)
            # start client to get info
            client_cmd = "/opt/iotivity/examples/resource/cpp/simpleclient > /tmp/output &"
            run_as("iotivity-tester", client_cmd, target=self.targets[0])
            print "\npatient... simpleclient needs long time for its observation"
            time.sleep(70)
            (status, output) = run_as("iotivity-tester", 'cat /tmp/output', target=self.targets[0])
            # kill server and client
            run_as("root", "killall simpleserver simpleclient", target=self.targets[0])        
            run_as("root", "killall simpleserver simpleclient", target=self.targets[1])        
            time.sleep(3)
            # judge if the values are correct
            ret = 0
            if "DISCOVERED Resource" in output and \
                "GET request was successful" in output and \
                "PUT request was successful" in output and \
                "POST request was successful" in output and \
                "Observe is used." in output:
                break
            else:
                ret = 1

        ##
        # TESTPOINT: #1, test_simple
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)                      

    def test_mnode_simpleHQ(self):
        '''
            Test simpleserverHQ and simpleclientHQ. 
            Compared to simpleserver, simpleserverHQ removes SlowResponse, and give
            sendResponse (when PUT) / sendPostResponse (when POST). Basically, they
            are the same.  
        @fn test_simpleHQ
        @param self
        @return
        '''
        for i in range(3):
            # start server
            server_cmd = "/opt/iotivity/examples/resource/cpp/simpleserverHQ > /tmp/svr_output &"
            run_as("iotivity-tester", server_cmd, target=self.targets[1])
            time.sleep(1)
            # start client to get info
            client_cmd = "/opt/iotivity/examples/resource/cpp/simpleclientHQ > /tmp/output &"
            run_as("iotivity-tester", client_cmd, target=self.targets[0])
            print "\npatient... simpleclientHQ needs long time for its observation"
            time.sleep(70)
            (status, output) = run_as("iotivity-tester", 'cat /tmp/output', target=self.targets[0])
            # kill server and client
            run_as("root", "killall simpleserverHQ simpleclientHQ", target=self.targets[0])        
            run_as("root", "killall simpleserverHQ simpleclientHQ", target=self.targets[1])        
            time.sleep(3)
            # judge if the values are correct
            ret = 0
            if "DISCOVERED Resource" in output and \
                "GET request was successful" in output and \
                "PUT request was successful" in output and \
                "POST request was successful" in output and \
                "Observe is used." in output:
                break
            else:
                ret = 1

        ##
        # TESTPOINT: #1, test_simpleHQ
        #
        self.assertEqual(ret, 0, msg="Error messages: %s" % output)                      

##
# @}
# @}
##

