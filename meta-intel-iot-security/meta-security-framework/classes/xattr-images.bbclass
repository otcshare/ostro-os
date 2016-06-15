# Both Smack and IMA/EVM rely on xattrs. Inheriting this class ensures
# that these xattrs get preserved in tar and jffs2 images.
#
# It also fixes the rootfs so that the content of directories with
# SMACK::TRANSMUTE is correctly labelled. This is because pseudo does
# not know the special semantic of SMACK::TRANSMUTE and omits the
# updating of the Smack label when creating entries inside such a directory,
# for example /etc (see base-files_%.bbappend). Without the fixup,
# files already installed during the image creation would have different (and
# wrong) Smack labels.

# xattr support is expected to be compiled into mtd-utils. We just need to
# use it.
EXTRA_IMAGECMD_jffs2_append = " --with-xattr"

# By default, OE-core uses tar from the host, which may or may not have the
# --xattrs parameter which was introduced in 1.27. For image building we
# use a recent enough tar instead.
#
# The GNU documentation does not specify whether --xattrs-include is necessary.
# In practice, it turned out to be not needed when creating archives and
# required when extracting, but it seems prudent to use it in both cases.
IMAGE_DEPENDS_tar_append = " tar-replacement-native"
EXTRANATIVEPATH += "tar-native"
IMAGE_CMD_TAR = "tar --xattrs --xattrs-include=*"

xattr_images_fix_transmute[dirs] = "${IMAGE_ROOTFS}"
python xattr_images_fix_transmute () {
    # The recursive updating of the Smack label ensures that each entry
    # has the label set for its parent directories if one of those was
    # marked as transmuting.
    #
    # In addition, "_" is set explicitly on everything that would not
    # have a label otherwise. This is a workaround for tools like swupd
    # which transfers files from a rootfs onto a target device where Smack
    # is active: on the target, each file gets assigned a label, typically
    # the one from the process which creates it. swupd (or rather, the tools
    # it is currently built on) knows how to set security.SMACK64="_" when
    # it is set on the original files, but it does not know that it needs
    # to remove that xattr when not set.
    import os
    import errno

    if getattr(os, 'getxattr', None):
        # Python 3: os has xattr support.
        def lgetxattr(f, attr):
            try:
                value = os.getxattr(f, attr, follow_symlinks=False)
                return value.decode('utf8')
            except OSError as ex:
                if ex.errno == errno.ENODATA:
                    return None

        def lsetxattr(f, attr, value):
            os.setxattr(f, attr.encode('utf8'), value.encode('utf8'), follow_symlinks=False)
    else:
        # Python 2: xattr support only in xattr module.
        #
        # Cannot use the 'xattr' module, it is not part of a standard Python
        # installation. Instead re-implement using ctypes. Only has to be good
        # enough for xattrs that are strings. Always operates on the symlinks themselves,
        # not what they point to.
        import ctypes

        # We cannot look up the xattr functions inside libc. That bypasses
        # pseudo, which overrides these functions via LD_PRELOAD. Instead we have to
        # find the function address and then create a ctypes function from it.
        libdl = ctypes.CDLL("libdl.so.2")
        _dlsym = libdl.dlsym
        _dlsym.restype = ctypes.c_void_p
        RTLD_DEFAULT = ctypes.c_void_p(0)
        _lgetxattr = ctypes.CFUNCTYPE(ctypes.c_ssize_t, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t,
                    use_errno=True)(_dlsym(RTLD_DEFAULT, 'lgetxattr'))
        _lsetxattr = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int,
                    use_errno=True)(_dlsym(RTLD_DEFAULT, 'lsetxattr'))

        def lgetxattr(f, attr):
            len = 32
            while True:
                buffer = ctypes.create_string_buffer('\000' * len)
                res = _lgetxattr(f, attr, buffer, ctypes.c_size_t(len))
                if res >= 0:
                    return buffer.value
                else:
                    error = ctypes.get_errno()
                    if ctypes.get_errno() == errno.ERANGE:
                        len *= 2
                    elif error == errno.ENODATA:
                        return None
                    else:
                        raise IOError(error, 'lgetxattr(%s, %s): %d = %s = %s' %
                                             (f, attr, error, errno.errorcode[error], os.strerror(error)))

        def lsetxattr(f, attr, value):
            res = _lsetxattr(f, attr, value, ctypes.c_size_t(len(value)), ctypes.c_int(0))
            if res != 0:
                error = ctypes.get_errno()
                raise IOError(error, 'lsetxattr(%s, %s, %s): %d = %s = %s' %
                                     (f, attr, value, error, errno.errorcode[error], os.strerror(error)))

    def visit(path, deflabel, deftransmute):
        isrealdir = os.path.isdir(path) and not os.path.islink(path)
        curlabel = lgetxattr(path, 'security.SMACK64')
        transmute = lgetxattr(path, 'security.SMACK64TRANSMUTE') == 'TRUE'

        if not curlabel:
            # Since swupd doesn't remove the label from an updated file assigned by
            # the target device's kernel upon unpacking the file from an update,
            # we have to set the floor label explicitly even though it is the default label
            # and thus adding it would create additional overhead. Otherwise this
            # would result in hash mismatches reported by `swupd verify`.
            lsetxattr(path, 'security.SMACK64', deflabel)
            if not transmute and deftransmute and isrealdir:
                lsetxattr(path, 'security.SMACK64TRANSMUTE', 'TRUE')

        # Identify transmuting directories and change the default Smack
        # label inside them. In addition, directories themselves must become
        # transmuting.
        if isrealdir:
            if transmute:
                deflabel = lgetxattr(path, 'security.SMACK64')
                deftransmute = True
                if deflabel is None:
                    raise RuntimeError('%s: transmuting directory without Smack label' % path)
            elif curlabel:
                # Directory with explicit label set and not transmuting => do not
                # change the content unless we run into another transmuting directory.
               deflabel = '_'
               deftransmute = False

            for entry in os.listdir(path):
                visit(os.path.join(path, entry), deflabel, deftransmute)

    visit('.', '_', False)
}
# Same logic as in ima-evm-rootfs.bbclass: try to run as late as possible.
IMAGE_PREPROCESS_COMMAND_append_smack = " xattr_images_fix_transmute ; "