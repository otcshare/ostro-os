import json
import os
import sys

SCRIPT_PATH = os.path.realpath(__file__)
CONST_PATH = os.path.dirname(SCRIPT_PATH)
JSON_PATH = os.path.join(CONST_PATH, "tests/results.json")

def format_results(json_path):
    with open(json_path) as data_file:
        data = json.load(data_file)
    res_list = data["output"]
    log_file = 'results-iotivity-node-upstream.log'
    if os.path.exists(log_file):
        os.remove(log_file)
    for i in range(len(res_list)):
        item = res_list[i]["test"]
        caseinfo = res_list[i]["results"]
        for j in range(len(caseinfo)):
            run_time = caseinfo[j]["runtime"]
            if "FAIL" == caseinfo[j]["result"]:
                result = "FAILED"
                break
            else:
                result = "PASSED"
        case_id = item.replace(' ', '_')
        case_result_info = ''.join([
            run_time,
            ' - runtest.py - RESULTS - Testcase ',
            case_id,
            ': ',
            result,
            '\n'
            ])
        sys.stdout.write(case_result_info)
        #log_file = 'results-iotivity-node-upstream.log'
        with open(log_file, 'a') as f:
            f.write(case_result_info)

def write_log(output):
    '''
    Save result log to file
    @fn write_log
    @param self
    '''
    log_file = 'results-iotivity-node-upstream.log'
    if os.path.exists(log_file):
        os.remove(log_file)
    with open(log_file, 'a') as f:
        f.write(output)


if __name__ == '__main__':
    for json_file in sys.argv[1:]:
        format_results(json_file)
