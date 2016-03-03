#
# ISA_kca_plugin.py -  Kernel config options analyzer plugin, part of ISA FW
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

try:
    from lxml import etree
except ImportError:
    try:
        import xml.etree.cElementTree as etree
    except ImportError:
        import xml.etree.ElementTree as etree


KCAnalyzer = None

class ISA_KernelChecker():    
    initialized = False

    hardening_kco = {  'CONFIG_CC_STACKPROTECTOR'                       : 'not set', 
                       'CONFIG_DEFAULT_MMAP_MIN_ADDR'                   : 'not set',
                       'CONFIG_KEXEC'                                   : 'not set',
                       'CONFIG_PROC_KCORE'                              : 'not set',
                       'CONFIG_SECURITY_DMESG_RESTRICT'                 : 'not set',
                       'CONFIG_DEBUG_STACKOVERFLOW'                     : 'not set',
                       'CONFIG_DEBUG_STRICT_USER_COPY_CHECKS'           : 'not set',
                       'CONFIG_ARCH_HAS_DEBUG_STRICT_USER_COPY_CHECKS'  : 'not set',
                       'CONFIG_IKCONFIG_PROC'                           : 'not set',
                       'CONFIG_RANDOMIZE_BASE'                          : 'not set',
                       'CONFIG_RANDOMIZE_BASE_MAX_OFFSET'               : 'not set',
                       'CONFIG_DEBUG_RODATA'                            : 'not set',
                       'CONFIG_STRICT_DEVMEM'                           : 'not set',
                       'CONFIG_DEVKMEM'                                 : 'not set',
                       'CONFIG_X86_MSR'                                 : 'not set',
                       'CONFIG_ARCH_BINFMT_ELF_RANDOMIZE_PIE'           : 'not set',
                       'CONFIG_DEBUG_KERNEL'                            : 'not set',
                       'CONFIG_DEBUG_FS'                                : 'not set',
                       'CONFIG_MODULE_SIG_FORCE'                        : 'not set',
                       'CONFIG_X86_INTEL_MPX'                           : 'not set'                     
    }

    hardening_kco_ref={'CONFIG_CC_STACKPROTECTOR'                       : 'y', 
                       'CONFIG_DEFAULT_MMAP_MIN_ADDR'                   : '65536', # x86 specific
                       'CONFIG_KEXEC'                                   : 'not set',
                       'CONFIG_PROC_KCORE'                              : 'not set',
                       'CONFIG_SECURITY_DMESG_RESTRICT'                 : 'y',
                       'CONFIG_DEBUG_STACKOVERFLOW'                     : 'y',
                       'CONFIG_DEBUG_STRICT_USER_COPY_CHECKS'           : 'y',
                       'CONFIG_ARCH_HAS_DEBUG_STRICT_USER_COPY_CHECKS'  : 'y',
                       'CONFIG_IKCONFIG_PROC'                           : 'not set',
                       'CONFIG_RANDOMIZE_BASE'                          : 'y',
                       'CONFIG_RANDOMIZE_BASE_MAX_OFFSET'               : '0x20000000,0x40000000', # x86 specific
                       'CONFIG_DEBUG_RODATA'                            : 'y',
                       'CONFIG_STRICT_DEVMEM'                           : 'y',
                       'CONFIG_DEVKMEM'                                 : 'not set',
                       'CONFIG_X86_MSR'                                 : 'not set',
                       'CONFIG_ARCH_BINFMT_ELF_RANDOMIZE_PIE'           : 'y',
                       'CONFIG_DEBUG_KERNEL'                            : 'not set',
                       'CONFIG_DEBUG_FS'                                : 'not set',
                       'CONFIG_MODULE_SIG_FORCE'                        : 'y',
                       'CONFIG_X86_INTEL_MPX'                           : 'y'   # x86 and certain HW variants specific                  
                     }

    keys_kco =       { 'CONFIG_KEYS'                                    : 'not set',
                       'CONFIG_TRUSTED_KEYS'                            : 'not set',
                       'CONFIG_ENCRYPTED_KEYS'                          : 'not set',
                       'CONFIG_KEYS_DEBUG_PROC_KEYS'                    : 'not set'
                     }
    keys_kco_ref =   { 'CONFIG_KEYS'                                    : 'y',
                       'CONFIG_TRUSTED_KEYS'                            : 'y',
                       'CONFIG_ENCRYPTED_KEYS'                          : 'y',
                       'CONFIG_KEYS_DEBUG_PROC_KEYS'                    : 'not set'
                     }

    security_kco =   { 'CONFIG_SECURITY'                                : 'not set', 
                       'CONFIG_SECURITYFS'                              : 'not set',
                       'CONFIG_SECURITY_NETWORKING'                     : 'not set',
                       'CONFIG_DEFAULT_SECURITY'                        : 'not set',
                       'CONFIG_SECURITY_SELINUX'                        : 'not set',
                       'CONFIG_SECURITY_SMACK'                          : 'not set',
                       'CONFIG_SECURITY_TOMOYO'                         : 'not set',
                       'CONFIG_SECURITY_APPARMOR'                       : 'not set',
                       'CONFIG_SECURITY_YAMA'                           : 'not set',
                       'CONFIG_SECURITY_YAMA_STACKED'                   : 'not set',
                       'CONFIG_LSM_MMAP_MIN_ADDR'                       : 'not set',
                       'CONFIG_INTEL_TXT'                               : 'not set'                      
                      }

    security_kco_ref ={'CONFIG_SECURITY'                                : 'y', 
                       'CONFIG_SECURITYFS'                              : 'y',
                       'CONFIG_SECURITY_NETWORKING'                     : 'y',
                       'CONFIG_DEFAULT_SECURITY'                        : '"selinux","smack","apparmor","tomoyo"',
                       'CONFIG_SECURITY_SELINUX'                        : 'y',
                       'CONFIG_SECURITY_SMACK'                          : 'y',
                       'CONFIG_SECURITY_TOMOYO'                         : 'y',
                       'CONFIG_SECURITY_APPARMOR'                       : 'y',
                       'CONFIG_SECURITY_YAMA'                           : 'y',
                       'CONFIG_SECURITY_YAMA_STACKED'                   : 'y',
                       'CONFIG_LSM_MMAP_MIN_ADDR'                       : '65536', #x86 specific
                       'CONFIG_INTEL_TXT'                               : 'y'                      
                      }

    integrity_kco =  { 'CONFIG_INTEGRITY'                               : 'not set',
                       'CONFIG_INTEGRITY_SIGNATURE'                     : 'not set',
                       'CONFIG_INTEGRITY_AUDIT'                         : 'not set',
                       'CONFIG_IMA'                                     : 'not set',
                       'CONFIG_IMA_LSM_RULES'                           : 'not set',
                       'CONFIG_IMA_APPRAISE'                            : 'not set',
                       'CONFIG_IMA_TRUSTED_KEYRING'                     : 'not set',
                       'CONFIG_IMA_APPRAISE_SIGNED_INIT'                : 'not set',
                       'CONFIG_EVM'                                     : 'not set',
                       'CONFIG_EVM_ATTR_FSUUID'                         : 'not set',
                       'CONFIG_EVM_EXTRA_SMACK_XATTRS'                  : 'not set',
                       'CONFIG_IMA_DEFAULT_HASH_SHA1'                   : 'not set',
                       'CONFIG_IMA_DEFAULT_HASH_SHA256'                 : 'not set',
                       'CONFIG_IMA_DEFAULT_HASH_SHA512'                 : 'not set',
                       'CONFIG_IMA_DEFAULT_HASH_WP512'                  : 'not set'
                       }

    integrity_kco_ref={'CONFIG_INTEGRITY'                               : 'y',
                       'CONFIG_INTEGRITY_SIGNATURE'                     : 'y',
                       'CONFIG_INTEGRITY_AUDIT'                         : 'y',
                       'CONFIG_IMA'                                     : 'y',
                       'CONFIG_IMA_LSM_RULES'                           : 'y',
                       'CONFIG_IMA_APPRAISE'                            : 'y',
                       'CONFIG_IMA_TRUSTED_KEYRING'                     : 'y',
                       'CONFIG_IMA_APPRAISE_SIGNED_INIT'                : 'y',
                       'CONFIG_EVM'                                     : 'y',
                       'CONFIG_EVM_ATTR_FSUUID'                         : 'y',
                       'CONFIG_EVM_EXTRA_SMACK_XATTRS'                  : 'y',
                       'CONFIG_IMA_DEFAULT_HASH_SHA1'                   : 'not set',
                       'CONFIG_IMA_DEFAULT_HASH_SHA256'                 : 'y',
                       'CONFIG_IMA_DEFAULT_HASH_SHA512'                 : 'y',
                       'CONFIG_IMA_DEFAULT_HASH_WP512'                  : 'not set'
                       }

    def __init__(self, ISA_config):
        self.proxy = ISA_config.proxy
        self.logfile = ISA_config.logdir + "/isafw_kcalog"
        self.full_report_name = ISA_config.reportdir + "/kca_full_report_" + ISA_config.machine + "_" + ISA_config.timestamp
        self.problems_report_name = ISA_config.reportdir + "/kca_problems_report_" + ISA_config.machine + "_" + ISA_config.timestamp
        self.full_reports = ISA_config.full_reports
        self.initialized = True
        with open(self.logfile, 'w') as flog:
            flog.write("\nPlugin ISA_KernelChecker initialized!\n")

    def process_kernel(self, ISA_kernel):
        if (self.initialized == True):
            if (ISA_kernel.img_name and ISA_kernel.path_to_config):
                with open(self.logfile, 'a') as flog:
                    flog.write("Analyzing kernel config file at: " + ISA_kernel.path_to_config +
                               " for the image: " + ISA_kernel.img_name + "\n")
                with open(ISA_kernel.path_to_config, 'r') as fkernel_conf:
                    for line in fkernel_conf:
                        line = line.strip('\n')
                        for key in self.hardening_kco:
                            if key +'=' in line:
                                self.hardening_kco[key] = line.split('=')[1]
                        for key in self.keys_kco:
                            if key +'=' in line:
                                self.keys_kco[key] = line.split('=')[1]
                        for key in self.security_kco:
                            if key +'=' in line:
                                self.security_kco[key] = line.split('=')[1]
                        for key in self.integrity_kco:
                            if key +'=' in line:
                                self.integrity_kco[key] = line.split('=')[1]
                with open(self.logfile, 'a') as flog:
                    flog.write("\n\nhardening_kco values: " + str(self.hardening_kco))
                    flog.write("\n\nkeys_kco values: " + str(self.keys_kco))              
                    flog.write("\n\nsecurity_kco values: " + str(self.security_kco))              
                    flog.write("\n\nintegrity_kco values: " + str(self.integrity_kco))
                self.write_full_report(ISA_kernel)
                self.write_problems_report(ISA_kernel)

            else:
                with open(self.logfile, 'a') as flog:
                    flog.write("Mandatory arguments such as image name and path to config are not provided!\n")
                    flog.write("Not performing the call.\n")
        else:
            with open(self.logfile, 'a') as flog:
                flog.write("Plugin hasn't initialized! Not performing the call!\n")

    def write_full_report(self, ISA_kernel):
        if self.full_reports :      
            with open(self.full_report_name + "_" + ISA_kernel.img_name, 'w') as freport:
                freport.write("Report for image: " + ISA_kernel.img_name + '\n')
                freport.write("With the kernel conf at: " + ISA_kernel.path_to_config + '\n\n')
                freport.write("Hardening options:\n")
                for key in sorted(self.hardening_kco):
                    freport.write(key + ' : ' + str(self.hardening_kco[key]) + '\n')
                freport.write("\nKey-related options:\n")
                for key in sorted(self.keys_kco):
                    freport.write(key + ' : ' + str(self.keys_kco[key]) + '\n')
                freport.write("\nSecurity options:\n")
                for key in sorted(self.security_kco):
                    freport.write(key + ' : ' + str(self.security_kco[key]) + '\n')
                freport.write("\nIntegrity options:\n")
                for key in sorted(self.integrity_kco):
                    freport.write(key + ' : ' + str(self.integrity_kco[key]) + '\n')

    def write_problems_report(self, ISA_kernel):
        with open(self.problems_report_name + "_" + ISA_kernel.img_name, 'w') as freport:
            freport.write("Report for image: " + ISA_kernel.img_name + '\n')
            freport.write("With the kernel conf at: " + ISA_kernel.path_to_config + '\n\n')
            freport.write("Hardening options that need improvement:\n")
            for key in sorted(self.hardening_kco):
                if (self.hardening_kco[key] != self.hardening_kco_ref[key]) :
                    valid = False
                    if (key == "CONFIG_DEBUG_STRICT_USER_COPY_CHECKS") :
                        if (self.hardening_kco['CONFIG_ARCH_HAS_DEBUG_STRICT_USER_COPY_CHECKS'] == 'y'):
                            valid = True
                    if (key == "CONFIG_RANDOMIZE_BASE_MAX_OFFSET"):
                        options = self.hardening_kco_ref[key].split(',')
                        for option in options:
                            if (option == self.hardening_kco[key]):
                                valid = True
                                break
                    if valid == False :
                        freport.write("\nActual value:\n")
                        freport.write(key + ' : ' + str(self.hardening_kco[key]) + '\n')
                        freport.write("Recommended value:\n")
                        freport.write(key + ' : ' + str(self.hardening_kco_ref[key]) + '\n')
            freport.write("\nKey-related options that need improvement:\n")
            for key in sorted(self.keys_kco):
                if (self.keys_kco[key] != self.keys_kco_ref[key]) :
                    freport.write("\nActual value:\n")
                    freport.write(key + ' : ' + str(self.keys_kco[key]) + '\n')
                    freport.write("Recommended value:\n")
                    freport.write(key + ' : ' + str(self.keys_kco_ref[key]) + '\n')
            freport.write("\nSecurity options that need improvement:\n")
            for key in sorted(self.security_kco):
                if (self.security_kco[key] != self.security_kco_ref[key]) :
                    valid = False
                    if (key == "CONFIG_DEFAULT_SECURITY"):
                        options = self.security_kco_ref[key].split(',')
                        for option in options:
                            if (option == self.security_kco[key]):
                                valid = True
                                break
                    if ((key == "CONFIG_SECURITY_SELINUX") or 
                       (key == "CONFIG_SECURITY_SMACK") or
                       (key == "CONFIG_SECURITY_APPARMOR") or
                       (key == "CONFIG_SECURITY_TOMOYO")) :
                        if ((self.security_kco['CONFIG_SECURITY_SELINUX'] == 'y') or 
                            (self.security_kco['CONFIG_SECURITY_SMACK'] == 'y') or
                            (self.security_kco['CONFIG_SECURITY_APPARMOR'] == 'y') or
                            (self.security_kco['CONFIG_SECURITY_TOMOYO'] == 'y')):
                            valid = True
                    if valid == False:
                        freport.write("\nActual value:\n")
                        freport.write(key + ' : ' + str(self.security_kco[key]) + '\n')
                        freport.write("Recommended value:\n")
                        freport.write(key + ' : ' + str(self.security_kco_ref[key]) + '\n')
            freport.write("\nIntegrity options that need improvement:\n")
            for key in sorted(self.integrity_kco):
                if (self.integrity_kco[key] != self.integrity_kco_ref[key]) :
                    valid = False
                    if ((key == "CONFIG_IMA_DEFAULT_HASH_SHA1") or 
                       (key == "CONFIG_IMA_DEFAULT_HASH_SHA256") or
                       (key == "CONFIG_IMA_DEFAULT_HASH_SHA512") or
                       (key == "CONFIG_IMA_DEFAULT_HASH_WP512")) :
                        if ((self.integrity_kco['CONFIG_IMA_DEFAULT_HASH_SHA256'] == 'y') or 
                            (self.integrity_kco['CONFIG_IMA_DEFAULT_HASH_SHA512'] == 'y')):
                            valid = True
                    if valid == False :
                        freport.write("\nActual value:\n")
                        freport.write(key + ' : ' + str(self.integrity_kco[key]) + '\n')
                        freport.write("Recommended value:\n")
                        freport.write(key + ' : ' + str(self.integrity_kco_ref[key]) + '\n')
        # write_problems_report_xml 
        numTests = len(self.hardening_kco) + len(self.keys_kco) + len(self.security_kco) + len(self.integrity_kco)
        root = etree.Element('testsuite', name = 'KCA_Plugin', tests=str(numTests))
        for key in sorted(self.hardening_kco) :
            tcase1 = etree.SubElement(root, 'testcase', classname ='Hardening options', name = key)
            if (self.hardening_kco[key] != self.hardening_kco_ref[key]) :
                valid = False
                if (key == "CONFIG_DEBUG_STRICT_USER_COPY_CHECKS") :
                    if (self.hardening_kco['CONFIG_ARCH_HAS_DEBUG_STRICT_USER_COPY_CHECKS'] == 'y'):
                        valid = True
                if (key == "CONFIG_RANDOMIZE_BASE_MAX_OFFSET"):
                    options = self.hardening_kco_ref[key].split(',')
                    for option in options:
                        if (option == self.hardening_kco[key]):
                            valid = True
                            break
                if valid == False:
                    msg1 = 'current=' + key + ' is ' + str(self.hardening_kco[key]) + ', recommended=' + key + ' is ' + str(self.hardening_kco_ref[key]) 
                    failrs1 = etree.SubElement(tcase1, 'failure', message = msg1, type = 'violation')
        for key in sorted(self.keys_kco):
            tcase2 = etree.SubElement(root, 'testcase', classname = 'Key-related options', name = key)
            if (self.keys_kco[key] != self.keys_kco_ref[key]) :               
                msg2 = 'current=' + key + ' is ' + str(self.keys_kco[key] + ', recommended=' + key + ' is ' + str(self.keys_kco_ref[key])) 
                failrs2 = etree.SubElement(tcase2, 'failure', message = msg2, type = 'violation')
        for key in sorted(self.security_kco):
            tcase3 = etree.SubElement(root, 'testcase', classname = 'Security options', name = key)
            if (self.security_kco[key] != self.security_kco_ref[key]) :
                valid = False
                if (key == "CONFIG_DEFAULT_SECURITY"):
                    options = self.security_kco_ref[key].split(',')
                    for option in options:
                        if (option == self.security_kco[key]):
                            valid = True
                            break
                if ((key == "CONFIG_SECURITY_SELINUX") or 
                   (key == "CONFIG_SECURITY_SMACK") or
                   (key == "CONFIG_SECURITY_APPARMOR") or
                   (key == "CONFIG_SECURITY_TOMOYO")) :
                    if ((self.security_kco['CONFIG_SECURITY_SELINUX'] == 'y') or 
                        (self.security_kco['CONFIG_SECURITY_SMACK'] == 'y') or
                        (self.security_kco['CONFIG_SECURITY_APPARMOR'] == 'y') or
                        (self.security_kco['CONFIG_SECURITY_TOMOYO'] == 'y')):
                        valid = True
                if valid == False:
                    msg3 = 'current=' + key + ' is ' + str(self.security_kco[key]) + ', recommended=' + key + ' is ' + str(self.security_kco_ref[key])
                    failrs3 = etree.SubElement(tcase3, 'failure', message = msg3, type ='violation')
        for key in sorted(self.integrity_kco):
            tcase4 = etree.SubElement(root, 'testcase', classname = 'Integrity options', name = key)
            if (self.integrity_kco[key] != self.integrity_kco_ref[key]) :
                valid = False
                if ((key == "CONFIG_IMA_DEFAULT_HASH_SHA1") or 
                   (key == "CONFIG_IMA_DEFAULT_HASH_SHA256") or
                   (key == "CONFIG_IMA_DEFAULT_HASH_SHA512") or
                   (key == "CONFIG_IMA_DEFAULT_HASH_WP512")) :
                    if ((self.integrity_kco['CONFIG_IMA_DEFAULT_HASH_SHA256'] == 'y') or 
                        (self.integrity_kco['CONFIG_IMA_DEFAULT_HASH_SHA512'] == 'y')):
                        valid = True
                if valid == False :
                    msg4 = 'current=' + key + ' is ' + str(self.integrity_kco[key]) + ', recommended=' + key + ' is ' + str(self.integrity_kco_ref[key])
                    failrs4 = etree.SubElement(tcase4, 'failure', message = msg4, type='violation')
        tree = etree.ElementTree(root)
        output = self.problems_report_name + "_" + ISA_kernel.img_name + '.xml' 
        try:
            tree.write(output, encoding='UTF-8', pretty_print=True, xml_declaration=True)
        except TypeError:
            tree.write(output, encoding='UTF-8', xml_declaration=True)


#======== supported callbacks from ISA =============#

def init(ISA_config):
    global KCAnalyzer 
    KCAnalyzer = ISA_KernelChecker(ISA_config)
def getPluginName():
    return "ISA_KernelChecker"
def process_kernel(ISA_kernel):
    global KCAnalyzer 
    return KCAnalyzer.process_kernel(ISA_kernel)
#====================================================#

