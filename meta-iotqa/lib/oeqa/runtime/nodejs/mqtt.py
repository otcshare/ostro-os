# -*- coding:utf8 -*-

"""
@file mqtt.py
"""

##
# @addtogroup nodejs mqtt
# @brief This is nodejs component
# @brief This is mqtt module
##

import os
import sys
import subprocess

from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag

def inst_cp_module_mqtt():
    '''
    Check command "sudo" is exist, install node module mqtt and mosca to host
    '''
    sudo_status = subprocess.Popen('sudo', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if "usage: sudo" not in sudo_status.stdout.read().decode('utf-8'):
        print('The command "sudo" dose not exists!')
    #install node module mqtt and mosca
    inst_mqtt_cmd = 'npm install mqtt mosca >/dev/null 2>&1'
    inst_status = subprocess.Popen(inst_mqtt_cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=target_file)
    inst_status.communicate()
    if inst_status.returncode != 0:
        print('Re-install node modules using root!')
        inst_mqtt = subprocess.Popen(('sudo ' + inst_mqtt_cmd), shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=target_file)
        inst_mqtt.communicate()
        if inst_mqtt.returncode != None:
            print('Install node modules failed! Please check it!' + \
                inst_mqtt.stdout.read().decode('utf-8'))

@tag(TestType='EFT', FeatureID='IOTOS-1160')
class mqttTest(oeRuntimeTest):
    """
    @class mqttTest
    """
    global target_file, mqtt_file
    CONST_PATH = os.path.dirname(os.path.realpath(__file__))
    target_file = os.path.join(CONST_PATH, 'files')
    mqtt_file = os.path.join(target_file, 'mqtt')
    def setUp(self):
        '''
        Copy mqtt.js and node module mqtt to target
        @fn setUp
        @param self
        @param return
        '''
        inst_cp_module_mqtt()
        if os.path.exists(os.path.join(target_file, 'node_modules')) and \
            os.path.exists(os.path.join(mqtt_file, 'mqtt.js')):
            oldscp = self.target.connection.scp[:]
            self.target.connection.scp.insert(1, '-r')
            self.target.copy_to(mqtt_file, '/tmp')
            self.target.copy_to(
                os.path.join(target_file, 'node_modules'),
                '/tmp'
                )
            self.target.connection.scp[:] = oldscp
        else:
            print("Please check there have files in mqtt and node_modules")
            sys.exit(1)

    def test_mqtt(self):
        '''
        Execute the tests and check the status
        @fn test_mqtt
        @param self
        @param return
        '''
        # Enable the port 1883
        self.target.run('ip6tables -A INPUT -p tcp --dport 1883 -j ACCEPT')
        (status, output) =  self.target.run("node /tmp/mqtt/mqtt.js")
        self.assertEqual(status, 0)
        self.assertTrue('error' not in output.lower())
        self.assertTrue('Mosca server is up and running' in output)
        self.assertTrue('Hello Mqtt' in output)

    def tearDown(self):
        '''
        Clean up the test environment
        @fn tearDown
        @param self
        @param return
        '''
        os.system('rm -rf %s >/dev/null 2>&1' % os.path.join(target_file, 'node_modules'))
        self.target.run('rm -rf /tmp/node_modules')
        self.target.run('rm -rf /tmp/mqtt')
        self.target.run('ip6tables -D INPUT -p tcp --dport 1883 -j ACCEPT')
