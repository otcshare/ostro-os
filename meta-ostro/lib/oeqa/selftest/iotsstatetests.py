import datetime
import unittest
import os
import re
import shutil
import glob
import subprocess

import oeqa.utils.ftools as ftools
from oeqa.selftest.base import oeSelfTest
from oeqa.utils.commands import runCmd, bitbake, get_bb_var, get_test_layer
from oeqa.selftest.sstate import SStateBase
from oeqa.utils.decorators import testcase
import oeqa.utils.ftools as ftools

class SStateTests(SStateBase):

    def test_sstate_samesigs(self):
        """
        The sstate checksums off allarch packages should be independent of whichever 
        MACHINE is set. Check this using bitbake -S.
        Also, rather than duplicate the test, check nativesdk stamps are the same between
        the two MACHINE values.
        Also, when building for multiple machines which share tune flag specific packages,
        those packages also need to have identical signatures.
        Based on oeqa.selftest.sstatetests.SStateTests.test_sstate_allarch_samesigs and
        extended to cover all Ostro OS machines.
        """

        topdir = get_bb_var('TOPDIR')
        targetos = get_bb_var('TARGET_OS')
        targetvendor = get_bb_var('TARGET_VENDOR')
        libcappend = get_bb_var('TCLIBCAPPEND')
        # Select subset of the machines to speed up testing.
        # Edison/intel-core2-32 are particularly sensitive.
        machines = "edison intel-quark intel-core2-32 intel-corei7-64 beaglebone".split()
        # machines = "edison intel-core2-32".split()
        first = machines[0]
        workdir = os.getcwd()
        try:
            pending = []
            for machine in machines:
                builddir = '%s/build-%s' % (topdir, machine)
                os.mkdir(builddir)
                self.track_for_cleanup(builddir)
                os.chdir(builddir)
                shutil.copytree('../conf', 'conf')
                ftools.write_file('conf/selftest.inc', """
TMPDIR = \"%s/tmp-sstatesamehash-%s\"
MACHINE = \"%s\"
""" % (topdir, machine, machine))
                # Comment out to debug with bitbake-diffstat after running the test.
                # In that case, remember to "rm -r tmp-*" before the next run.
                self.track_for_cleanup(topdir + "/tmp-sstatesamehash-%s%s" % (machine, libcappend))
                # Replace build targets with individual recipes to investigate just those.
                pending.append((machine, subprocess.Popen('bitbake world meta-toolchain -S none'.split(),
                                                          stdout=open('%s/bitbake.log' % builddir, 'w'),
                                                          stderr=subprocess.STDOUT)))
            for machine, p in pending:
                returncode = p.wait()
                if returncode:
                    raise AssertionError("bitbake failed for machine %s with return code %d:\n%s" %
                                         (machine, returncode, open('%s/build-%s/bitbake.log' % (topdir, machine)).read()))
        finally:
            os.chdir(workdir)

        def get_hashes(d, subdir):
            f = {}
            for root, dirs, files in os.walk(os.path.join(d, subdir)):
                for name in files:
                    # meta-toolchain depends on cross-canadian.
                    # Not sure about adt-installer. Hash is different, but bitbake-diffstat
                    # shows no difference.
                    # do_deploy is allowed to differ, it just as a performance impact because of
                    # unnecessary rebuilding (minor in our case, not many recipes hit this).
                    if "meta-environment" in root or "cross-canadian" in root or \
                       "do_populate_adt" in name and "adt-installer" in root or \
                       "do_populate_sdk" in name and "meta-toolchain" in root or \
                       "do_build" in name or \
                       "do_deploy" in name:
                        continue
                    components = name.split('.sigdata.')
                    # Map from 'all-ostro-linux/1_1.04-r4.do_build' to '95c22ae3e1c81cdc116db37b68db10be'.
                    # All tasks that are shared by different machines must have the same hash.
                    f[os.path.join(os.path.relpath(root, d), components[0])] = ''.join(components[1:])
            return f

        # Will be found when building meta-toolchain, otherwise it won't.
        nativesdkdir = glob.glob(topdir + ("/tmp-sstatesamehash-%s%s/stamps/*-nativesdk*-linux" % (first, libcappend)))
        if nativesdkdir:
            nativesdkdir = os.path.basename(nativesdkdir[0])
        hashes = {}
        tasks = set()
        for machine in machines:
            hashes[machine] = {}
            # Only some some packages are expected to have the same signature.
            subdirs = ["all" + targetvendor + "-" + targetos, # allarch
                       "core2-32" + targetvendor + "-" + targetos, # shared between edison and intel-core2-32
                   ]
            if nativesdkdir:
                subdirs.append(nativesdkdir)
            for subdir in subdirs:
                hashes[machine].update(get_hashes(topdir + ("/tmp-sstatesamehash-%s%s/stamps" % (machine, libcappend)), subdir))
            tasks.update(hashes[machine].keys())
        errors = ['Machines have different hashes:']
        analysis = []
        tasks = list(tasks)
        tasks.sort()
        for task in tasks:
            # Find all machines sharing the same value.
            values = {}
            for machine in machines:
                value = hashes[machine].get(task, None)
                if value:
                    values.setdefault(value, []).append(machine)
            values = sorted(values.items())
            if len(values) > 1:
                errors.append('Not the same hash for ' + task + ': ' +
                              ' '.join(['/'.join(m) + '=' + v for v, m in values]))
                # Pick the initial two values and the first machine in each where
                # the task differed and compare the signatures.
                cmd = "set -x; bitbake-diffsigs tmp-sstatesamehash-*%s*/stamps/*%s.* tmp-sstatesamehash-*%s*/stamps/*%s.*" % \
                (values[0][1][0], task,
                 values[1][1][0], task)
                p = subprocess.Popen(cmd,
                                     shell=True,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
                stdout, stderr = p.communicate()
                analysis.append(stdout.decode("utf-8"))
        if len(errors) > 1:
            # If this fails, it often fails for a whole range of tasks where one depends on
            # the other. In this example, only the original source file was different:
            #
            # AssertionError: False is not true : Machines have different hashes:
            # Not the same hash for all-poky-linux/initramfs-boot/1.0-r2.do_compile: intel-core2-32=1efd21ed2f11a4a2aef1ade99e0ae523 edison=d4aa4f356187f0902cd5b9e1fed250c4
            # ...
            # Not the same hash for all-ostro-linux/initramfs-boot/1.0-r2.do_fetch: edison=82a397e985e2c570714ab7dfa3e21a6c intel-core2-32=79b455328b0b298423cf52582cc12c7c
            # ...
            self.assertTrue(False, msg='\n'.join(errors) + '\n\n' + '\n\n'.join(analysis))
