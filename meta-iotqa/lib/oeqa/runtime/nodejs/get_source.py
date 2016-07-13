import os
import sys
import shutil
import subprocess

def check_sudo_status():
    sudo_status = subprocess.Popen('sudo', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if "usage: sudo" not in sudo_status.stdout.read().decode('utf-8'):
        print('\nThe command "sudo" dose not exists')
        return False
    else:
        return True

def get_test_module_repo(url, module):
    repo_target_path = '/tmp'
    repo_path = os.path.join('/tmp',module)
    if os.path.exists(repo_path):
        status = check_sudo_status()
        if status is False:
            print('\nPlease remove the exists repository of' + module + 'at first using root')
            sys.exit(1)
        else:
            shutil.rmtree(repo_path)
    ori_path = os.getcwd()
    os.chdir(repo_target_path)
    if module == 'iotivity-node':
        git_cmd = ''.join([
                  'wget ',
                  url
            ])
    else:
        git_cmd = ''.join([
                  'git ',
                  'clone ',
                  url
            ])

    git_status = subprocess.Popen(git_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    git_status.wait()
    if git_status.returncode != 0:
        print('\nClone into '+ module +' failed!\n' + git_status.stdout.read().decode('utf-8'))
        sys.exit(1)
    inst_node_modules(url, module)
    os.chdir(ori_path)

def inst_node_modules(url, module):
    if module == 'iotivity-node':
        sub_str = url.split('/')
        for child_str in sub_str:
            if child_str.endswith('zip'):
                os.system('unzip %s >/dev/null 2>&1' % child_str)
                os.system('mv iotivity-node-%s iotivity-node' % \
                    child_str.strip('.zip'))
                os.system('rm %s*' % child_str)
    os.chdir('/tmp/%s' % module)
    inst_node_cmd = 'npm install'
    inst_node_status = subprocess.Popen(inst_node_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    inst_node_status.wait()
    if inst_node_status.returncode != 0:
        print('\nRe-install node modules using root!')
        inst_node = subprocess.Popen('sudo npm install', shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        inst_node.wait()
        if inst_node.returncode != 0:
            print('\nInstall node modules failed! Please check it!\n' + inst_node.stdout.read().decode('utf-8'))
            sys.exit(1)
    if module == "iotivity-node":
        inst_grunt_cli_cmd = 'npm install grunt-cli'
        inst_grunt_cli_status = subprocess.Popen(inst_grunt_cli_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        inst_grunt_cli_status.wait()
        if inst_grunt_cli_status.returncode != 0:
            print('\nInstall grunt-cli failed!\n' + inst_grunt_cli_status.stdout.read().decode('utf-8'))
            sys.exit(1)
        else:
            print('\nInstall grunt-cli done!')
