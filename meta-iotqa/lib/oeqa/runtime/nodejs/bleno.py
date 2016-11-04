#!/usr/bin/env python3

import os
import sys
import time
import json
import shutil
import subprocess

from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag


class BlenoTest(oeRuntimeTest):
    
    cleanup = False
    bleno_prefix_dir = '/home/root'

    def setUp(self):
        '''
        Install bleno on the target device.
        '''
        self.clean_up_dirs()

        print('\nInstalling bleno on the target...')
        install_bleno_cmd = 'cd {prefix};npm install bleno'.format(
                            prefix = self.bleno_prefix_dir)
        (status, output) = self.target.run(install_bleno_cmd)
        if status != 0:
            sys.stderr.write('Failed to install bleno on the target device.')
            return
        print('Installing bleno on the target: done.')

        print('Installing bleno devDependencies for test...')
        npm_install_cmd = 'cd {prefix}/node_modules/bleno;npm install'.format(
                        prefix = self.bleno_prefix_dir)
        (status, output) = self.target.run(npm_install_cmd)
        if status != 0:
            sys.stderr.write('Failed to install bleno devDependencies for test.')
            return
        print('Installing bleno devDependencies for test: done.')

        update_mocha_test_cmd = 'cd {prefix}/node_modules/bleno;'.format(
                                prefix = self.bleno_prefix_dir)
        update_mocha_test_cmd += 'sed -i -e "s|-R spec test/\*.js|'
        update_mocha_test_cmd += '-R json test/\*.js > ../bleno.log|" package.json'
        print(update_mocha_test_cmd)

        self.target.run(update_mocha_test_cmd)


    @tag(CasesNumber = 23)
    def test_bleno(self):
        '''
        Run the bleno test cases on the target device.
        '''
        test_cmd = 'cd {prefix}/node_modules/bleno;npm test'.format(
                        prefix = self.bleno_prefix_dir)
        self.target.run(test_cmd)
        
        cat_bleno_log_cmd = 'cat {prefix}/node_modules/bleno.log'.format(
                                prefix = self.bleno_prefix_dir)
        (status, output) = self.target.run(cat_bleno_log_cmd)

        self.parse_bleno_test_log(output)


    def parse_bleno_test_log(self, output):
        '''
        Parse the json-formatted test results log. 
        '''
        try:
            result_json = json.loads(output.strip())
        except Exception:
            sys.stderr.write('Invalid JSON format results.')
            return

        with open('result-bleno.log', 'w') as fp:            
            for passed_tc in result_json.get('passes'):
                fp.write('{t} - runtest.py - RESULTS - ' \
                        'Testcase {tc_name}: {result}\n'.format(
                        t = time.strftime('%H:%M:%S', time.localtime()),
                        tc_name = '{tc}'.format(tc = passed_tc.get('fullTitle').replace(' ', '_')),
                        result = 'PASSED'))
            for failed_tc in result_json.get('failures'):
                fp.write('{t} - runtest.py - RESULTS - ' \
                        'Testcase {tc_name}: {result}\n'.format(
                        t = time.strftime('%H:%M:%S', time.localtime()),
                        tc_name = '{tc}'.format(tc = failed_tc.get('fullTitle').replace(' ', '_')),
                        result = 'FAILED'))
            

    def clean_up_dirs(self):
        '''
        Remove any bleno directory if it already exists on the target device.
        '''
        if self.cleanup:
            self.target.run('rm -fr ~/node_modules/bleno')


    def tearDown(self):
        '''
        Clean up work.
        '''
        self.clean_up_dirs();