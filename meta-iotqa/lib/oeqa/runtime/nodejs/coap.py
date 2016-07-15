# -*- coding:utf8 -*-

"""
@file coap.py
"""

##
# @addtogroup nodejs coap
# @brief This is nodejs component
# @brief This is coap module
##

import os
import sys
import subprocess

from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag

def inst_cp_module_coap():
    '''
    Check command "sudo" is exist, install node module coap to host
    '''
    sudo_status = subprocess.Popen('sudo', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if "usage: sudo" not in sudo_status.stdout.read().decode('utf-8'):
        print('The command "sudo" dose not exists!')
    #install node module coap
    inst_coap_cmd = 'npm install coap >/dev/null 2>&1'
    inst_status = subprocess.Popen(inst_coap_cmd, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=target_file)
    inst_status.communicate()
    if inst_status.returncode != 0:
        print('Re-install node modules using root!')
        inst_coap = subprocess.Popen(('sudo ' + inst_coap_cmd), shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=target_file)
        inst_coap.communicate()
        if inst_coap.returncode != None:
            print('Install node modules failed! Please check it!' + \
                inst_coap.stdout.read().decode('utf-8'))


@tag(TestType='EFT', FeatureID='IOTOS-1161')
class CoapTest(oeRuntimeTest):
    """
    @class CoapTest
    """
    global target_file, coap_file
    CONST_PATH = os.path.dirname(os.path.realpath(__file__))
    target_file = os.path.join(CONST_PATH, 'files')
    coap_file = os.path.join(target_file, 'coap')
    def setUp(self):
        '''
        Copy coap.js and node module coap to target
        @fn setUp
        @param self
        @param return
        '''
        inst_cp_module_coap()
        if os.path.exists(os.path.join(target_file, 'node_modules')) and \
            os.path.exists(os.path.join(coap_file, 'coap.js')):
            oldscp = self.target.connection.scp[:]
            self.target.connection.scp.insert(1, '-r')
            self.target.copy_to(coap_file, '/tmp')
            self.target.copy_to(
                os.path.join(target_file, 'node_modules'),
                '/tmp'
                )
            self.target.connection.scp[:] = oldscp
        else:
            print("Please check there have files in coap and node_modules")
            sys.exit(1)

    def test_coap(self):
        '''
        Execute the tests and check the status
        @fn test_coap
        @param self
        @param return
        '''
        (status, output) =  self.target.run('node /tmp/coap/coap.js')
        self.assertEqual(status, 0)
        self.assertTrue('Hello Coap' in output)

    def tearDown(self):
        '''
        Clean up the test environment
        @fn tearDown
        @param self
        @param return
        '''
        os.system('rm -rf %s' % os.path.join(target_file, 'node_modules'))
        self.target.run('rm -rf /tmp/node_modules')
        self.target.run('rm -rf /tmp/coap')

