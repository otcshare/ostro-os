#!/usr/bin/env python3


import os
import sys
import subprocess
import shutil
import time

from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag


class NodeJSCryptoAPITest(oeRuntimeTest):

    DEFAULT_NODEJS_VERSION = 'v4.5.0'
    NODEJS_ARCHIVE_URL = 'https://github.com/nodejs/node/archive/{ver}.tar.gz'
    apprt_files_dir = os.path.join(os.path.dirname(__file__), 
                                    'files', 
                                    'noderuntime')
    node_version = None
    crypto_api_tc_list_file = os.path.join(apprt_files_dir, 
                                    'crypto_api_tc_list')
    results = {} 


    def setUp(self):
        '''
        Setup before running the test cases.
        '''        
        print('\nDetecting node version of the target...')
        self.get_target_nodejs_ver()
        print('Node version of target is ' + self.node_version)
        
        self.clean_up_dirs()
        
        print('Downloading node archive from github...')
        self.get_nodejs_archive()
        print('Downloading node archive done.')

        print('Scp test cases to the target...')
        self.scp_test_to_target()
        print('Scp test cases to the target done.')


    def clean_up_dirs(self):
        '''
        Remove /tmp/node-{version} on host and test on target device.
        '''
        tmp_node_dir = '/tmp/node-{ver}'.format(
                        ver = self.node_version.lstrip('v'))
        if os.path.exists(tmp_node_dir):
            shutil.rmtree(tmp_node_dir)        
        self.target.run('rm -fr ~/test')


    @tag(CasesNumber = 32)
    def get_target_nodejs_ver(self):
        '''
        Detect the NodeJS version on the target device.
        '''
        (status, output) = self.target.run('node -v')
        if status != 0:
            print('Executing node -v error, use default node version:' \
                    ' {ver}!\n'.format(ver = DEFAULT_NODEJS_VERSION))
            self.node_version = DEFAULT_NODEJS_VERSION
        else:
            self.node_version = output.strip()

    
    def get_nodejs_archive(self):
        '''
        Download the nodejs archive from github.com and uncompress it.
        '''
        node_archive_name = '{ver}.tar.gz'.format(ver = self.node_version)
        dl_cmd = ['wget', self.NODEJS_ARCHIVE_URL.format(
                                                ver = self.node_version)]
        tmp_node_archive = os.path.join('/tmp', node_archive_name)

        if not os.path.exists(tmp_node_archive):
            p = subprocess.Popen(dl_cmd,
                                 stdout = subprocess.PIPE, 
                                 stderr = subprocess.STDOUT,
                                 cwd = self.apprt_files_dir)
            p.wait()
            if p.returncode == 0:
                shutil.move(os.path.join(self.apprt_files_dir, 
                                        node_archive_name), 
                            tmp_node_archive)

        unzip_cmd = ['tar', '-xf', tmp_node_archive, '-C', '/tmp']
        p = subprocess.Popen(unzip_cmd,
                            stdout = subprocess.PIPE,
                            stderr = subprocess.STDOUT)
        p.wait()
        if p.returncode != 0:
            return False

        return True
            

    def scp_test_to_target(self):
        '''
        Scp the nodejs/test directory to the target device.
        '''
        scp_cmd = ['scp', '-r', '/tmp/node-{ver}/test'.format(
                    ver = self.node_version.lstrip('v')), 
                    'root@{ip}:~/'.format(ip = self.target.ip)]
        print(scp_cmd)
        p = subprocess.Popen(scp_cmd, 
                            stdout = subprocess.PIPE, 
                            stderr = subprocess.STDOUT)
        p.wait()
        if p.returncode != 0:
            return False

        return True


    def test_crypto_api(self):
        '''
        Run all the Crypto API test cases based on the list in 
        '''
        with open(self.crypto_api_tc_list_file) as f:
            crypto_api_tc_list = f.readlines()

        results = {}
        print('Running Crypto test cases...')
        for tc in crypto_api_tc_list:
            tc = tc.strip()
            if tc.startswith('#'):
                continue

            if os.path.exists(os.path.join('/tmp/node-{ver}/test/{tc}'.format(
                ver = self.node_version.lstrip('v'), tc = tc))):
                print(tc + '...', end = '')
                target_cmd = 'node ~/test/{testcase}'.format(testcase = tc)                
                (status, output) = self.target.run(target_cmd, 3600)
                if status == 0:
                    self.results[tc] = True
                    print('ok')
                elif status == 143:
                    self.results[tc] = 'Block'
                    print('block')
                else:
                    self.results[tc] = False
                    print('nok')
            else:
                print(tc + ' does not exist in node {ver}'.format(
                                                    ver = self.node_version))

        self.gen_crypto_result_log()


    def gen_crypto_result_log(self):
        '''
        Generate the formatted log for Crypto API tests.
        '''
        if not self.results:
            return
        
        with open('result-crypto-api.log', 'w') as fp:
            for tc, result in self.results.items():
                if result:
                    if not isinstance(result, str):
                        tc_result = 'PASSED'
                else:
                    tc_result = 'FAILED'
                    
                fp.write('{t} - runtest.py - RESULTS - ' \
                        'Testcase {tc_name}: {result}\n'.format(
                        t = time.strftime('%H:%M:%S', time.localtime()),
                        tc_name = os.path.splitext(tc)[0].replace('/', '.'),
                        result = tc_result))
            
 
    def tearDown(self):
        '''
        Clean up work.
        '''
        self.clean_up_dirs()
