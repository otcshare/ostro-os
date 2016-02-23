#
# isafw.py - Main classes for ISA FW
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


import os
import sys
import isaplugins


__all__ = [
    'ISA_package',
    'ISA_pkg_list',
    'ISA_kernel',
    'ISA_filesystem',
    'ISA',
    ]

# classes for representing objects for ISA plugins

# source package
class ISA_package:
    name = ""                     # pkg name                            (mandatory argument)
    version = ""                  # full version                        (mandatory argument)
    licenses = []                 # list of licences for all subpackages
    aliases = []                  # list of alias names for packages if exist
    source_files = []             # list of strings of source files 
    patch_files = []              # list of patch files to be applied
    path_to_sources = ""          # path to the source files

# package list
class ISA_pkg_list:
    img_name = ""                 # image name                            (mandatory argument)
    path_to_list = ""             # path to the pkg list file             (mandatory argument)

# kernel
class ISA_kernel:
    img_name = ""                 # image name                          (mandatory argument)
    path_to_config = ""           # path to the kernel config file      (mandatory argument)

# filesystem
class ISA_filesystem:
    img_name = ""                 # image name                          (mandatory argument)
    type = ""                     # filesystem type
    path_to_fs = ""               # path to the fs location             (mandatory argument)

# configuration of ISAFW
# if both whitelist and blacklist is empty, all avaliable plugins will be used
# if whitelist has entries, then only whitelisted plugins will be used from a set of avaliable plugins
# if blacklist has entries, then the specified plugins won't be used even if avaliable and even if specified in whitelist
class ISA_config:
    plugin_whitelist = ""         # comma separated list of plugins to whitelist
    plugin_blacklist = ""         # comma separated list of plugins to blacklist
    proxy = ""                    # proxy settings
    reportdir = ""                # location of produced reports
    logdir = ""                   # location of produced logs
    timestamp = ""                # timestamp of the build provided by build system
    full_reports = False          # produce full reports for plugins, False by default
    machine = ""                  # name of machine build is produced for


class ISA:
    def __init__(self, ISA_config):
        self.ISA_config = ISA_config
        for name in isaplugins.__all__:
            plugin = getattr(isaplugins, name)
            try:
                # see if the plugin has a 'init' attribute
                register_plugin = plugin.init
            except:
                print("Error in calling init() for plugin " + plugin.getPluginName())
                print("Error info: ", sys.exc_info())
                print("Skipping this plugin")
                continue           
            else:
                if self.ISA_config.plugin_whitelist and plugin.getPluginName() not in self.ISA_config.plugin_whitelist:
                    continue
                if self.ISA_config.plugin_blacklist and plugin.getPluginName() in self.ISA_config.plugin_blacklist:
                    continue
                try:
                    register_plugin(ISA_config)
                except:
                    print("Exception in plugin init: ", sys.exc_info())

    def process_package(self, ISA_package):
        for name in isaplugins.__all__:
            plugin = getattr(isaplugins, name)
            try:
                # see if the plugin has a 'process_package' attribute
                process_package = plugin.process_package
            except AttributeError:
                # if it doesn't, it is ok, won't call this plugin
                pass
            else:
                if self.ISA_config.plugin_whitelist and plugin.getPluginName() not in self.ISA_config.plugin_whitelist:
                    continue
                if self.ISA_config.plugin_blacklist and plugin.getPluginName() in self.ISA_config.plugin_blacklist:
                    continue
                try:
                    process_package(ISA_package)
                except:
                    print("Exception in plugin: ", sys.exc_info())

    def process_pkg_list(self, ISA_pkg_list):
        for name in isaplugins.__all__:
            plugin = getattr(isaplugins, name)
            try:
                # see if the plugin has a 'process_pkg_list' attribute
                process_pkg_list = plugin.process_pkg_list
            except AttributeError:
                # if it doesn't, it is ok, won't call this plugin
                pass
            else:
                if self.ISA_config.plugin_whitelist and plugin.getPluginName() not in self.ISA_config.plugin_whitelist:
                    continue
                if self.ISA_config.plugin_blacklist and plugin.getPluginName() in self.ISA_config.plugin_blacklist:
                    continue
                try:
                    process_pkg_list(ISA_pkg_list)
                except:
                    print("Exception in plugin: ", sys.exc_info())

    def process_kernel(self, ISA_kernel):
        for name in isaplugins.__all__:
            plugin = getattr(isaplugins, name)
            try:
                # see if the plugin has a 'process_kernel' attribute
                process_kernel = plugin.process_kernel
            except AttributeError:
                # if it doesn't, it is ok, won't call this plugin
                pass
            else:
                if self.ISA_config.plugin_whitelist and plugin.getPluginName() not in self.ISA_config.plugin_whitelist:
                    continue
                if self.ISA_config.plugin_blacklist and plugin.getPluginName() in self.ISA_config.plugin_blacklist:
                    continue
                try:
                    process_kernel(ISA_kernel)
                except:
                    print("Exception in plugin: ", sys.exc_info())

    def process_filesystem(self, ISA_filesystem):
        for name in isaplugins.__all__:
            plugin = getattr(isaplugins, name)
            try:
                # see if the plugin has a 'process_filesystem' attribute
                process_filesystem = plugin.process_filesystem
            except AttributeError:
                # if it doesn't, it is ok, won't call this plugin
                pass
            else:
                if self.ISA_config.plugin_whitelist and plugin.getPluginName() not in self.ISA_config.plugin_whitelist:
                    continue
                if self.ISA_config.plugin_blacklist and plugin.getPluginName() in self.ISA_config.plugin_blacklist:
                    continue
                try:
                    process_filesystem(ISA_filesystem)
                except:
                    print("Exception in plugin: ", sys.exc_info())

    def process_report(self):
        for name in isaplugins.__all__:
            plugin = getattr(isaplugins, name)
            try:
                # see if the plugin has a 'process_report' attribute
                process_report = plugin.process_report
            except AttributeError:
                # if it doesn't, it is ok, won't call this plugin
                pass
            else:
                if self.ISA_config.plugin_whitelist and plugin.getPluginName() not in self.ISA_config.plugin_whitelist:
                    continue
                if self.ISA_config.plugin_blacklist and plugin.getPluginName() in self.ISA_config.plugin_blacklist:
                    continue
                try:
                    process_report()
                except:
                    print("Exception in plugin: ", sys.exc_info())



