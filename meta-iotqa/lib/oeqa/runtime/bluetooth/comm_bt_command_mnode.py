"""
@file comm_bt_command_mnode.py
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
class CommBTTestMNode(oeRuntimeTest):
    """
    @class CommBTTestMNode
    """
    @classmethod
    def setUpClass(cls):
        '''Copy gatttool to /tmp/ folder
        @fn setUpClass
        @param cls
        @return
        '''
        bt1=bluetooth.BTFunction(cls.tc.targets[0])
        bt2=bluetooth.BTFunction(cls.tc.targets[1])
        copy_to_path = os.path.join(get_files_dir(), 'gatttool')
        cls.tc.targets[0].copy_to(copy_to_path, "/tmp/")
        bt1.target.run('chmod +x /tmp/gatttool')
        bt2.target.run('chmod +x /tmp/gatttool')

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

    @tag(FeatureID="IOTOS-456")
    def test_bt_gatt_read_primary(self):
        '''Use gatttool to show remote primary attr handles
        @fn test_bt_gatt_read_primary
        @param self
        @return
        '''
        for i in range(3):
            self.bt2.target_hciconfig_init()
            self.bt2.set_leadv()
            (status, output) = self.bt1.gatt_basic_check(self.bt2.get_bt_mac(), 'primary')
            if status == 0:
                break

        self.assertEqual(status, 0, msg="gatttool Primary is wrong: %s" % output)

    @tag(FeatureID="IOTOS-456")
    def test_bt_gatt_read_characteristics(self):
        '''Use gatttool to show target characteristics handles
        @fn test_bt_gatt_read_characteristics
        @param self
        @return
        '''
        for i in range(3):
            self.bt2.target_hciconfig_init()
            self.bt2.set_leadv()
            (status, output) = self.bt1.gatt_basic_check(self.bt2.get_bt_mac(), 'characteristics')
            if status == 0:
                break

        self.assertEqual(status, 0, msg="gatttool characteristics fails: %s" % output)

    @tag(FeatureID="IOTOS-456")
    def test_bt_gatt_read_handle(self):
        '''Use gatttool to read target handle value
        @fn test_bt_gatt_read_handle
        @param self
        @return
        '''
        for i in range(3):
            self.bt2.target_hciconfig_init()
            self.bt2.set_leadv()
            (status, output) = self.bt1.gatt_basic_check(self.bt2.get_bt_mac(), 'handle')
            if status == 0:
                break

        self.assertEqual(status, 0, msg="gatttool read handle fails: %s" % output)

    @tag(FeatureID="IOTOS-456")
    def test_bt_gatt_connect(self):
        '''Use gatttool interactive mode to do connect
        @fn test_bt_gatt_connect
        @param self
        @return
        '''
        for i in range(3):
            self.bt2.target_hciconfig_init()
            self.bt2.set_leadv()
            (status, output) = self.bt1.gatt_basic_check(self.bt2.get_bt_mac(), 'connect')
            if status == 2:
                break

        self.assertEqual(status, 2, msg="gatttool connect fails: %s" % output)

    @tag(FeatureID="IOTOS-456")
    def test_bt_remote_gatt_read_primary(self):
        '''Use gatttool to show host primary attr handles
        @fn test_bt_remote_gatt_read_primary
        @param self
        @return
        '''
        for i in range(3):
            self.bt1.target_hciconfig_init()
            self.bt1.set_leadv()
            (status, output) = self.bt2.gatt_basic_check(self.bt1.get_bt_mac(), 'primary')
            if status == 0:
                break

        self.assertEqual(status, 0, msg="gatttool be read primary fails: %s" % output)

    @tag(FeatureID="IOTOS-456")
    def test_bt_remote_gatt_read_characteristics(self):
        '''Use gatttool to show host characteristics handles
        @fn test_bt_remote_gatt_read_characteristics
        @param self
        @return
        '''
        for i in range(3):
            self.bt1.target_hciconfig_init()
            self.bt1.set_leadv()
            (status, output) = self.bt2.gatt_basic_check(self.bt1.get_bt_mac(), 'characteristics')
            if status == 0:
                break

        self.assertEqual(status, 0, msg="gatttool be read characteristics fails: %s" % output)

    @tag(FeatureID="IOTOS-456")
    def test_bt_remote_gatt_read_handle(self):
        '''Use gatttool to read host handle value
        @fn test_bt_remote_gatt_read_handle
        @param self
        @return
        '''
        for i in range(3):
            self.bt1.target_hciconfig_init()
            self.bt1.set_leadv()
            (status, output) = self.bt2.gatt_basic_check(self.bt1.get_bt_mac(), 'handle')
            if status == 0:
                break

        self.assertEqual(status, 0, msg="gatttool be read handle fails: %s" % output)

    @tag(FeatureID="IOTOS-456")
    def test_bt_remote_gatt_connect(self):
        '''Use gatttool interactive mode to do connect to host
        @fn test_bt_remote_gatt_connect
        @param self
        @return
        '''
        for i in range(3):
            self.bt1.target_hciconfig_init()
            self.bt1.set_leadv()
            (status, output) = self.bt2.gatt_basic_check(self.bt1.get_bt_mac(), 'connect')
            if status == 2:
                break

        self.assertEqual(status, 2, msg="gatttool be connected fails: %s" % output)

    @tag(FeatureID="IOTOS-456")
    def test_bt_visible(self):
        '''Do traditional visible and be scanned by other (not ble scan)
        @fn test_bt_visible
        @param self
        @return
        '''
        self.bt1.target.run('hciconfig hci0 noleadv')
        for i in range(3):
            # For init function already set visible status, directly be scanned.  
            exp = os.path.join(os.path.dirname(__file__), "files/bt_scan.exp")
            cmd = "expect %s %s %s" % (exp, self.bt2.target.ip, self.bt1.get_bt_mac())
            status, output = shell_cmd_timeout(cmd, timeout=100)
            if status == 2:
                break
        self.assertEqual(status, 2, msg="Scan remote device fails: %s" % output) 

    @tag(FeatureID="IOTOS-456")
    def test_bt_scan(self):
        '''Scan nearby bluetooth devices (not ble scan)
        @fn test_bt_scan
        @param self
        @return
        '''
        self.bt2.target.run('hciconfig hci0 noleadv')
        for i in range(3):
            # For init function already set visible status, directly be scanned.  
            exp = os.path.join(os.path.dirname(__file__), "files/bt_scan.exp")
            cmd = "expect %s %s %s" % (exp, self.bt1.target.ip, self.bt2.get_bt_mac())
            status, output = shell_cmd_timeout(cmd, timeout=100)
            if status == 2:
                break
        self.assertEqual(status, 2, msg="Scan remote device fails: %s" % output) 

    @tag(FeatureID="IOTOS-759")
    def test_bt_le_advertising(self):
        '''Target does LE advertising, another device scans it
        @fn test_bt_le_advertising
        @param self
        @return
        '''
        for i in range(3):
            # close legacy iscan mode
            self.bt1.target.run('hciconfig hci0 noscan')
            # begin low-energy scan
            self.bt1.target.run('hciconfig hci0 leadv')
            time.sleep(1)
            # Another device starts bluetoothctl to scan target 
            exp = os.path.join(os.path.dirname(__file__), "files/bt_scan.exp")
            cmd = "expect %s %s %s" % (exp, self.bt2.target.ip, self.bt1.get_bt_mac())
            status, output = shell_cmd_timeout(cmd, timeout=100)
            if status == 2:
                break
            else:
                self.bt1.target.run('hciconfig hci0 reset')
                time.sleep(3)
        self.assertEqual(status, 2, msg="Be LE-scanned fails: %s" % output) 

    @tag(FeatureID="IOTOS-770")
    def test_bt_le_scan(self):
        '''Another device (host) does LE advertising, target scans it
        @fn test_bt_le_scan
        @param self
        @return
        '''
        for i in range(3):
            # close legacy iscan mode
            self.bt2.target.run('hciconfig hci0 noscan')
            # begin low-energy scan
            self.bt2.target.run('hciconfig hci0 leadv')
            time.sleep(1)
            # Device starts bluetoothctl to scan others 
            exp = os.path.join(os.path.dirname(__file__), "files/bt_scan.exp")
            cmd = "expect %s %s %s" % (exp, self.bt1.target.ip, self.bt2.get_bt_mac())
            status, output = shell_cmd_timeout(cmd, timeout=100)
            if status == 2:
                break
            else:
                self.bt2.target.run('hciconfig hci0 reset')
                time.sleep(3)
        self.assertEqual(status, 2, msg="LE Scan other fails: %s" % output) 

    @tag(FeatureID="IOTOS-453")
    def test_bt_pairing(self):
        '''Use bluetoothctl to pair IoT device with host
        @fn test_bt_pairing
        @param self
        @return
        '''
        # On remote, start pair_slave in back-ground
        slave_exp = os.path.join(os.path.dirname(__file__), "files/bt_pair_slave_on_iot.exp")
        cmd = "%s %s %s" % (slave_exp, self.bt2.target.ip, self.bt1.get_bt_mac())
        subprocess.Popen(cmd, shell=True)

        # On target, perform pair_master
        master_exp = os.path.join(os.path.dirname(__file__), "files/bt_pair_master.exp")
        cmd = "expect %s %s %s" % (master_exp, self.bt1.target.ip, self.bt2.get_bt_mac())
        for i in range(3):
            (status, output) = shell_cmd_timeout(cmd, timeout=200)
            if status == 2:
                break
        self.assertEqual(status, 2, msg="expect excution fail: %s" % output)

        # On target, check paired devices to see if IoT is in
        check_exp = os.path.join(os.path.dirname(__file__), "files/bt_list_paired_device.exp")
        (status, output) = shell_cmd_timeout("%s %s | grep '^Device %s'" % (check_exp, self.bt1.target.ip, self.bt2.get_bt_mac()), timeout=20)
        self.assertEqual(status, 0, msg="Not found IoT device paired")

##
# @}
# @}
##

