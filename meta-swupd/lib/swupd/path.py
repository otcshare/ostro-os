import oe.path


def copyxattrtree(src, dst):
    """
    Copy all of the files in src to dst preserving extended attributes

    src -- the source to copy from
    dst -- the destination to copy to
    """
    import subprocess
    cmd = "bsdtar -cf - -C %s . | bsdtar -xf - -C %s" % (src, dst)
    subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)


def copyxattrfiles(d, filelist, src, dst, archive=False):
    """
    copy files preserving extended attributes

    d -- the bitbake data store
    filelist -- a list of file paths
    src -- where to copy the files from (directory or archive, auto-detected)
    dst -- where to copy the files to (directory or archive, depending on archive parameter)
    archive -- create archive at dst instead of writing into that directory
    """
    import subprocess
    import tempfile

    bb.utils.mkdirhier(os.path.dirname(dst) if archive else dst)
    files = sorted(filelist)

    fromdir = os.path.isdir(src)
    workdir = d.getVar('WORKDIR', True)
    fd, copyfile = tempfile.mkstemp(dir=workdir)
    os.close(fd)
    with open(copyfile, 'w') as fdest:
        for f in files:
            fdest.write('%s\n' % f)

    if fromdir:
        if archive:
            cmd = "bsdtar --no-recursion -C %s -zcf %s -T %s -p" % (src, dst, copyfile)
        else:
            cmd = "bsdtar --no-recursion -C %s -cf - -T %s -p | bsdtar -p -xf - -C %s" % (src, copyfile, dst)
    else:
        if archive:
            # archive->archive not needed at the moment and cannot be done easily,
            # because although bsdtar supports reading from an archive with @<archive>,
            # filtering entries isn't supported in that mode.
            bb.fatal('Extracting files from an archive and writing into an archive not implemented yet.')
        else:
            cmd = "bsdtar --no-recursion -C %s -xf %s -T %s" % (dst, src, copyfile)
    output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    if output:
        bb.fatal('Unexpected output from the following command:\n%s\n%s' % (cmd, output))
    os.remove(copyfile)


def remove_empty_directories(tree):
    """
    remove any empty sub-directories of the passed path

    tree -- the root of the tree whose empty children should be deleted
    """
    for dir, _, _ in os.walk(tree, topdown=False):
        try:
            os.rmdir(dir)
        except OSError as err:
            bb.debug(4, 'Not removing %s (it is probably not empty): %s' % (dir, err.strerror))
