from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag
import time,json

class App(object):
    def __init__(self,target):
        self.target = target

    def getProcessInfo(self,keyword):
        ''' get info of process '''
        if len(keyword) > 8:
            keyword = keyword[:8]
        (status,output) = self.target.run(" ps axo pid,user:20,comm | grep -v grep | grep %s | head -n 1" % keyword)
        if 'invalid option' in output :
            (status,output) = self.target.run(" ps | grep -v grep | grep %s | head -n 1" % keyword)
            if status == 0 and output.strip():
                return output
            else:
                return None
        else:
            return output

    def getProcessPID(self,keyword):
        ''' get PID of process '''
        info = self.getProcessInfo(keyword)
        if info:
            return info.split()[0]
        else:
            return None   
          
        
    def startApp(self,service_name):
        ''' start app '''
        (status,output) = self.target.run("systemctl start %s" % service_name)
        time.sleep(3)
        if status != 0 :
            return False
        (status,output) = self.target.run("machinectl -l")
        if status == 0 and service_name in output :
            pass
        else:
            return False
        PID = self.getProcessPID(service_name)
        if PID :
            return True 
        else:
            return False 
        
    def stopApp(self,service_name):
        ''' stop app '''
        PID = self.getProcessPID(service_name)
        if not PID:
            return False 
        (status,output) = self.target.run("systemctl stop %s" % service_name)
        time.sleep(3)
        if status != 0 :
            return False
        (status,output) = self.target.run("machinectl -l")
        if status == 0 and service_name not in output :
            pass
        else:
            return False
        PID = self.getProcessPID(service_name)
        if not PID:
            return True
        else:
            return False
        
class AppFWTest(oeRuntimeTest):

    node_app_name = 'iodine-nodetest'
    node_app_manifest = '/apps/iodine/nodetest/manifest'

    def setUp(self):
        self.app = App(self.target)
    
    def _getProcessInfo(self,name):
        ''' get username,pid and exec command of process '''
        return self.app.getProcessInfo(name)

    def _startApp(self,name):
        ''' start app '''
        self.assertTrue(self.app.startApp(name),'Fail to start app')
        
    def _stopApp(self,name):
        ''' stop app '''
        self.assertTrue(self.app.stopApp(name),'Fail to stop app')

    def _getAppManifest(self):
        ''' get App manifest '''       
        (status,output) = self.target.run("cat %s " % self.node_app_manifest)
        if output : 
            return json.loads(output)
        else:
            return None

    @tag(TestType = 'FVT', FeatureID = 'IOTOS-337')
    def test_appFW_install_pkg_during_img_creation(self):
        '''check app is pre-installed'''
        (chk_example_app,output) = self.target.run("ls /apps/iodine/nodetest/")
        self.assertTrue(chk_example_app == 0 ,
                        "example-app is not integreated in image")
        
    @tag(TestType = 'FVT', FeatureID = 'IOTOS-337')
    def test_appFW_app_start(self):
        ''' Check app start successfully '''
        self._startApp(self.node_app_name)

    @tag(TestType = 'FVT', FeatureID = 'IOTOS-337')
    def test_appFW_app_stop(self):
        ''' Check app stop successfully '''
        self._startApp(self.node_app_name)
        self._stopApp(self.node_app_name)

    @tag(TestType = 'FVT', FeatureID = 'IOTOS-337')
    def test_appFW_app_restart(self):
        ''' Check app restart successfully '''
        self._startApp(self.node_app_name)
        self._stopApp(self.node_app_name)
        self._startApp(self.node_app_name)

    @tag(TestType = 'FVT', FeatureID = 'IOTOS-337')
    def test_appFW_app_restop(self):
        ''' Check app restop successfully '''
        self._startApp(self.node_app_name)
        self._stopApp(self.node_app_name)
        self._startApp(self.node_app_name)
        self._stopApp(self.node_app_name)

    @tag(TestType = 'FVT', FeatureID = 'IOTOS-337')
    def test_appFW_app_restart_systemctl(self):
        ''' Check app restart by systemctl restart successfully '''
        self._startApp(self.node_app_name)
        (status,output) = self.target.run("systemctl restart %s" % self.node_app_name)
        time.sleep(5)
        self.assertTrue(status == 0 , 'App restart by systemctl fail')
        self.assertTrue(self.app.getProcessPID(self.node_app_name),
                        'App restart by systemctl fail')
    
    @tag(TestType = 'FVT', FeatureID = 'IOTOS-339')
    def test_appFW_app_running_with_Dedicated_User(self):
        ''' check app launched by normal user '''
        self._startApp(self.node_app_name)
        p_info = self._getProcessInfo(self.node_app_name)
        self.assertTrue(p_info,'No see App running')
        p_name = p_info.split()[1]
        self.assertTrue(self.node_app_name[:8] == p_name , "Not found app running with dedicated user")
        # check the user is normal user by uid and gid
        (status,output) = self.target.run("id -u %s" % self.node_app_name)
        self.assertEqual(status, 0 , 'Fail to get uid : %s' % output)
        self.assertTrue(int(output)>=1000, 'Is not normal user, uid is: %s' % output)

        (status,output) = self.target.run("id -g %s" % self.node_app_name)
        self.assertEqual(status, 0 , 'Fail to get gid : %s' % output)
        self.assertTrue(int(output)>=1000, 'Is not normal user, uid is: %s' % output)
            

    @tag(TestType = 'FVT', FeatureID = 'IOTOS-342')
    def test_appFW_app_container_list(self):
        ''' check app listed in container '''
        self._startApp(self.node_app_name)
        (status,output) = self.target.run("machinectl -l")
        self.assertTrue(status == 0 and self.node_app_name in output , '%s : app not running in container' % output) 

    @tag(TestType = 'FVT', FeatureID = 'IOTOS-342')
    def test_appFW_app_container_status(self):
        ''' check app status in container '''
        self._startApp(self.node_app_name)
        (status,output) = self.target.run("machinectl status %s" % self.node_app_name)
        self.assertTrue(status == 0 and self.node_app_name in output , '%s : app not running in container' % output) 
        (status,output) = self.target.run("machinectl show %s" % self.node_app_name)
        self.assertTrue(status == 0 and 'State=running' in output , '%s : app not running in container' % output) 
         
    @tag(TestType = 'FVT', FeatureID = 'IOTOS-416')
    def test_appFW_app_impersonation(self):
        ''' check access of app user accout '''
        self.test_appFW_install_pkg_during_img_creation()
        (status,output) = self.target.run("su %s" % self.node_app_name)
        self.assertTrue(status != 0 , 'Test access of app user fail')
         
    @tag(TestType = 'FVT', FeatureID = 'IOTOS-358')
    def test_appFW_sqlite_integrated(self):
        ''' Check sqlite is integrated in image'''
        (status,output) = self.target.run("ls /usr/lib/libsqlite*.so || ls /lib/libsqlite*.so")
        self.assertTrue(status == 0 , 'Check sqlite integration fail')

    @tag(TestType = 'FVT', FeatureID = 'IOTOS-418')
    def test_appFW_app_autostart(self):
        ''' Check app is defined as autostart from manifest'''
        (status,output) = self.target.run("cat %s | grep autostart | grep -iE 'yes|true'" % self.node_app_manifest)
        self.assertEqual(status , 0 , 'App not set to autostart')
        self.assertTrue(self._getProcessInfo(self.node_app_name))
