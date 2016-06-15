import os
import sys
import shutil
import commands

def check_sudo_status():
    sudo_status = commands.getstatusoutput('sudo')
    if "sudo -h" not in sudo_status[1]:
        print '\nThe command "sudo" dose not exists'
        return False
    else:
        return True

def get_test_module_repo(url, module):
    repo_target_path = '/tmp'
    repo_path = os.path.join('/tmp',module)
    if os.path.exists(repo_path):
        status = check_sudo_status()
        if status is False:
            print '\nPlease remove the exists repository of %s at first using root' % module
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

    git_status = commands.getstatusoutput(git_cmd)
    if git_status[0] != 0:
        print '\nClone into %s failed! %s' % (module, git_status[1])
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
    inst_node_status = commands.getstatusoutput(inst_node_cmd)
    if inst_node_status[0] != 0:
        print '\nRe-install node modules using root!'
        inst_node = commands.getstatusoutput('sudo npm install')
        if inst_node[0] != 0:
            print '%s \n Install node modules failed! Please check it!' % \
            inst_node[1]
            sys.exit(1)
    if module == "iotivity-node":
        inst_grunt_cli_cmd = 'npm install grunt-cli'
        inst_grunt_cli_status = commands.getstatusoutput(inst_grunt_cli_cmd)
        if inst_grunt_cli_status[0] != 0:
            print '\nInstall grunt-cli failed! %s' % inst_grunt_cli_status[1]
            sys.exit(1)
        else:
            print '\nInstall grunt-cli done!'
