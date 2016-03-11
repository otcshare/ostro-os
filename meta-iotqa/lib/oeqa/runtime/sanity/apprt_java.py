"""
@file apprt_java.py
"""

##
# @addtogroup sanity sanity
# @brief This is sanity component
# @{
# @addtogroup apprt_java apprt_java
# @brief This is apprt_java module
# @{
##

import os
import re
from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag

@tag(FeatureID="IOTOS-356", TestType="FVT")
class SanityTestJava(oeRuntimeTest):
    """
    @class SanityTestJava
    """
    
    apprt_test_java_helloworld = "AppRtTestJavaHelloWorld"
    apprt_test_java_helloworld_class = '%s.class' % apprt_test_java_helloworld
    apprt_test_java_helloworld_target = '/tmp/%s' % \
                                        apprt_test_java_helloworld_class

    apprt_test_java_x11_disabled = "AppRtTestJavaX11Disabled"
    apprt_test_java_x11_disabled_class = '%s.class' % apprt_test_java_x11_disabled
    apprt_test_java_x11_disabled_target = '/tmp/%s' % \
                                        apprt_test_java_x11_disabled_class

    def setUp(self):
        '''
        Copy all necessary files for test to the target device. 
        @fn setUp
        @param self
        @return
        '''
        self.target.copy_to(
            os.path.join(
                os.path.dirname(__file__),
                'files',
                SanityTestJava.apprt_test_java_helloworld_class),
            SanityTestJava.apprt_test_java_helloworld_target)        

        self.target.copy_to(
            os.path.join(
                os.path.dirname(__file__),
                'files',
                SanityTestJava.apprt_test_java_x11_disabled_class),
            SanityTestJava.apprt_test_java_x11_disabled_target)

    def test_java_exists(self):
        '''
        Test if the java executable is installed and in PATH.
        @fn test_java_exists
        @param self
        @return
        '''
        (status, _) = self.target.run('which java')
        ##
        # TESTPOINT: #1, test_java_exists
        #
        self.assertEqual(
            status,
            0,
            msg='java binary not in PATH or on target.')


    def test_java_version(self):
        '''
        Test if the version of Java is OK.
        The expected version of Java must be greater than or equal to 1.8
        @fn test_java_version
        @param self
        @return
        '''
        (status, output) = self.target.run('java -version')
        ##
        # TESTPOINT: #1, test_java_version
        #
        self.assertEqual(
            status,
            0,
            msg = 'V option for java command is invalid or '\
                    'java binary does not work.')

        ver = re.split('\s+', output.strip())[2]
        (major, minor, _) = re.split('\.', ver.strip())
        ##
        # TESTPOINT: #2, test_java_version
        #
        self.assertTrue(
            (major > 1) or (
                major == 1 and minor >= 8),
            msg='Java version is lower than 1.8!')


    def test_java_helloworld(self):
        '''
        Test if the simple hello world program of Java works well.
        @fn test_java_helloworld
        @param self
        @return
        '''
        (status, output) = self.target.run('java -classpath /tmp/ %s' %
                    SanityTestJava.apprt_test_java_helloworld)
        ##
        # TESTPOINT: #1, test_java_helloworld
        #
        self.assertEqual(
            status,
            0,
            msg='Exit status was not 0. Output: %s' %
            output)
        ##
        # TESTPOINT: #2, test_java_helloworld
        #
        self.assertEqual(
            output,
            'Hello World!',
            msg='Incorrect output: %s' %
            output)

    def test_java_x11_disabled(self):
        '''
        Test that X11 is not enabled.
        @fn test_java_x11_disabled
        @param self
        @return
        '''
        (status, output) = self.target.run('java -classpath /tmp/ %s' %
                    SanityTestJava.apprt_test_java_x11_disabled)
        ##
        # TESTPOINT: #1, test_java_x11_disabled
        #
        self.assertEqual(
            status,
            0,
            msg='Exit status was not 0. Output: %s' %
            output)
        ##
        # TESTPOINT: #2, test_java_x11_disabled
        #
        self.assertEqual(
            output,
            'OK!',
            msg='Incorrect output: %s' %
            output)

    def tearDown(self):
        '''
        Clean work: remove all the files copied to the target device.
        @fn tearDown
        @param self
        @return
        '''
        self.target.run(
            'rm -f %s %s' %
            (SanityTestJava.apprt_test_java_helloworld_target,
             SanityTestJava.apprt_test_java_x11_disabled_target))

##
# @}
# @}
##

