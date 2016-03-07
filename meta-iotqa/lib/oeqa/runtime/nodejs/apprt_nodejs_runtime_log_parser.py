"""
@file apprt_nodejs_runtime_log_parser.py
"""

##
# @addtogroup nodejs nodejs
# @brief This is nodejs component
# @{
# @addtogroup apprt_nodejs_runtime_log_parser apprt_nodejs_runtime_log_parser
# @brief This is apprt_nodejs_runtime_log_parser module
# @{
##

import time


def is_a_blank_line(line):
    """
    @fn is_a_blank_line
    @return
    """
    blank = True
    for ch in line:
        if ch != chr(0x20):
            blank = False
            break
    return blank


def parse_test_cases(all_test_output, target_node_version):
    '''
    Parse the full node.js API test cases. 
    More information, please refer to the result log
    of running python tool/test.py
    in node.js repository
    @fn parse_test_cases
    @param all_test_output
    @return
    '''
    statistics = all_test_output[-1]
    statistics_list = statistics.lstrip('[').rstrip(']: Done').replace(
        '%',
        '').replace(
        '+',
        '').replace(
            '-',
        '').split('|')
    failed = int(statistics_list[-1])
    success = int(statistics_list[-2])
    all_num = success + failed
    all_info = []

    start = 0
    end = 0
    duration = 2
    for i in xrange(all_num):
        test_case = dict()
        test_case_info = dict()
        if all_test_output[start].startswith('[') and \
           is_a_blank_line(all_test_output[start + 1]):
            if all_test_output[start + 2].startswith('['):
                end = start + 1
                duration = 2
                success = True
                error = ''
                test_path = ''.join(['/tmp/node_%s_test/test/' % target_node_version])
                test_index = all_test_output[start].index(test_path)
                test_last_index = all_test_output[start].index('.js')
                test_case_name = all_test_output[start][
                    test_index +
                    len(test_path):
                    test_last_index].strip().replace('/', '-')
            elif all_test_output[start + 2].startswith('==='):
                err_start = start + 2
                i = 0
                while not all_test_output[err_start + i].startswith('['):
                    i += 1
                else:
                    err_duration = i - 1
                    end = start + 2 + err_duration
                duration = i + 2
                success = False
                error = ''
                for i in xrange(err_duration):
                    error += all_test_output[err_start + i]
                second_output = all_test_output[start + 2].splitlines()
                for index, line in enumerate(second_output):
                    if line.startswith('Path: '):
                        path_index = line.index('Path: ')
                        test_case_name_ori = line[path_index + len('Path: '):]
                        test_case_name = test_case_name_ori.strip().replace('/', '-')

            release_index = all_test_output[start].index(': release')
            test_case_name = all_test_output[start][
                release_index +
                len(': release') +
                1:].strip()

            test_case_info['last_exec_info'] = all_test_output[start]
            test_case_info['start'] = start
            test_case_info['end'] = end
            test_case_info['duration'] = duration
            test_case_info['success'] = success
            test_case_info['error'] = error

            test_case[test_case_name] = test_case_info
            all_info.append(test_case)

        start += duration

    return all_info


def print_test_results(all_tests):
    """
    @fn print_test_results
    @param all_tests
    @return
    """
    print '%d tests...' % len(all_tests)
    for t in all_tests:
        test_name = t.keys()[0]
        success = t.values()[0]['success']
        info = '\t' + test_name + '.' * (69 - len(test_name))
        if success:
            info += 'OK'
        else:
            info += 'FAILED'
            error = t.values()[0]['error']
            info += '\n'
            info += error
        print info


def print_error_test_results(all_tests):
    """
    @fn print_error_test_results
    @param all_tests
    @return
    """
    print '%d tests...' % len(all_tests)
    error_tests = []
    for t in all_tests:
        test_name = t.keys()[0]
        success = t.values()[0]['success']
        info = test_name
        if not success:
            info += t.values()[0]['error']
            error_tests.append(test_name + '\n')
            print info
    with open('error_test.txt', 'w') as f:
        f.writelines(error_tests)


def write_test_results(output, start_time, log_file, target_node_version):
    """
    @fn write_test_results
    @param output
    @param  start_time
    @param  log_file
    @return
    """
    output_seq = output
    all_tests = parse_test_cases(output_seq, target_node_version)

    for i in xrange(len(all_tests) - 1):
        (minutes, seconds) = all_tests[
            i + 1].values()[0]['last_exec_info'].split('|')[0].lstrip('[').split(':')
        elapse = float(minutes) * 60 + float(seconds)
        all_tests[i].values()[0]['result_at'] = time.strftime(
            '%H:%M:%S',
            time.gmtime(
                start_time +
                elapse))

    (minutes, seconds) = output_seq[-1].split('|')[0].lstrip('[').split(':')
    elapse = float(minutes) * 60 + float(seconds)
    all_tests[-1].values()[0]['result_at'] = time.strftime('%H:%M:%S',
                                    time.gmtime(start_time + elapse))

    f = open(log_file, 'w')
    for t in all_tests:
        if t.values()[0]['success']:
            success = 'PASSED'
        else:
            success = 'FAILED'
            success += '\n'
            success += t.values()[0]['error']
        f.write(
            '%s - runexported.py - RESULTS - Testcase %s: %s\n' %
            (t.values()[0]['result_at'], t.keys()[0], success))
    f.close()

##
# @}
# @}
##

