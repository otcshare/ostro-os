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
        enable_port_cmd = 'iptables -A INPUT -p tcp -dport 8000 -j ACCEPT'
        start_server_cmd = 'systemctl start iot-rest-api-server'
        self.target.run(enable_port_cmd)
        self.target.run(start_server_cmd)
        check_process_cmd = 'ps | grep "iot-rest-api-server" | grep -v grep | awk "{print $1}"'
        (status, output) = self.target.run(check_process_cmd)
        self.assertNotEqual(output, ' ', 'Can not start the iot-rest-api-server')
        (returncode, output) = self._run_curl_cmd()
        self.assertEqual(output.strip(), '200')
        stop_server_cmd = 'systemctl stop iot-rest-api-server'
        self.target.run(stop_server_cmd)

##
# @}
# @}
##

