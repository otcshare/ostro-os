"""
@file iotivity_js_apis.py
"""

##
# @addtogroup nodejs nodejs
# @brief This is nodejs component
# @{
# @addtogroup iotivity_js_apis iotivity_js_apis
# @brief This is iotivity_js_apis module
# @{
##

import os
import subprocess

from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag


@tag(TestType='FVT', FeatureID='IOTOS-764')
class IotivityJSAPITest(oeRuntimeTest):
    '''
    The test suite checks whether the iotivity node binding APIs work well.
    @class IotivityJSAPITest
    '''

    iotivity_js_apis = 'iotivityjsapis'
    files_dir = os.path.join(os.path.dirname(__file__),
                            'files')
    iotivity_js_apis_dir = os.path.join(files_dir,
                            iotivity_js_apis
                            )
    nodeunit_zip = os.path.join(files_dir, 'master.zip')
    target_iotivity_js_apis_dir = '/tmp/%s' % iotivity_js_apis
    iotivity_js_apis_files = {
        'oic_device': 'test_oic_device.js',
        'oic_client': 'test_oic_client.js',
        'oic_server': 'test_oic_server.js',
        'oic_resource': 'test_oic_resource.js',
        'oic_discovery': 'test_oic_discovery.js',
        'oic_platform': 'test_oic_platform.js'
    }
    timeout = 20


    @classmethod
    def all_files_exist(cls):
        '''
        Check if all the files exists.
        :return:
        @fn all_files_exist
        @param cls
        @return
        '''
        for test_file in cls.iotivity_js_apis_files.values():
            if not os.path.exists(os.path.join(os.path.dirname(__file__),
                                               'files',
                                               cls.iotivity_js_apis_dir,
                                               test_file)):
                return False
        return True



    @classmethod
    def setUpClass(cls):
        '''
        Copy all the JavaScript files to the target system.
        @fn setUpClass
        @param cls
        @return
        '''
        cls.tc.target.run('rm -fr %s' % cls.target_iotivity_js_apis_dir)
        cls.tc.target.run('rm -f %s.tar' % cls.target_iotivity_js_apis_dir)

        if os.path.exists('%s.tar' % cls.iotivity_js_apis_dir):
            os.remove('%s.tar' % cls.iotivity_js_apis_dir)

        # compress iotivity javascript api directory and copy it to target device.
        proc = None
        if cls.all_files_exist():
            proc = subprocess.Popen(
                ['tar', '-cf', '%s.tar' % cls.iotivity_js_apis, cls.iotivity_js_apis],
                cwd = cls.files_dir)
            proc.wait()

        if proc and proc.returncode == 0 and \
            os.path.exists('%s.tar' % cls.iotivity_js_apis_dir):
            cls.tc.target.copy_to(
                os.path.join(
                    os.path.dirname(__file__),
                                    'files',
                                    '%s.tar' % cls.iotivity_js_apis_dir),
                '%s.tar' % cls.target_iotivity_js_apis_dir)
            cls.tc.target.run('cd /tmp/; ' \
                            'tar -xf %s.tar -C %s/' % (
                                cls.target_iotivity_js_apis_dir,
                                os.path.dirname(cls.target_iotivity_js_apis_dir))
                            )


        if not os.path.exists('/tmp/master.zip'):
            proc = subprocess.Popen(['wget', 'https://github.com/caolan/nodeunit/archive/master.zip'],
                                cwd = cls.files_dir)
            proc.wait()
        else:
            os.system('cp -f /tmp/master.zip %s' % (cls.nodeunit_zip))

        if os.path.exists(cls.nodeunit_zip):
            #change nodeunit zip package to tar package
            os.chdir(cls.files_dir)
            os.system('unzip -oq %s; tar -cf master.tar nodeunit-master; rm -rf nodeunit-master' % cls.nodeunit_zip)
            cls.nodeunit_tar = os.path.join(cls.files_dir, 'master.tar')
            cls.tc.target.copy_to(cls.nodeunit_tar, '/tmp/master.tar')
            cls.tc.target.run('cd /tmp/; ' \
                            'tar -xf master.tar;' \
                            'chmod +x /tmp/nodeunit-master/bin/nodeunit'
                           )


    def test_oic_device_attr_uuid(self):
        '''
        Test if OicDevice object has uuid attribute.
        @fn test_oic_device_attr_uuid
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDeviceAttrUuid' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_device']
                   ), self.timeout
        )
        ##
        # TESTPOINT: #1, test_oic_device_attr_uuid
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_device_attr_url(self):
        '''
        Test if OicDevice.settings has url member.
        @fn test_oic_device_attr_url
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDeviceAttrUrl' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_device']
                   ), self.timeout
        )
        ##
        # TESTPOINT: #1, test_oic_device_attr_url
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_device_attr_name(self):
        '''
        Test if OicDevice.settings has info member.
        @fn test_oic_device_attr_name
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDeviceAttrName' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_device']
                   ), self.timeout
        )
        ##
        # TESTPOINT: #1, test_oic_device_attr_name
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_device_attr_dataModels(self):
        '''
        Test if OicDevice.settings has role member.
        @fn test_oic_device_attr_dataModels
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDeviceAttrDataModels' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_device']
                   ), self.timeout
        )
        ##
        # TESTPOINT: #1, test_oic_device_attr_dataModels
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_device_attr_coreSpecVersion(self):
        '''
        Test if OicDevice.settings has connectionMode member.
        @fn test_oic_device_attr_coreSpecVersion
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDeviceAttrCoreSpecVersion' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_device']
                   ), self.timeout
        )
        ##
        # TESTPOINT: #1, test_oic_device_attr_coreSpecVersion
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_device_attr_role(self):
        '''
        Test if OicDevice.settings.info has uuid member.
        @fn test_oic_device_attr_role
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDeviceAttrRole' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_device']
                   ), self.timeout
        )
        ##
        # TESTPOINT: #1, test_oic_device_attr_role
        #
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

# OicClient
    def test_oic_client_attr_create(self):
        '''
        Test if OicClient has create promise function.
        @fn test_oic_client_attr_create
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicClientRetrievePromise' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_client']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_client_attr_retrieve(self):
        '''
        Test if OicClient has retrieve promise function.
        @fn test_oic_client_attr_retrieve
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicClientUpdatePromise' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_client']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_client_attr_update(self):
        '''
        Test if OicClient has update promise function.
        @fn test_oic_client_attr_update
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicClientDeletePromise' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_client']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_client_attr_delete(self):
        '''
        Test if OicClient has delete promise function.
        @fn test_oic_client_attr_delete
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicClientHasRetrieveResourcePromise' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_client']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


# OicServer
    def test_oic_server_has_registerResource_promise(self):
        '''
        Test if OicClient has registerResource promise function.
        @fn test_oic_server_has_registerResource_promise
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicServerHasRegisterResourcePromise' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_server']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_server_has_unregisterResource_promise(self):
        '''
        Test if OicClient has unregisterResource promise function.
        @fn test_oic_server_has_unregisterResource_promise
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicServerHasUnregisterResourcePromise' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_server']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_server_has_enablePresence_promise(self):
        '''
        Test if OicClient has enablePresence promise function.
        @fn test_oic_server_has_enablePresence_promise
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicServerHasEnablePresencePromise' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_server']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_server_has_disablePresence_promise(self):
        '''
        Test if OicClient has disablePresence promise function.
        @fn test_oic_server_has_disablePresence_promise
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicServerHasDisablePresencePromise' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_server']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_server_has_notify_promise(self):
        '''
        Test if OicClient has notify promise function.
        @fn test_oic_server_has_notify_promise
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicServerHasNotifyPromise' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_server']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_server_has_onobserverequest_promise(self):
        '''
        Test if OicClient has onobserverequest event.
        @fn test_oic_server_has_onobserverequest_promise
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicServerHasOnobserverequestEvent' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_server']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_server_has_onunobserverequest_promise(self):
        '''
        Test if OicClient has onunobserverequest event.
        @fn test_oic_server_has_onunobserverequest_promise
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicServerHasOnunobserverequestEvent' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_server']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_server_has_onretrieverequest_promise(self):
        '''
        Test if OicClient has onretrieverequest event.
        @fn test_oic_server_has_onretrieverequest_promise
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicServerHasOnretrieverequestEvent' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_server']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_server_has_ondeleterequest_promise(self):
        '''
        Test if OicClient has ondeleterequest event.
        @fn test_oic_server_has_ondeleterequest_promise
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicServerHasOndeleterequestEvent' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_server']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_server_has_onupdaterequest_promise(self):
        '''
        Test if OicClient has onupdaterequest event.
        @fn test_oic_server_has_onupdaterequest_promise
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicServerHasOnupdaterequestEvent' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_server']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


    def test_oic_server_has_oncreaterequest_promise(self):
        '''
        Test if OicClient has oncreaterequest event.
        @fn test_oic_server_has_oncreaterequest_promise
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicServerHasOncreaterequestEvent' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_server']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])


# OicResource
    def test_oic_resource_has_addEventListener(self):
        '''
        Test if OicResource has addEventListener member.
        @fn test_oic_resource_has_addEventListener
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicResourceHasaddEventListener' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_resource']
                   )
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_oic_resource_has_removeEventListener(self):
        '''
        Test if OicResource has removeEventListener member.
        @fn test_oic_resource_has_removeEventListener
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicResourceHasremoveEventListener' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_resource']
                   )
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])


    def test_oic_resource_has_dispatchEvent(self):
        '''
        Test if OicResource has dispatchEvent member.
        @fn test_oic_resource_has_dispatchEvent
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicResourceHasdispatchEvent' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_resource']
                   )
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-1])

#oicDiscovery
    def test_oic_discovery_findResources(self):
        '''
        Test if oicDiscovery has findResources member.
        @fn test_oic_discovery_findResources
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDiscoveryAttrFindResources' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_discovery']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_discovery_getDeviceInfo(self):
        '''
        Test if oicDiscovery has getDeviceInfo member.
        @fn test_oic_discovery_getDeviceInfo
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDiscoveryAttrGetDeviceInfo' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_discovery']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_discovery_getPlatformInfo(self):
        '''
        Test if oicDiscovery has getPlatformInfo member.
        @fn test_oic_discovery_getPlatformInfo
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDiscoveryAttrGetPlatformInfo' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_discovery']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_discovery_findDevices(self):
        '''
        Test if oicDiscovery has findDevices member.
        @fn test_oic_discovery_findDevices
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDiscoveryAttrFindDevices' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_discovery']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_discovery_onresourcefound(self):
        '''
        Test if oicDiscovery has onresourcefound member.
        @fn test_oic_discovery_onresourcefound
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDiscoveryAttrOnresourcefound' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_discovery']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_discovery_ondevicefound(self):
        '''
        Test if oicDiscovery has ondevicefound member.
        @fn test_oic_discovery_ondevicefound
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDiscoveryAttrOndevicefound' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_discovery']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_discovery_ondiscoveryerror(self):
        '''
        Test if oicDiscovery has ondiscoveryerror member.
        @fn test_oic_discovery_ondiscoveryerror
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicDiscoveryAttrOndiscoveryerror' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_discovery']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

#OicPlatform

    def test_oic_platform_id(self):
        '''
        Test if oicPlatform has id member.
        @fn test_oic_platform_id
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicPlatformAttrId' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_platform']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_platform_osVersion(self):
        '''
        Test if oicPlatform has osVersion member.
        @fn test_oic_platform_osVersion
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicPlatformAttrOsVersion' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_platform']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_platform_model(self):
        '''
        Test if oicPlatform has model member.
        @fn test_oic_platform_model
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicPlatformAttrModel' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_platform']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_platform_manufacturerName(self):
        '''
        Test if oicPlatform has manufacturerName member.
        @fn test_oic_platform_manufacturerName
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicPlatformAttrManufacturerName' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_platform']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_platform_manufacturerUrl(self):
        '''
        Test if oicPlatform has manufacturerUrl member.
        @fn test_oic_platform_manufacturerUrl
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicPlatformAttrManufacturerUrl' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_platform']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_platform_manufactureDate(self):
        '''
        Test if oicPlatform has manufactureDate member.
        @fn test_oic_platform_manufactureDate
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicPlatformAttrManufactureDate' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_platform']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_platform_platformVersion(self):
        '''
        Test if oicPlatform has platformVersion member.
        @fn test_oic_platform_platformVersion
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicPlatformAttrPlatformVersion' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_platform']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_platform_firmwareVersion(self):
        '''
        Test if oicPlatform has firmwareVersion member.
        @fn test_oic_platform_firmwareVersion
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicPlatformAttrFirmwareVersion' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_platform']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def test_oic_platform_supportUrl(self):
        '''
        Test if oicPlatform has supportUrl member.
        @fn test_oic_platform_supportUrl
        @param self
        @return
        '''
        (api_status, api_output) = self.target.run(
                'export NODE_PATH="/usr/lib/node_modules/"; cd %s/; /tmp/nodeunit-master/bin/nodeunit %s/%s -t testOicPlatformAttrSupportUrl' % (
                    self.target_iotivity_js_apis_dir,
                    self.target_iotivity_js_apis_dir,
                    self.iotivity_js_apis_files['oic_platform']
                   ), self.timeout
        )
        self.assertTrue('OK:' in api_output.strip().splitlines()[-3])

    def tearDown(self):
        '''
        Kill the process after running test
        @fn setUp
        @param self
        @return
        '''
        self.target.run("kill -9 `ps | grep '%s' | grep -v 'grep' | awk '{print $1}'`" %
            "/tmp/nodeunit-master/bin/nodeunit"
            )
        self.target.run("kill -9 `ps | grep '%s' | grep -v 'grep' | awk '{print $1}'`" %
            "iotivityjsapis"
            )

    @classmethod
    def tearDownClass(cls):
        '''
        Clean work.
        Clean all the files and directories that the tests may be used on target.
        @fn tearDownClass
        @param cls
        @return
        '''
        if os.path.exists('%s.tar' % cls.iotivity_js_apis_dir):
            os.remove('%s.tar' % cls.iotivity_js_apis_dir)
        os.system('rm -rf %s' % cls.nodeunit_tar)
        if os.path.exists(cls.nodeunit_zip) and not os.path.exists('/tmp/master.zip'):
            os.system('mv -f %s /tmp/' % (cls.nodeunit_zip))

        cls.tc.target.run('rm -f %s.tar' % cls.target_iotivity_js_apis_dir)
        cls.tc.target.run('rm -fr %s/' % cls.target_iotivity_js_apis_dir)
        cls.tc.target.run('rm -fr /tmp/nodeunit-master')
        cls.tc.target.run('rm -f /tmp/master.zip')


##
# @}
# @}
##

