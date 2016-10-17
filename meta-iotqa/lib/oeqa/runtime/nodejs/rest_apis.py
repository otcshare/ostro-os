# -*- coding:utf8 -*-

"""
@file rest_apis.py
"""

##
# @addtogroup nodejs nodejs
# @brief This is nodejs component
# @{
# @addtogroup rest_apis rest_apis
# @brief This is rest_apis module
# @{
##

__author__ = 'qiuzhong'
__version__ = '0.0.1'

import os
import subprocess
import sys
import shutil

from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag


@tag(TestType='FVT', FeatureID='IOTOS-343')
class RESTAPITest(oeRuntimeTest):
    '''
    The test case checks whether the REST APIs for Ostro OS works well.
    @class RESTAPITest
    '''
    rest_api = 'restapis'
    files_dir = None
    rest_api_dir = None
    target_rest_api_dir = '/tmp/%s' % rest_api
    nodeunit_zip = None
    rest_api_js_files = {

        'api_system': 'nodeunit_test_api_system.js',
        'api_oic_d': 'nodeunit_test_api_oic_d.js',
        'api_oic_p': 'nodeunit_test_api_oic_p.js',
        'api_oic_res': 'nodeunit_test_api_oic_res.js'

    }

    @classmethod
    def all_files_exists(cls):
        '''
        See wether all the files exists.
        :return:
        @fn all_files_exists
        @param cls
        @return
        '''
        for test_file in cls.rest_api_js_files.values():
            if not os.path.exists(os.path.join(os.path.dirname(__file__),
                                               'files', cls.rest_api,
                                               test_file)):
                return False
        return True

    @classmethod
    def node_module_path(cls):
        '''
        Install the module path via npm
        @fn node_module_path
        @param cls
        @return
        '''
        path_module_path = '/tmp/node_modules/path'
        if os.path.exists(path_module_path):
            shutil.rmtree(path_module_path)
        proc = subprocess.Popen(['npm', 'install', 'path'], cwd='/tmp/')
        proc.wait()
        if proc and proc.returncode == 0 and os.path.exists(path_module_path):
            oldscp = cls.tc.target.connection.scp[:]
            cls.tc.target.connection.scp.insert(1, '-r')
            cls.tc.target.run('cd /tmp; mkdir node_modules;')
            cls.tc.target.copy_to(
                path_module_path,
                '/tmp/node_modules'
                )
            cls.tc.target.connection.scp[:] = oldscp
        else:
            print ('Install node module path failed')
            sys.exit(1)


    @classmethod
    def setUpClass(cls):
        '''
        Copy all the JavaScript files to the target system.
        @fn setUpClass
        @param cls
        @return
        '''
        cls.files_dir = os.path.join(os.path.dirname(__file__), 'files')
        cls.rest_api_dir = os.path.join(os.path.dirname(__file__),
                                    'files', cls.rest_api).rstrip('/')

        cls.tc.target.run('rm -fr %s' % cls.target_rest_api_dir)
        cls.tc.target.run('rm -f %s.tar' % cls.target_rest_api_dir)

        if os.path.exists('%s.tar' % cls.rest_api_dir):
            os.remove('%s.tar' % cls.rest_api_dir)

        # compress restapi directory and copy it to target device.
        proc = None
        if cls.all_files_exists():
            proc = subprocess.Popen(
                ['tar', '-cf', '%s.tar' % cls.rest_api, cls.rest_api],
                cwd = cls.files_dir)
            proc.wait()

        if proc and proc.returncode == 0 and \
            os.path.exists('%s.tar' % cls.rest_api_dir):
            cls.tc.target.copy_to(
                os.path.join(
                    os.path.dirname(__file__),
                                    'files',
                                    '%s.tar' % cls.rest_api),
                '%s.tar' % cls.target_rest_api_dir)
            cls.tc.target.run('cd /tmp/; ' \
                            'tar -xf %s.tar -C %s/' % (
                                cls.target_rest_api_dir,
                                os.path.dirname(cls.target_rest_api_dir))
                            )

        # Install and copy the node module path to device
        cls.node_module_path()

        #Start the server iot-rest-api-server
        cls.tc.target.run('systemctl stop iot-rest-api-server.socket; systemctl stop iot-rest-api-server.service')
        check_process_cmd = 'ps | grep "/usr/lib/node_modules/iot-rest-api" | grep -v grep | awk "{print $4}"'
        (status, output) = cls.tc.target.run(check_process_cmd)
        if '/usr/lib/node_modules/iot-rest-api' not in output:
            cls.tc.target.run('systemctl start iot-rest-api-server.socket')
            (status, output) = cls.tc.target.run('unset http_proxy; curl http://%s:8000/api/oic/d' % (cls.tc.target.ip))
            (status, output) = cls.tc.target.run(check_process_cmd)
            if '/usr/lib/node_modules/iot-rest-api' not in output:
                print ("The iot-rest-api-server doesn't start!")
                sys.exit(1)

        # Download nodeunit from git hub
        proc = subprocess.Popen(['wget', 'https://github.com/caolan/nodeunit/archive/master.zip'],
                                cwd = cls.files_dir)
        proc.wait()

        cls.nodeunit_zip = os.path.join(os.path.dirname(__file__),
                                    'files',
                                    'master.zip')
        if os.path.exists(cls.nodeunit_zip):
            #change nodeunit zip to tar
            os.chdir(cls.files_dir)
            os.system('unzip -oq %s; cd nodeunit-master;npm install;cd ..;tar -cf master.tar nodeunit-master; rm -rf nodeunit-master' %\
                (cls.nodeunit_zip)
            )
            cls.nodeunit_tar = os.path.join(cls.files_dir, 'master.tar')
            cls.tc.target.copy_to(cls.nodeunit_tar, '/tmp/master.tar')
            cls.tc.target.run('cd /tmp/; ' \
                            'tar -xf master.tar;' \
                            'chmod +x /tmp/nodeunit-master/bin/nodeunit'
                           )

        cls.tc.target.run("/usr/sbin/iptables -w -A INPUT -p udp --dport 5683 -j ACCEPT")
        cls.tc.target.run('/opt/iotivity/examples/resource/c/SimpleClientServer/ocserver -o 0')
        for api, api_js in cls.rest_api_js_files.items():
            cls.tc.target.run('cd %s; node %s' % (cls.target_rest_api_dir, api_js) )


    def test_api_system_status_code(self):
        '''
        Test status code of response of  /api/system is 200
        @fn test_api_system_status_code
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemStatusCode' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_status_code
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_status_code
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_has_hostname(self):
        '''
        Test if the response of /api/system has hostname property.
        @fn test_api_system_has_hostname
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemHostnameNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_has_hostname
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_has_hostname
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_hostname_type(self):
        '''
        Test if type of hostname property in response is a string.
        @fn test_api_system_hostname_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemHostnameType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_hostname_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_hostname_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_hostname_value(self):
        '''
        Test if value of hostname property in response is OK.
        @fn test_api_system_hostname_value
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemHostnameValue' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_hostname_value
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_hostname_value
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_has_type(self):
        '''
        Test if the response of /api/system has type property.
        @fn test_api_system_has_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemTypeNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_has_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_has_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_type_type(self):
        '''
        Test if type of type property in response is a string.
        @fn test_api_system_type_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemTypeType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_type_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_type_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_type_value(self):
        '''
        Test if value of type property in response is OK.
        @fn test_api_system_type_value
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemTypeValue' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_type_value
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_type_value
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_has_arch(self):
        '''
        Test if the response of /api/system has arch property.
        @fn test_api_system_has_arch
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemArchNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_has_arch
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_has_arch
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_arch_type(self):
        '''
        Test if type of arch property in response is a string.
        @fn test_api_system_arch_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemArchType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_arch_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_arch_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_arch_value(self):
        '''
        Test if value of arch property in response is OK.
        @fn test_api_system_arch_value
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemArchValue' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_arch_value
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_arch_value
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_has_release(self):
        '''
        Test if the response of /api/system has release property.
        @fn test_api_system_has_release
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemReleaseNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_has_release
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_has_release
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_release_type(self):
        '''
        Test if type of release property in response is a string.
        @fn test_api_system_release_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemReleaseType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_release_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_release_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_release_value(self):
        '''
        Test if value of release property in response is OK.
        @fn test_api_system_release_value
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemReleaseValue' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_release_value
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_release_value
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_has_uptime(self):
        '''
        Test if the response of /api/system has uptime property.
        @fn test_api_system_has_uptime
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemUptimeNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_has_uptime
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_has_uptime
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_uptime_type(self):
        '''
        Test if type of uptime property in response is a number.
        @fn test_api_system_uptime_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemUptimeType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_uptime_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_uptime_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_has_loadavg(self):
        '''
        Test if the response of /api/system has loadavg property.
        @fn test_api_system_has_loadavg
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemLoadavgNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_has_loadavg
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_has_loadavg
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_loadavg_type(self):
        '''
        Test if type of loadavg property in response is an array.
        @fn test_api_system_loadavg_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemLoadavgType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_loadavg_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_loadavg_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_has_totalmem(self):
        '''
        Test if the response of /api/system has totalmem property.
        @fn test_api_system_has_totalmem
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemTotalmemNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_has_totalmem
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_has_totalmem
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_totalmem_type(self):
        '''
        Test if type of totalmem property in response is a string.
        @fn test_api_system_totalmem_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemTotalmemType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_totalmem_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_totalmem_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_totalmem_value(self):
        '''
        Test if value of totalmem property in response is OK.
        @fn test_api_system_totalmem_value
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemTotalmemValue' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_totalmem_value
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_totalmem_value
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_has_freemem(self):
        '''
        Test if the response of /api/system has freemem property.
        @fn test_api_system_has_freemem
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemFreememNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_has_freemem
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_has_freemem
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_freemem_type(self):
        '''
        Test if type of freemem property in response is a string.
        @fn test_api_system_freemem_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemFreememType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_freemem_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_freemem_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_has_cpus(self):
        '''
        Test if the response of /api/system has cpus property.
        @fn test_api_system_has_cpus
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemCpusNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_has_cpus
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_has_cpus
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_cpus_type(self):
        '''
        Test if type of cpus property in response is an array.
        @fn test_api_system_cpus_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemCpusType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_cpus_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_cpus_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_system_cpus_value(self):
        '''
        Test if value of cpus property in response is OK.
        @fn test_api_system_cpus_value
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemCpusValue' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_cpus_value
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_cpus_value
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])



    def test_api_system_networkinterfaces_value(self):
        '''
        Test if value of networkinterfaces property in response is OK.
        @fn test_api_system_networkinterfaces_value
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiSystemNetworkInterfacesValue' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_system']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_system_networkinterfaces_value
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_system_networkinterfaces_value
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_d_status_code(self):
        '''
        Test status code of response to /api/oic/d is 200
        @fn test_api_oic_d_status_code
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicDStatusCode' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_d']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_d_status_code
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_d_status_code
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_d_has_required_n(self):
        '''
        Test if the response of /api/oic/d has required property n.
        @fn test_api_oic_d_has_required_n
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicDRequiredNNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_d']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_d_has_required_n
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_d_has_required_n
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_d_required_n_type(self):
        '''
        Test if the type of n property in response is string.
        @fn test_api_oic_d_required_n_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicDRequiredNType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_d']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_d_required_n_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_d_required_n_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_d_has_required_di(self):
        '''
        Test if the response of /api/oic/d has required property di.
        @fn test_api_oic_d_has_required_di
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicDRequiredDiNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_d']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_d_has_required_di
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_d_has_required_di
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_d_required_di_type(self):
        '''
        Test if the type of di property in response is string.
        @fn test_api_oic_d_required_di_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicDRequiredDiType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_d']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_d_required_di_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_d_required_di_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_d_required_di_value_uuid(self):
        '''
        Test if the value of di property in response is UUID format.
        @fn test_api_oic_d_required_di_value_uuid
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicDRequiredDiUuid' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_d']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_d_required_di_value_uuid
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_d_required_di_value_uuid
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_d_has_required_icv(self):
        '''
        Test if the response of /api/oic/d has required property icv.
        @fn test_api_oic_d_has_required_icv
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicDRequiredIcvNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_d']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_d_has_required_icv
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_d_has_required_icv
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_d_required_icv_type(self):
        '''
        Test if the type of icv property in response is string.
        @fn test_api_oic_d_required_icv_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicRequiredDIcvType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_d']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_d_required_icv_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_d_required_icv_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_d_optional_dmv_type(self):
        '''
        Test if the type of dmv property (if it exists) in response is string.
        @fn test_api_oic_d_optional_dmv_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicDOptionalDmvType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_d']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_d_optional_dmv_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_d_optional_dmv_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])



    def test_api_oic_d_optional_dmv_value_csv(self):
        '''
        Test if the value of dmv property (if it exists) in response is csv format.
        @fn test_api_oic_d_optional_dmv_value_csv
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicDOptionalDmvCsv' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_d']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_d_optional_dmv_value_csv
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_d_optional_dmv_value_csv
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_status_code(self):
        '''
        Test status code of /api/oic/p.
        @fn test_api_oic_p_status_code
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPStatusCode' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_status_code
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_status_code
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_has_required_pi(self):
        '''
        Test if the response of /api/oic/pi has required property pi.
        @fn test_api_oic_p_has_required_pi
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPRequiredPiNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_has_required_pi
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_has_required_pi
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_required_pi_type(self):
        '''
        Test if the type of pi property in response is string.
        @fn test_api_oic_p_required_pi_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPRequiredPiType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_required_pi_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_required_pi_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_has_required_mnmn(self):
        '''
        Test if the response of /api/oic/p has required property mnmn.
        @fn test_api_oic_p_has_required_mnmn
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPRequiredMnmnNotNull' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_has_required_mnmn
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_has_required_mnmn
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_required_mnmn_type(self):
        '''
        Test if the type of mnmn property in response is string.
        @fn test_api_oic_p_required_mnmn_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPRequiredMnmnType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_required_mnmn_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_required_mnmn_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_optional_mnml_type(self):
        '''
        Test if the type of mnml property in response is string.
        @fn test_api_oic_p_optional_mnml_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPOptionalMnmlType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_optional_mnml_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_optional_mnml_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_optional_mnmo_type(self):
        '''
        Test if the type of mnmo property in response is string.
        @fn test_api_oic_p_optional_mnmo_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPOptionalMnmoType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_optional_mnmo_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_optional_mnmo_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_optional_mndt_type(self):
        '''
        Test if the type of mndt property in response is string.
        @fn test_api_oic_p_optional_mndt_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPOptionalMndtType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_optional_mndt_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_optional_mndt_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_optional_mnpv_type(self):
        '''
        Test if the type of mnpv property in response is string.
        @fn test_api_oic_p_optional_mnpv_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPOptionalMnpvType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_optional_mnpv_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_optional_mnpv_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_optional_mnos_type(self):
        '''
        Test if the type of mnos property in response is string.
        @fn test_api_oic_p_optional_mnos_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPOptionalMnosType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_optional_mnos_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_optional_mnos_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_optional_mnhw_type(self):
        '''
        Test if the type of mnhw property in response is string.
        @fn test_api_oic_p_optional_mnhw_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPOptionalMnhwType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_optional_mnhw_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_optional_mnhw_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_optional_mnfv_type(self):
        '''
        Test if the type of mnfv property in response is string.
        @fn test_api_oic_p_optional_mnfv_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPOptionalMnfvType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_optional_mnfv_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_optional_mnfv_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_optional_mnsl_type(self):
        '''
        Test if the type of mnfv property in response is string.
        @fn test_api_oic_p_optional_mnsl_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPOptionalMnslType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_optional_mnsl_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_optional_mnsl_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_p_optional_st_type(self):
        '''
        Test if the type of st property in response is string.
        @fn test_api_oic_p_optional_st_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicPOptionalStType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_p']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_p_optional_st_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_p_optional_st_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_res_status_code(self):
        '''
        Test status code of /api/oic/res.
        @fn test_api_oic_res_status_code
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicResStatusCode' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_res']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_res_status_code
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_res_status_code
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_res_n_type(self):
        '''
        Test if the type of n property (if it exists) in response is string.
        @fn test_api_oic_res_n_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicResNType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_res']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_res_n_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_res_n_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_res_di_type(self):
        '''
        Test if the type of di property (if it exists) in response is string.
        @fn test_api_oic_res_di_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicResDiType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_res']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_res_di_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_res_di_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_res_di_value_uuid(self):
        '''
        Test if the value of di property (if it exists) in response is UUID format.
        @fn test_api_oic_res_di_value_uuid
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicResDiUuid' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_res']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_res_di_value_uuid
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_res_di_value_uuid
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_api_oic_res_links_type(self):
        '''
        Test if the type of links property (if it exists) in response is an array.
        @fn test_api_oic_res_links_type
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testApiOicResLinksType' % (
                    self.target_rest_api_dir,
                    self.target_rest_api_dir,
                    self.rest_api_js_files['api_oic_res']
                   )
        )
        ##
        # TESTPOINT: #1, test_api_oic_res_links_type
        #
        self.assertEqual(api_status, 0)
        ##
        # TESTPOINT: #2, test_api_oic_res_links_type
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    @classmethod
    def tearDownClass(cls):
        '''
        Clean work.
        Clean all the files and directories that the tests may be used on target.
        @fn tearDownClass
        @param cls
        @return
        '''
        (_, pid) = cls.tc.target.run("ps | grep -v grep | grep 'ocserver' | awk '{print $1}'")
        cls.tc.target.run('kill -9 %s' % pid.strip());
        stop_server_cmd = 'systemctl stop iot-rest-api-server.socket; systemctl stop iot-rest-api-server.service'
        cls.tc.target.run(stop_server_cmd)
        if os.path.exists('%s.tar' % cls.rest_api_dir):
            os.remove('%s.tar' % cls.rest_api_dir)
        if os.path.exists(cls.nodeunit_zip):
            os.remove(cls.nodeunit_zip)
        os.system('rm -rf %s/master.*' % cls.files_dir)

        cls.tc.target.run('rm -f %s.tar' % cls.target_rest_api_dir)
        cls.tc.target.run('rm -fr %s/' % cls.target_rest_api_dir)
        cls.tc.target.run('rm -fr /tmp/nodeunit-master')
        cls.tc.target.run('rm -f /tmp/master.tar')
        cls.tc.target.run('rm -rf /tmp/modules')

        cls.tc.target.run("/usr/sbin/iptables -w -D INPUT -p udp --dport 5683 -j ACCEPT")

##
# @}
# @}
##

