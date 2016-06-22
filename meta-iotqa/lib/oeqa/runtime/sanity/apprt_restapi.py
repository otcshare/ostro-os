"""
@file apprt_restapi.py
"""

##
# @addtogroup sanity sanity
# @brief This is sanity component
# @{
# @addtogroup apprt_restapi apprt_restapi
# @brief This is apprt_restapi module
# @{
##

import subprocess
from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag

@tag(TestType='FVT', FeatureID='IOTOS-343')
class SanityTestRestApi(oeRuntimeTest):
    """
    @class SanityTestRestApi
    """

    def _run_curl_cmd(self):

        curl_cmd = ''.join([
                   'unset http_proxy; curl --noproxy "*" -s -o',
                   ' /dev/null -w %{http_code}',
                   ' --no-buffer http://%s:8000/api/oic/d' % (self.target.ip)])
        p = subprocess.Popen(curl_cmd,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT, shell=True)
        p.wait()
        ret = p.returncode
        output = p.stdout.read()
        return (ret, output)


    def test_restapi_available_by_remote(self):
        '''
        Send a HTTP request to the REST API server and see if 200 is returned.
        '''
        self.target.run('systemctl stop iot-rest-api-server.socket; systemctl stop iot-rest-api-server.service')
        check_process_cmd = 'ps | grep "/usr/lib/node_modules/iot-rest-api" | grep -v grep | awk "{print $4}"'
        (status, output) = self.target.run(check_process_cmd)
        if '/usr/lib/node_modules/iot-rest-api' not in output:
            self.target.run('systemctl start iot-rest-api-server.socket')
            (returncode, output) = self._run_curl_cmd()
            (status, output) = self.target.run(check_process_cmd)
            self.assertTrue('/usr/lib/node_modules/iot-rest-api' in output)
        (returncode, output) = self._run_curl_cmd()
        self.assertEqual(output.strip(), '200')


    def tearDown(self):
        stop_server_cmd = 'systemctl stop iot-rest-api-server.socket; systemctl stop iot-rest-api-server.service'
        self.target.run(stop_server_cmd)

##
# @}
# @}
##

