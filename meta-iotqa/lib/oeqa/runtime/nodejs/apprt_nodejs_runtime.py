"""
@file apprt_nodejs_runtime.py
"""

##
# @addtogroup nodejs nodejs
# @brief This is nodejs component
# @{
# @addtogroup apprt_nodejs_runtime apprt_nodejs_runtime
# @brief This is apprt_nodejs_runtime module
# @{
##

import os
import sys
import time
import shutil
import subprocess
import ConfigParser

from oeqa.oetest import oeRuntimeTest
from oeqa.utils.decorators import tag

from apprt_nodejs_runtime_log_parser import print_test_results
from apprt_nodejs_runtime_log_parser import parse_test_cases
from apprt_nodejs_runtime_log_parser import write_test_results
from nodejs_remove_blacklist_tests import remove_blacklist


def get_nodejs_repo(
        local_nodejs_path,
        config_file,
        node_version,
        store_output=False):
    '''
    Get the latest repo of node.js from github.com
    If the repo directory doesn't exist, git clone it.
    If the repo directory already exists, git pull it.
    @fn get_nodejs_repo
    @param          local_nodejs_path
    @param          config_file
    @param          node_version
    @param          store_output
    @return
    '''
    git_cmd = ['git']
    p = None
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    apprt_files_dir = os.path.dirname(local_nodejs_path)

    if os.path.exists(local_nodejs_path):
        git_cmd.append('pull')
        git_cmd.append('origin')
        git_cmd.append('%s-release:%s-release' % (node_version, node_version))
        p = subprocess.Popen(git_cmd,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             cwd=local_nodejs_path)
    else:
        if os.path.exists('/tmp/%s.zip' % node_version):
            get_node_zip_cmd = [
                'cp',
                '/tmp/%s.zip' %
                node_version,
                os.path.join(
                    apprt_files_dir,
                    '%s.zip' %
                    node_version)]
        else:
            node_archive_url = config.get('github', 'node_archive_url')
            get_node_zip_cmd = [
                'wget', '%s/%s.zip' %
                (node_archive_url, node_version)]
        p = subprocess.Popen(get_node_zip_cmd,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             cwd=apprt_files_dir)
        p.communicate()
        if p.returncode == 0:
            p = subprocess.Popen(['unzip',
                                  '%s.zip' % node_version],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 cwd=apprt_files_dir)
            p.communicate()
            if p.returncode == 0:
                os.rename(
                    os.path.join(
                        apprt_files_dir, 'node-%s' %
                        node_version.lstrip('v')), os.path.join(
                        apprt_files_dir, 'node'))
                return 0
            else:
                # If unzip fails because of the zip file is damaged, 
                # remove the zip file
                # and the generated directory if it exists
                zip_file = os.path.join(
                    apprt_files_dir,
                    '%s.zip' %
                    node_version)
                if os.path.exists(zip_file):
                    os.unlink(zip_file)
                unzip_folder = os.path.join(
                    apprt_files_dir,
                    'node-%s' %
                    node_version.lstrip('v'))
                if os.path.exists(unzip_folder):
                    shutil.rmtree(unzip_folder)

        nodejs_url = config.get(
            'github',
            'nodejs_url',
            vars={
                'nodejs_url': 'https://github.com/nodejs/node.git'})

        git_cmd.append('clone')
        git_cmd.append(nodejs_url)

        p = subprocess.Popen(git_cmd,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             cwd=apprt_files_dir)

    p.wait()
    if store_output:
        with open('git.log', 'w') as f:
            f.write(p.stdout.read())
    return p.returncode


def checkout_nodejs(local_nodejs_path, node_version='v4.2.4'):
    '''
    Switch the right branch from the local nodejs repo.
    We need to checkout the branch because of different branches of nodejs
    source may have different number of API test cases.
    Make sure the test cases matches node version of target device.
    For example, if the node version of target device is v0.12.7, we need to
    git checkout v0.12.7-release
    branch.
    @fn checkout_nodejs
    @param local_nodejs_path
    @param  node_version
    @return
    '''
    apprt_files_dir = os.path.dirname(local_nodejs_path)
    if os.path.exists(os.path.join(apprt_files_dir, '%s.zip' % node_version)):
        return 0

    if not os.path.exists(local_nodejs_path):
        sys.stderr.write(
            'node repo directory %s does not exist!\n' %
            local_nodejs_path)
        return 1

    get_remote_branch_cmd = ['git', 'branch', '-a']
    found_matched_node = False
    p = subprocess.Popen(get_remote_branch_cmd,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         cwd=local_nodejs_path)
    node_version_release = node_version + '-release'
    for line in p.stdout:
        if node_version in line and node_version_release in line:
            found_matched_node = True
            break

    if found_matched_node:
        git_checkout_cmd = ['git', 'checkout', '%s' % node_version_release]
        p = subprocess.Popen(git_checkout_cmd,
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             cwd=local_nodejs_path)
        p.wait()
        return p.returncode
    else:
        # no matched node branch found.
        return 1


def choose_test_files_and_tar(local_nodejs_path, node_version):
    '''
    choose all the test files and directories so that we start tests.
    1. Generate a new temporary directory
    2. Copy all the files and directories to the temporary directory.
    3. tar -cjf node-<version>-release.tar.gz
    @fn choose_test_files_and_tar
    @param local_nodejs_path
    @param  node_version
    @return
    '''
    apprt_files_dir = os.path.abspath(os.path.dirname(local_nodejs_path))

    node_test_dir = os.path.join(apprt_files_dir,
                                 'node_%s_test' % node_version)

    if os.path.exists(node_test_dir):
        shutil.rmtree(node_test_dir)
    os.mkdir(node_test_dir)

    if os.path.exists('%s.tar.gz' % node_test_dir):
        os.unlink('%s.tar.gz' % node_test_dir)

    # The 3 directories are certain to be used
    sys.stdout.write('Removing blacklist tests')
    sys.stdout.flush()
    remove_blacklist(apprt_files_dir, node_version)
    copy_dirs = ['tools', 'test', 'deps/v8/tools']
    for single_dir in copy_dirs:
        shutil.copytree(os.path.join(local_nodejs_path, single_dir),
                        os.path.join(node_test_dir, single_dir))
    for filename in os.listdir(local_nodejs_path):
        file_path = os.path.join(local_nodejs_path, filename)
        if os.path.isfile(file_path):
            shutil.copyfile(file_path,
                            os.path.join(node_test_dir, filename))

    compact_cmd = ['tar', '-czf']
    compact_cmd.append('%s.tar.gz' % node_test_dir)
    compact_cmd.append('node_%s_test' % node_version)

    p = subprocess.Popen(compact_cmd, cwd=apprt_files_dir)
    p.wait()

    return p.returncode


@tag(TestType='EFT', FeatureID='IOTOS-332')
class NodejsRuntimeTest(oeRuntimeTest):
    """
    @class NodejsRuntimeTest
    """

    target_node_version = None
    target_node_path = None

    has_build_toolchain = False
    files_dir = None
    nodejs_dir = None
    node_zip = None
    config_path = None
    config = None

    def setUp(self):
        '''
        The steps of testing the full nodejs APIs:
        1. Download the node.js official repository, and checkout the version
           of the pre-installed node version so that the test cases can apply
           to the pre-installed node version.
        2. Find the pre-installed node version. Go to the local repo directory
            and checkout the right version of node source that matches the
            target device
        3. Change some configuration that before the test start.
        4. Upload the necessary files and directories on the target device.
        @fn setUp
        @param self
        @return
        '''

        # Get the node information of target device
        self.files_dir = os.path.join(
            os.path.abspath(
                os.path.dirname(__file__)),
            'files')
        self.nodejs_dir = os.path.join(self.files_dir, 'node')
        self.config_path = os.path.join(
            self.files_dir,
            'noderuntime',
            'apprt_nodejs_runtime_config')

        # Clean the wokrspace directory to avoid error when setUp fails, 
        # this ususally causes the failure of second-time to run.
        if os.path.exists(self.nodejs_dir):
            shutil.rmtree(self.nodejs_dir)

        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_path)
        self.target_node_path = self.config.get('target', 'node_path')
        self.target_node_version = self.config.get('target', 'node_version')

        (status, output) = self.target.run('which node')
        if status != 0:
            sys.stderr.write(
                '\nExecuting which node error, use default node path: %s!\n' %
                self.target_node_path)
            sys.stderr.flush()
        else:
            self.target_node_path = output.strip()

        (status, output) = self.target.run('node -v')
        if status != 0:
            sys.stderr.write(
                '\nExecuting node -v error, use default node version: %s!\n' %
                self.target_node_version)
            sys.stdout.flush()
        else:
            self.target_node_version = output.strip()
            sys.stdout.write(
                '\nNode version on target: %s\n' %
                self.target_node_version)
            sys.stdout.flush()

        # Consider the failure of the setUp, we need to clean before we do
        # anything.
        self.node_zip = os.path.join(
            self.files_dir,
            '%s.zip' %
            self.target_node_version)
        if os.path.exists(self.node_zip):
            os.unlink(self.node_zip)

        node_test_dir = os.path.join(
            self.files_dir,
            'node_%s_test' %
            self.target_node_version)
        if os.path.exists(node_test_dir):
            shutil.rmtree(node_test_dir)
        if os.path.exists('%s.tar.gz' % node_test_dir):
            os.unlink('%s.tar.gz' % node_test_dir)

        sys.stdout.write('Downloading node.js repository...')
        sys.stdout.flush()
        ret = get_nodejs_repo(
            self.nodejs_dir,
            self.config_path,
            self.target_node_version)
        if ret != 0:
            sys.stderr.write('Fail to download node.js repo\n')
            sys.exit(1)
        sys.stdout.write('\r' + ' ' * 78 + '\r')
        sys.stdout.write('Downloading node.js repository DONE\n')
        sys.stdout.flush()

        sys.stdout.write(
            'Checking out node.js to branch %s...' %
            self.target_node_version)
        sys.stdout.flush()
        ret = checkout_nodejs(self.nodejs_dir, self.target_node_version)
        if ret != 0:
            sys.stderr.write('Fail to checkout node.js with version %s\n'
                             % self.target_node_version)
            sys.exit(1)
        sys.stdout.write('\r' + ' ' * 78 + '\r')
        sys.stdout.write(
            'Checking out node.js to branch %s DONE\n' %
            self.target_node_version)
        sys.stdout.flush()

        sys.stdout.write('Choosing necessary files for tests...')
        sys.stdout.flush()
        ret = choose_test_files_and_tar(
            self.nodejs_dir,
            self.target_node_version)
        if ret != 0:
            sys.stderr.write('Fail to copy test files and tar\n')
            sys.exit(1)
        sys.stdout.write('\r' + ' ' * 78 + '\r')
        sys.stdout.write('Choosing necessary files for tests DONE\n')
        sys.stdout.flush()

        # Clean /tmp directory to make sure no node_VERSION_test directory
        # and no node_VERSION_test.tar.gz file on target
        self.target.run('rm -fr /tmp/node_%s_test/' % self.target_node_version)
        self.target.run(
            'rm -f /tmp/node_%s_test.tar.gz' %
            self.target_node_version)

        sys.stdout.write('Copying necessary files to target...')
        sys.stdout.flush()
        (status, output) = self.target.copy_to(
            os.path.join(
                self.files_dir,
                'node_%s_test.tar.gz' %
                self.target_node_version),
            '/tmp/node_%s_test.tar.gz' %
            self.target_node_version)
        if status != 0:
            sys.stderr.write('Fail to copy archives to the target device\n')
            sys.exit(1)
        sys.stdout.write('\r' + ' ' * 78 + '\r')
        sys.stdout.write(
            'Copying node_%s_test.tar.gz to target device DONE\n' %
            self.target_node_version)
        sys.stdout.flush()

        sys.stdout.write('Extracting tar files on target...')
        sys.stdout.flush()
        (status, output) = self.target.run(
            'tar -xzf  /tmp/node_%s_test.tar.gz -C /tmp/' % \
            self.target_node_version)
        if status != 0:
            sys.stderr.write('Fail to extract node.js test files\n')
            sys.exit(1)
        sys.stdout.write('\r' + ' ' * 78 + '\r')
        sys.stdout.write(
            'Extracting node_%s_test.tar.gz on target device DONE\n' %
            self.target_node_version)
        sys.stdout.flush()

        (status, output) = self.target.run(
            'mkdir -p /tmp/node_%s_test/out/Release' % self.target_node_version)
        if status != 0:
            sys.stderr.write('Fail to mkdir out/Release in node directory\n')
            sys.exit(1)
        sys.stdout.write(
            'mkdir -p /tmp/node_%s_test/out/Release DONE\n' %
            self.target_node_version)
        sys.stdout.flush()

        (status, output) = self.target.run(
            'ln -fs %s /tmp/node_%s_test/out/Release/node' %
            (self.target_node_path, self.target_node_version))
        if status != 0:
            sys.stderr.write(
                'Fail to link %s -> /tmp/node_%s_test/out/Release/node\n' %
                (self.target_node_path, self.target_node_version))
        else:
            sys.stdout.write(
                'ln -fs %s /tmp/node_%s_test/out/Release/node DONE\n' %
                (self.target_node_path, self.target_node_version))
            sys.stdout.flush()

    @tag(CasesNumber=865)
    def test_apprt_nodejs_runtime(self):
        '''
        Execute the node.js upstream test cases.
        @fn test_apprt_nodejs_runtime
        @param self
        @return
        '''
        sys.stdout.write('Executing node.js upstream test cases...\n');
        sys.stdout.flush()
        start = time.time()

        test_modules = self.config.get('test', 'specified_modules')
        (status, output) = self.target.run(
            'cd /tmp/node_%s_test/; python tools/test.py %s -v' %
            (self.target_node_version, test_modules))

        output = output.strip().split('\r')
        print_test_results(parse_test_cases(output, self.target_node_version))
        write_test_results(
            output,
            start,
            self.config.get(
                'results',
                'formatted_result_file'),
                self.target_node_version
            )

#        statistics = output[-1]
#        sys.stdout.write(statistics + '\n')
#        sys.stdout.flush()
#        statistics_list = statistics.lstrip('[').rstrip(']: Done').\
#               replace('%', '').replace('+', '').replace('-', '').split('|')
#        failed_num = int(statistics_list[-1])
#        self.assertEqual(failed_num, 0, msg = \
#               'There are %s test(s) failed!' % failed_num)

    def tearDown(self):
        '''
        Clean work: remove all the files downloaded on host and 
        copied to the target device during the test.
        @fn tearDown
        @param self
        @return
        '''
        node_test_dir = os.path.join(
            self.files_dir,
            'node_%s_test' %
            self.target_node_version)

        if os.path.exists(self.nodejs_dir):
            shutil.rmtree(self.nodejs_dir)
            sys.stdout.write('Removing node.js repository DONE\n')
            sys.stdout.flush()

        if os.path.exists(node_test_dir):
            shutil.rmtree(node_test_dir)
            sys.stdout.write(
                'Removing node_%s_test directory DONE\n' %
                self.target_node_version)
            sys.stdout.flush()

        if os.path.exists('%s.tar.gz' % node_test_dir):
            os.unlink('%s.tar.gz' % node_test_dir)
            sys.stdout.write(
                'Removing node_%s_test.tar.gz DONE\n' %
                self.target_node_version)
            sys.stdout.flush()

        if os.path.exists(self.node_zip):
            if not os.path.exists('/tmp/%s.zip' % self.target_node_version):
                shutil.copyfile(
                    self.node_zip,
                    '/tmp/%s.zip' %
                    self.target_node_version)
            os.unlink(self.node_zip)
            sys.stdout.write(
                'Removing node %s.zip DONE\n' %
                self.target_node_version)
            sys.stdout.flush()

        self.target.run('rm -fr /tmp/node_%s_test/' % self.target_node_version)
        sys.stdout.write(
            'rm -fr /tmp/node_%s_test/ on target DONE\n' %
            self.target_node_version)
        sys.stdout.flush()

        self.target.run(
            'rm -f /tmp/node_%s_test.tar.gz' %
            self.target_node_version)
        sys.stdout.write(
            'rm -f /tmp/node_%s_test.tar.gz on target DONE\n' %
            self.target_node_version)
        sys.stdout.flush()

##
# @}
# @}
##

