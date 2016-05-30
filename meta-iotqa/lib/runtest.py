#!/usr/bin/env python


# Copyright (C) 2015 Intel Corporation
#
# Released under the MIT license (see COPYING.MIT)
# ./runtest.py -b build_data.json -a tag -f test.manifest

import sys
import os
import time
import unittest
import inspect
from functools import wraps

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(os.path.join(BASEDIR, "oeqa"))

from optparse import OptionParser
from oeqa.oetest import oeTest
from oeqa.oetest import oeRuntimeTest
from oeqa.oetest import TestContext as OETestContext
from oeqa.utils.sshcontrol import SSHControl
from oeqa.utils.decorators import gettag

class FakeTarget(object):
    def __init__(self, d):
        self.connection = None
        self.ip = None
        self.server_ip = None
        self.datetime = time.strftime('%Y%m%d%H%M%S',time.gmtime())
        self.testdir = d.getVar("TEST_LOG_DIR", True)
        self.pn = d.getVar("PN", True)

    def exportStart(self, mainTarget=True):
        if mainTarget:
            self.sshlog = os.path.join(self.testdir, "ssh_target_log.%s" % self.datetime)
            sshloglink = os.path.join(self.testdir, "ssh_target_log")
            if os.path.lexists(sshloglink):
                os.remove(sshloglink)
            os.symlink(self.sshlog, sshloglink)
            print("SSH log file: %s" %  self.sshlog)
        else:
            self.sshlog = os.path.join(self.testdir, "ssh_target_log_%s_%s" % (self.ip, self.datetime))
        self.connection = SSHControl(self.ip, logfile=self.sshlog)

    def run(self, cmd, timeout=None):
        return self.connection.run(cmd, timeout)

    def copy_to(self, localpath, remotepath):
        return self.connection.copy_to(localpath, remotepath)

    def copy_from(self, remotepath, localpath):
        return self.connection.copy_from(remotepath, localpath)


class MyDataDict(dict):
    def getVar(self, key, unused = None):
        return self.get(key, "")

class TestContext(object):
    def __init__(self):
        self.d = None
        self.target = None

class RuntestTestContext(OETestContext):
    def __init__(self, tc):
        d = tc.d
        self.targets = tc.targets
        super(RuntestTestContext, self).__init__(d)
        self.pkgmanifest = tc.pkgmanifest
        self.target = tc.target
        self.tagexp = tc.tagexp
        self.imagefeatures = tc.imagefeatures
        self.distrofeatures = tc.distrofeatures
    def _get_test_suites(self):
        return self.d.getVar("testslist", True)
    def _get_tests_list(self, *args, **kwargs):
        return self.testsuites
    def _get_test_suites_required(self, *args, **kwargs):
        return self.testsuites
    def loadTests(self):
        super(RuntestTestContext, self).loadTests()
        setattr(oeRuntimeTest, "pscmd", "ps -ef" if oeTest.hasPackage("procps") else "ps")
try:
    import simplejson as json
except ImportError:
    import json

def setUp(self):
    pass
oeRuntimeTest.setUp = setUp

def wrap_runner(runner, *wargs, **wkwargs):
    @wraps(runner)
    def __wrapper(*args, **kwargs):
        # args and kwargs will overwrite the wargs and wkwargs
        _args = list(args)
        _args.extend(wargs[len(args):] if len(wargs) > len(args) else [])
        kw = wkwargs.copy()
        kw.update(kwargs)
        return runner(*_args, **kw)
    return __wrapper

def main():

    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--target-ip", dest="ip", action="append",
            help="The IP address of the target machine. Use this to \
            overwrite the value determined from TEST_TARGET_IP at build time")
    parser.add_option("-s", "--server-ip", dest="server_ip",
            help="The IP address of this machine. Use this to \
            overwrite the value determined from TEST_SERVER_IP at build time.")
    parser.add_option("-d", "--deploy-dir", dest="deploy_dir",
            default=os.path.join(BASEDIR, "deploy"),
            help="Full path to the package feeds, that this \
            the contents of what used to be DEPLOY_DIR on the build machine. \
            If not specified it will use the value specified in the json if \
            that directory actually exists or it will error out.")
    parser.add_option("-l", "--log-dir", dest="log_dir",
            help="This sets the path for TEST_LOG_DIR. If not specified \
            the current dir is used. This is used for usually creating a \
            ssh log file and a scp test file.")
    parser.add_option("-f", "--test-manifest", dest="tests_list",
            help="The test list file")
    parser.add_option("-b", "--build-data", dest="build_data",
            help="The build data file.")
    parser.add_option("-a", "--tag", dest="tag",
            help="The tags to filter test case")
    parser.add_option("-m", "--machine", dest="machine",
            help="""The target machine:quark intel-corei7-64 beaglebone""")
    parser.add_option("-n", "--nativearch", dest="nativearch",
            help="The native arch")
    parser.add_option("-x", "--xunit", dest="xunit",
            help="Output directory to put results in xUnit XML format")


    (options, args) = parser.parse_args()

    tc = TestContext()

    #inject testcase list
    tclist = []
    if not options.tests_list:
        options.tests_list = os.path.join(os.path.dirname(__file__), "testplan", "iottest.manifest")
    for each_manifest in options.tests_list.split():
        with open(each_manifest, "r") as f:
            map(lambda y:tclist.append(y) if y not in tclist else None, 
                filter(lambda x: x and not x.startswith('#'),
                              [n.strip() for n in f.readlines()])
                )
    tc.testslist = tclist
    print tc.testslist

    #add testsrequired for skipModule 
    tc.testsrequired = tc.testslist

    deployDir = os.path.abspath(options.deploy_dir)
    if not os.path.isdir(deployDir):
        raise Exception("The path to DEPLOY_DIR does not exists: %s" % deployDir)
    if options.machine:
        machine = options.machine
    else:
        parser.error("Please specify target machine by -m")
    if options.xunit:
        try:
            import xmlrunner
        except Exception:
            raise Exception(
              "xUnit output requested but unittest-xml-reporting not installed")
        unittest.TextTestRunner = wrap_runner(xmlrunner.XMLTestRunner, output=options.xunit)
    if options.build_data:
        build_data = options.build_data
    else:
        build_data = os.path.join(deployDir, "files", machine, "builddata.json")
    #get build data from file
    with open(build_data, "r") as f:
        loaded = json.load(f)
    #inject build datastore
    d = MyDataDict()
    if loaded.has_key("d"):
        for key in loaded["d"].keys():
            d[key] = loaded["d"][key]
    d["DEPLOY_DIR"], d["MACHINE"] = deployDir, machine
    if options.log_dir:
        d["TEST_LOG_DIR"] = os.path.abspath(options.log_dir)
    else:
        d["TEST_LOG_DIR"] = os.path.abspath(os.path.dirname(__file__))

    navarch = os.popen("uname -m").read().strip()
    d["BUILD_ARCH"] = "x86_64" if not navarch else navarch
    if options.nativearch:
        d["BUILD_ARCH"] = options.nativearch
    d["testslist"] = tc.testslist
    setattr(tc, "d", d)

    #inject build package manifest
    pkgs = [pname.strip() for pname in loaded["pkgmanifest"]]
    setattr(tc, "pkgmanifest", "\n".join(pkgs))

    #inject target information
    targets = []
    targets_ip = options.ip if options.ip else ["192.168.7.2"]
    server_ip = options.server_ip if options.server_ip else "192.168.7.1"
    first = True
    for ip in targets_ip:
        target = FakeTarget(d)
        target.ip = ip
        target.server_ip = server_ip
        target.exportStart(first)
        first = False
        targets.append(target)
    setattr(tc, "targets", targets)
    setattr(tc, "target", targets[0])
    setattr(oeRuntimeTest, "targets", targets)

    #inject others
    for key in loaded.keys():
        if key not in ["testslist", "d", "target", "pkgmanifest"]:
            setattr(tc, key, loaded[key])

    
    setattr(tc, "tagexp", options.tag)
    runner = RuntestTestContext(tc)
    runner.loadTests()
    runner.runTests()

    return 0

if __name__ == "__main__":
    try:
        ret = main()
    except Exception:
        ret = 1
        import traceback
        traceback.print_exc(5)
    sys.exit(ret)
