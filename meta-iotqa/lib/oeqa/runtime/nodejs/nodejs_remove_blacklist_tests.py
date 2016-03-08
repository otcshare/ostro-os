import os
import shutil


def remove_blacklist(apprt_files_dir, node_version):
    '''
    Remove the invalid test cases from file blacklist
    @fn remove_blacklist
    @param apprt_files_dir
    @node_version
    '''
    blacklist_file = os.path.join(
        apprt_files_dir,
        'noderuntime/blacklist'
        )
    test_suite_path = os.path.join(
        apprt_files_dir,
        ''.join([
            'node_',
            node_version,
            '_test'
            ]),
        'test'
        )
    with open(blacklist_file) as f:
        lines = f.readlines()
        for line in lines:
            line_format = line.strip('\n').split('/')
            folder_name = line_format[0]
            file_name = ''.join([line_format[-1], '.js'])
            folder_path = os.path.join(
                            test_suite_path,
                            folder_name
                            )
            if folder_name == 'addons':
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
            elif folder_name == 'gc':
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
            else:
                os.remove(
                    os.path.join(
                        folder_path,
                        file_name
                        )
                    )
