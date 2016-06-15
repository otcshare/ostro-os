# This moves files out of /etc. It gets applied both
# to individual packages (to avoid or at least catch problems
# early) as well as the entire rootfs (to catch files not
# contained in packages).

# Package QA check which greps for known bad paths which should
# not be used anymore, like files which used to be in /etc and
# got moved elsewhere.
STATELESS_DEPRECATED_PATHS ??= ""

# Check not activated by default, can be done in distro with:
# ERROR_QA += "stateless"

# If set to True, a recipe gets configured with
# sysconfdir=${datadir}/defaults. If set to a path, that
# path is used instead. In both cases, /etc typically gets
# ignored and the component no longer can be configured by
# the device admin.
STATELESS_RELOCATE ??= "False"

# A space-separated list of recipes which may contain files in /etc.
STATELESS_PN_WHITELIST ??= ""

# A space-separated list of shell patterns. Anything matching a
# pattern is allowed in /etc. Changing this influences the QA check in
# do_package and do_rootfs.
STATELESS_ETC_WHITELIST ??= "${STATELESS_ETC_DIR_WHITELIST}"

# A subset of STATELESS_ETC_WHITELIST which also influences do_install
# and determines which directories to keep.
STATELESS_ETC_DIR_WHITELIST ??= ""

# A space-separated list of entries in /etc which need to be moved
# away. Default is to move into ${datadir}/doc/${PN}/etc. The actual
# new name can also be given with old-name=new-name, as in
# "pam.d=${datadir}/pam.d".
STATELESS_MV ??= ""

# A space-separated list of entries in /etc which can be removed
# entirely.
STATELESS_RM ??= ""

# Same as the previous ones, except that they get applied to the rootfs
# before running ROOTFS_POSTPROCESS_COMMANDs.
STATELESS_RM_ROOTFS ??= ""
STATELESS_MV_ROOTFS ??= ""

###########################################################################

def stateless_is_whitelisted(etcentry, whitelist):
    import fnmatch
    for pattern in whitelist:
        if fnmatch.fnmatchcase(etcentry, pattern):
            return True
    return False

def stateless_mangle(d, root, docdir, stateless_mv, stateless_rm, dirwhitelist, is_package):
    import os
    import errno
    import shutil

    # Remove content that is no longer needed.
    for entry in stateless_rm:
        old = os.path.join(root, 'etc', entry)
        if os.path.exists(old) or os.path.islink(old):
            bb.note('stateless: removing %s' % old)
            if os.path.isdir(old) and not os.path.islink(old):
                shutil.rmtree(old)
            else:
                os.unlink(old)

    # Move away files. Default target is docdir, but others can
    # be set by appending =<new name> to the entry, as in
    # tmpfiles.d=libdir/tmpfiles.d
    for entry in stateless_mv:
        paths = entry.split('=', 1)
        etcentry = paths[0]
        old = os.path.join(root, 'etc', etcentry)
        if os.path.exists(old) or os.path.islink(old):
            if len(paths) > 1:
                new = root + paths[1]
            else:
                new = os.path.join(docdir, entry)
            destdir = os.path.dirname(new)
            bb.utils.mkdirhier(destdir)
            # Also handles moving of directories where the target already exists, by
            # moving the content. When moving a relative symlink the target gets updated.
            def move(old, new):
                bb.note('stateless: moving %s to %s' % (old, new))
                if os.path.isdir(new):
                    for entry in os.listdir(old):
                        move(os.path.join(old, entry), os.path.join(new, entry))
                    os.rmdir(old)
                else:
                    os.rename(old, new)
            move(old, new)

    # Remove /etc if all that's left are directories.
    # Some directories are expected to exists (for example,
    # update-ca-certificates depends on /etc/ssl/certs),
    # so if a directory is white-listed, it does not get
    # removed.
    etcdir = os.path.join(root, 'etc')
    def tryrmdir(path):
        if is_package and \
           path.endswith('/etc/modprobe.d') or \
           path.endswith('/etc/modules-load.d'):
           # Expected to exist by kernel-module-split.bbclass
           # which will clean it itself.
           return
        if stateless_is_whitelisted(path[len(etcdir) + 1:], dirwhitelist):
           bb.note('stateless: keeping white-listed directory %s' % path)
           return
        bb.note('stateless: removing dir %s' % path)
        try:
            os.rmdir(path)
        except OSError as ex:
            bb.note('stateless: removing dir failed: %s' % ex)
            if ex.errno != errno.ENOTEMPTY:
                 raise
    if os.path.isdir(etcdir):
        for root, dirs, files in os.walk(etcdir, topdown=False):
            for dir in dirs:
                path = os.path.join(root, dir)
                if os.path.islink(path):
                    files.append(dir)
                else:
                    tryrmdir(path)
            for file in files:
                bb.note('stateless: /etc not empty: %s' % os.path.join(root, file))
        tryrmdir(etcdir)


# Modify ${D} after do_install and before do_package resp. do_populate_sysroot.
do_install[postfuncs] += "stateless_mangle_package"
python stateless_mangle_package() {
    pn = d.getVar('PN', True)
    if pn in (d.getVar('STATELESS_PN_WHITELIST', True) or '').split():
        return
    installdir = d.getVar('D', True)
    docdir = installdir + os.path.join(d.getVar('docdir', True), pn, 'etc')
    whitelist = (d.getVar('STATELESS_ETC_DIR_WHITELIST', True) or '').split()

    stateless_mangle(d, installdir, docdir,
                     (d.getVar('STATELESS_MV', True) or '').split(),
                     (d.getVar('STATELESS_RM', True) or '').split(),
                     whitelist,
                     True)
}

# Check that nothing is left in /etc.
PACKAGEFUNCS += "stateless_check"
python stateless_check() {
    pn = d.getVar('PN', True)
    if pn in (d.getVar('STATELESS_PN_WHITELIST', True) or '').split():
        return
    whitelist = (d.getVar('STATELESS_ETC_WHITELIST', True) or '').split()
    import os
    sane = True
    for pkg, files in pkgfiles.items():
        pkgdir = os.path.join(d.getVar('PKGDEST', True), pkg)
        for file in files:
            targetfile = file[len(pkgdir):]
            if targetfile.startswith('/etc/') and \
               not stateless_is_whitelisted(targetfile[len('/etc/'):], whitelist):
                bb.warn("stateless: %s should not contain %s" % (pkg, file))
                sane = False
    if not sane:
        d.setVar("QA_SANE", "")
}

QAPATHTEST[stateless] = "stateless_qa_check_paths"
def stateless_qa_check_paths(file,name, d, elf, messages):
    """
    Check for deprecated paths that should no longer be used.
    """

    if os.path.islink(file):
        return

    # Ignore ipk and deb's CONTROL dir
    if file.find(name + "/CONTROL/") != -1 or file.find(name + "/DEBIAN/") != -1:
        return

    bad_paths = d.getVar('STATELESS_DEPRECATED_PATHS', True).split()
    if bad_paths:
        import subprocess
        import pipes
        cmd = "strings -a %s | grep -F '%s' | sort -u" % (pipes.quote(file), '\n'.join(bad_paths))
        s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = s.communicate()
        # Cannot check return code, some of them may get lost because we use a pipe
        # and cannot rely on bash's pipefail. Instead just check for unexpected
        # stderr content.
        if stderr:
            bb.fatal('Checking %s for paths deprecated via STATELESS_DEPRECATED_PATHS failed:\n%s' % (file, stderr))
        if stdout:
            package_qa_add_message(messages, "stateless", "%s: %s contains paths deprecated in a stateless configuration: %s" % (name, package_qa_clean_path(file, d), stdout))
do_package_qa[vardeps] += "stateless_qa_check_paths"

python () {
    # The bitbake cache must be told explicitly that changes in the
    # directories have an effect on the recipe. Otherwise adding
    # or removing patches or whole directories does not trigger
    # re-parsing and re-building.
    import os
    patchdir = d.expand('${STATELESS_PATCHES_BASE}/${PN}')
    bb.parse.mark_dependency(d, patchdir)
    if os.path.isdir(patchdir):
        patches = os.listdir(patchdir)
        if patches:
            filespath = d.getVar('FILESPATH', True)
            d.setVar('FILESPATH', filespath + ':' + patchdir)
            srcuri = d.getVar('SRC_URI', True)
            d.setVar('SRC_URI', srcuri + ' ' + ' '.join(['file://' + x for x in sorted(patches)]))

    # Dynamically reconfigure the package to use /usr instead of /etc for
    # configuration files.
    relocate = d.getVar('STATELESS_RELOCATE', True)
    if relocate != 'False':
        defaultsdir = d.expand('${datadir}/defaults') if relocate == 'True' else relocate
        d.setVar('sysconfdir', defaultsdir)
        d.setVar('EXTRA_OECONF', d.getVar('EXTRA_OECONF', True) + " --sysconfdir=" + defaultsdir)
}

# Several post-install scripts modify /etc.
# For example:
# /etc/shells - gets extended when installing a shell package
# /etc/passwd - adduser in postinst extends it
# /etc/systemd/system - has several .wants entries
#
# We fix this directly after the write_image_manifest command
# in the ROOTFS_POSTUNINSTALL_COMMAND.
#
# However, that is very late, so changes made by a ROOTFS_POSTPROCESS_COMMAND
# (like setting an empty root password) become part of the system,
# which might not be intended in all cases.
#
# It would be better to do this directly after installing with
# ROOTFS_POSTINSTALL_COMMAND += "stateless_mangle_rootfs;"
# However, opkg then becomes unhappy and causes failures in the
# *_manifest commands which get executed later:
#
# ERROR: Cannot get the installed packages list. Command '.../opkg -f .../ostro-image-minimal/1.0-r0/opkg.conf -o .../ostro-image-minimal/1.0-r0/rootfs  --force_postinstall --prefer-arch-to-version   status' returned 0 and stderr:
# Collected errors:
#  * file_md5sum_alloc: Failed to open file .../ostro-image-minimal/1.0-r0/rootfs/etc/hosts: No such file or directory.
#
# ERROR: Function failed: write_package_manifest
#
# TODO: why does opkg complain? /etc/hosts is listed in CONFFILES of netbase,
# so it should be valid to remove it. If we can fix that and ensure that
# all /etc files are marked as CONFFILES (perhaps by adding that as
# default for all packages), then we can use ROOTFS_POSTINSTALL_COMMAND
# again.
ROOTFS_POSTUNINSTALL_COMMAND_append = "stateless_mangle_rootfs;"

python stateless_mangle_rootfs () {
    pn = d.getVar('PN', True)
    if pn in (d.getVar('STATELESS_PN_WHITELIST', True) or '').split():
        return

    rootfsdir = d.getVar('IMAGE_ROOTFS', True)
    docdir = rootfsdir + d.getVar('datadir', True) + '/doc/etc'
    whitelist = (d.getVar('STATELESS_ETC_WHITELIST', True) or '').split()
    stateless_mangle(d, rootfsdir, docdir,
                     (d.getVar('STATELESS_MV_ROOTFS', True) or '').split(),
                     (d.getVar('STATELESS_RM_ROOTFS', True) or '').split(),
                     whitelist,
                     False)
    import os
    etcdir = os.path.join(rootfsdir, 'etc')
    valid = True
    for dirpath, dirnames, filenames in os.walk(etcdir):
        for entry in filenames + [x for x in dirnames if os.path.islink(x)]:
            fullpath = os.path.join(dirpath, entry)
            etcentry = fullpath[len(etcdir) + 1:]
            if not stateless_is_whitelisted(etcentry, whitelist):
                bb.warn('stateless: rootfs should not contain %s' % fullpath)
                valid = False
    if not valid:
        bb.fatal('stateless: /etc not empty')
}
