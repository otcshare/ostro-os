#
# ISA_cfa_plugin.py -  Compile flag analyzer plugin, part of ISA FW
# Main functionality is based on build_comp script from Clear linux project
#
# Copyright (c) 2015, Intel Corporation
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of Intel Corporation nor the names of its contributors
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import subprocess
import os
import stat
from re import compile
from re import sub
from lxml import etree

CFChecker = None

class ISA_CFChecker():    
    initialized = False
    no_relo = []
    no_canary = []
    no_pie = []
    no_nx = []
    execstack = []
    execstack_not_defined = []
    nodrop_groups = []
    no_mpx = []

    def __init__(self, ISA_config):
        self.proxy = ISA_config.proxy
        self.logfile = ISA_config.logdir + "/isafw_cfalog"
        self.full_report_name = ISA_config.reportdir + "/cfa_full_report_" + ISA_config.machine + "_" + ISA_config.timestamp
        self.problems_report_name = ISA_config.reportdir + "/cfa_problems_report_" + ISA_config.machine + "_" + ISA_config.timestamp
        self.full_reports = ISA_config.full_reports
        # check that checksec is installed
        DEVNULL = open(os.devnull, 'wb')
        rc = subprocess.call(["which", "checksec.sh"], stdout=DEVNULL)
        if rc == 0:
            # check that execstack is installed
            rc = subprocess.call(["which", "execstack"], stdout=DEVNULL)
            if rc == 0:
                # check that execstack is installed
                rc = subprocess.call(["which", "readelf"], stdout=DEVNULL)
                if rc == 0:
                    self.initialized = True
                    with open(self.logfile, 'w') as flog:
                        flog.write("\nPlugin ISA_CFChecker initialized!\n")
                        DEVNULL.close()
                    return
        with open(self.logfile, 'w') as flog:
            flog.write("checksec, execstack or readelf tools are missing!\n")
            flog.write("Please install checksec from http://www.trapkit.de/tools/checksec.html\n")
            flog.write("Please install execstack from prelink package\n")
        DEVNULL.close()

    def process_filesystem(self, ISA_filesystem):
        if (self.initialized == True):
            if (ISA_filesystem.img_name and ISA_filesystem.path_to_fs):
                with open(self.logfile, 'a') as flog:
                    flog.write("\n\nFilesystem path is: " + ISA_filesystem.path_to_fs)
                if self.full_reports :
                    with open(self.full_report_name + "_" + ISA_filesystem.img_name, 'w') as ffull_report:
                        ffull_report.write("Security-relevant flags for executables for image: " + ISA_filesystem.img_name + '\n')
                        ffull_report.write("With rootfs location at " +  ISA_filesystem.path_to_fs + "\n\n")
                self.files = self.find_files(ISA_filesystem.path_to_fs)
                with open(self.logfile, 'a') as flog:
                    flog.write("\n\nFile list is: " + str(self.files))
                self.process_files(ISA_filesystem.img_name, ISA_filesystem.path_to_fs)
                self.write_report(ISA_filesystem)
                self.write_report_xml(ISA_filesystem)
            else:
                with open(self.logfile, 'a') as flog:
                    flog.write("Mandatory arguments such as image name and path to the filesystem are not provided!\n")
                    flog.write("Not performing the call.\n")
        else:
            with open(self.logfile, 'a') as flog:
                flog.write("Plugin hasn't initialized! Not performing the call.\n")

    def write_report(self, ISA_filesystem):
        with open(self.problems_report_name + "_" + ISA_filesystem.img_name, 'w') as fproblems_report:
            fproblems_report.write("Report for image: " + ISA_filesystem.img_name + '\n')
            fproblems_report.write("With rootfs location at " + ISA_filesystem.path_to_fs + "\n\n")
            fproblems_report.write("Files with no RELO:\n")
            for item in self.no_relo:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                fproblems_report.write(item + '\n')
            fproblems_report.write("\n\nFiles with no canary:\n")
            for item in self.no_canary:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                fproblems_report.write(item + '\n')
            fproblems_report.write("\n\nFiles with no PIE:\n")
            for item in self.no_pie:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                fproblems_report.write(item + '\n')
            fproblems_report.write("\n\nFiles with no NX:\n")
            for item in self.no_nx:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                fproblems_report.write(item + '\n')
            fproblems_report.write("\n\nFiles with executable stack enabled:\n")
            for item in self.execstack:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                fproblems_report.write(item + '\n')
            fproblems_report.write("\n\nFiles with no ability to fetch executable stack status:\n")
            for item in self.execstack_not_defined:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                fproblems_report.write(item + '\n')
            fproblems_report.write("\n\nFiles that don't initialize groups while using setuid/setgid:\n")
            for item in self.nodrop_groups:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                fproblems_report.write(item + '\n')
            fproblems_report.write("\n\nFiles that don't have MPX protection enabled:\n")
            for item in self.no_mpx:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                fproblems_report.write(item + '\n')

    def write_report_xml(self, ISA_filesystem):
        numTests = len(self.no_relo) + len(self.no_canary) + len(self.no_pie) + len(self.no_nx) + len(self.execstack) + len(self.execstack_not_defined) + len(self.nodrop_groups) + len(self.no_mpx) 
        root = etree.Element('testsuite', name='ISA_CFChecker', tests=str(numTests))
        if self.no_relo:
            for item in self.no_relo:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                tcase1 = etree.SubElement(root, 'testcase', classname='files_with_no_RELO', name=item)
                etree.SubElement(tcase1, 'failure', message=item, type='violation')
        if self.no_canary: 
            for item in self.no_canary:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                tcase2 = etree.SubElement(root, 'testcase', classname='files_with_no_canary', name=item)
                etree.SubElement(tcase2, 'failure', message=item, type='violation')
        if self.no_pie: 
            for item in self.no_pie:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                tcase3 = etree.SubElement(root, 'testcase', classname='files_with_no_PIE', name=item)
                etree.SubElement(tcase3, 'failure', message=item, type='violation')
        if self.no_nx: 
            for item in self.no_nx:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                tcase4 = etree.SubElement(root, 'testcase', classname='files_with_no_NX', name=item)
                etree.SubElement(tcase4, 'failure', message=item, type='violation')
        if self.execstack: 
            for item in self.execstack:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                tcase5 = etree.SubElement(root, 'testcase', classname='files_with_execstack', name=item)
                etree.SubElement(tcase5, 'failure', message=item, type='violation')
        if self.execstack_not_defined: 
            for item in self.execstack_not_defined:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                tcase6 = etree.SubElement(root, 'testcase', classname='files_with_execstack_not_defined', name=item)
                etree.SubElement(tcase6, 'failure', message=item, type='violation')
        if self.nodrop_groups: 
            for item in self.nodrop_groups:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                tcase7 = etree.SubElement(root, 'testcase', classname='files_with_nodrop_groups', name=item)
                etree.SubElement(tcase7, 'failure', message=item, type='violation')
        if self.no_mpx: 
            for item in self.no_mpx:
                item = item.replace(ISA_filesystem.path_to_fs, "")
                tcase8 = etree.SubElement(root, 'testcase', classname='files_with_no_mpx', name=item)
                etree.SubElement(tcase8, 'failure', message=item, type='violation')
        tree = etree.ElementTree(root)
        output = self.problems_report_name + "_" + ISA_filesystem.img_name + '.xml' 
        tree.write(output, encoding= 'UTF-8', pretty_print=True, xml_declaration=True)

    def find_files(self, init_path):
        list_of_files = []
        for (dirpath, dirnames, filenames) in os.walk(init_path):
            for f in filenames:
                list_of_files.append(str(dirpath+"/"+f)[:])
        return list_of_files

    def get_execstack(self, file_name):
        cmd = ['execstack', '-q', file_name]
        try:
            result = subprocess.check_output(cmd).decode("utf-8")
        except:
            return "Not able to fetch execstack status"
        else:
            if result.startswith("X "):
                self.execstack.append(file_name[:])
            if result.startswith("? "):
                self.execstack_not_defined.append(file_name[:])             
            return result

    def get_nodrop_groups(self, file_name):
        cmd = ['readelf', '-s', file_name]
        try:
            result = subprocess.check_output(cmd).decode("utf-8")
        except:
            return "Not able to fetch nodrop groups status"
        else:
            if ("setgid@GLIBC" in result) or ("setegid@GLIBC" in result) or ("setresgid@GLIBC" in result):
                if ("setuid@GLIBC" in result) or ("seteuid@GLIBC" in result) or ("setresuid@GLIBC" in result):
                    if ("setgroups@GLIBC" not in result) and ("initgroups@GLIBC" not in result):
                        self.nodrop_groups.append(file_name[:])       
            return result

    def get_mpx(self, file_name):
        cmd = ['objdump', '-d', file_name]
        try:
            result = subprocess.check_output(cmd).decode("utf-8")
        except:
            return "Not able to fetch mpx status"
        else:
            if ("bndcu" not in result) and ("bndcl" not in result) and ("bndmov" not in result):
                self.no_mpx.append(file_name[:])       
            return result

    def get_security_flags(self, file_name):
        SF = {
	        'No RELRO'        : 0,
	        'Full RELRO'      : 2,
	        'Partial RELRO'   : 1,
	        'Canary found'    : 1,
	        'No canary found' : 0,
	        'NX disabled'     : 0,
	        'NX enabled'      : 1,
	        'No PIE'          : 0,
	        'PIE enabled'     : 3,
	        'DSO'             : 2,
	        'RPATH'           : 0,
	        'Not an ELF file' : 1,
	        'No RPATH'        : 1,
	        'RUNPATH'         : 0,
	        'No RUNPATH'      : 1
        }
        cmd = ['checksec.sh', '--file', file_name]
        try:
            result = subprocess.check_output(cmd).decode("utf-8").split('\n')[1]
        except:
            return "Not able to fetch flags"
        else:
            ansi_escape = compile(r'\x1b[^m]*m')
            text = ansi_escape.sub('', result)
            text2 = sub(r'\ \ \ *', ',', text).split(',')[:-1]
            text = []
            for t2 in text2:
                if t2 == "No RELRO":
                    self.no_relo.append(file_name[:])
                elif t2 == "No canary found" :
                    self.no_canary.append(file_name[:])
                elif t2 == "No PIE" :
                    self.no_pie.append(file_name[:])
                elif t2 == "NX disabled" :
                    self.no_nx.append(file_name[:])
                text.append((t2, SF[t2]))               
            return text

    def process_files(self, img_name, path_to_fs):
        for i in self.files:
            real_file = i
            if os.path.isfile(i):
                # getting file type
                cmd = ['file', '--mime-type', i]
                try:
                    result = subprocess.check_output(cmd).decode("utf-8")
                except:
                    print("Not able to decode mime type", sys.exc_info())
                    with open(self.logfile, 'a') as flog:
                        flog.write("Not able to decode mime type" + sys.exc_info())
                    continue
                type = result.split()[-1]
                # looking for links
                if type.find("symlink") != -1:
                    real_file = os.path.realpath(i)
                    cmd = ['file', '--mime-type', real_file]
                    try:
                        result = subprocess.check_output(cmd).decode("utf-8")
                    except:
                        print("Not able to decode mime type", sys.exc_info())
                        with open(self.logfile, 'a') as flog:
                            flog.write("Not able to decode mime type" + sys.exc_info())
                        continue
                    type = result.split()[-1]
                # checking security flags if applies
                if type.find("application") != -1:
                    if type.find("octet-stream") != -1:
                        sec_field = "File is octect-stream, can not be analyzed with checksec.sh"
                    elif type.find("dosexec") != -1:
                        sec_field = "File MS Windows binary"
                    elif type.find("archive") != -1:
                        sec_field = "File is an archive"
                    elif type.find("xml") != -1:
                        sec_field = "File is xml"
                    elif type.find("gzip") != -1:
                        sec_field = "File is gzip"
                    elif type.find("postscript") != -1:
                        sec_field = "File is postscript"
                    elif type.find("pdf") != -1:
                        sec_field = "File is pdf"
                    else:
                        sec_field = self.get_security_flags(real_file)
                        execstack = self.get_execstack(real_file)
                        nodrop_groups = self.get_nodrop_groups(real_file)
                        no_mpx = self.get_mpx(real_file)
                        if self.full_reports :
                            with open(self.full_report_name + "_" + img_name, 'a') as ffull_report:
                                real_file = real_file.replace(path_to_fs, "")
                                ffull_report.write(real_file + ": ")
                                for s in sec_field:
                                    line = ' '.join(str(x) for x in s)
                                    ffull_report.write(line + ' ')
                                ffull_report.write('\nexecstack: ' + execstack +' ')
                                ffull_report.write('\nnodrop_groups: ' + nodrop_groups +' ')
                                ffull_report.write('\nno mpx: ' + no_mpx +' ')
                                ffull_report.write('\n')                            
                else:
                    continue

#======== supported callbacks from ISA =============#

def init(ISA_config):
    global CFChecker 
    CFChecker = ISA_CFChecker(ISA_config)
def getPluginName():
    return "ISA_CFChecker"
def process_filesystem(ISA_filesystem):
    global CFChecker 
    return CFChecker.process_filesystem(ISA_filesystem)

#====================================================#

