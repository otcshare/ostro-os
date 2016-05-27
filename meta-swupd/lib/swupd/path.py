import oe.path


def copyxattrfiles(d, filelist, src, dst):
    import subprocess

    def pathtostring(path):
        return path.replace('/', '-')

    bb.utils.mkdirhier(dst)
    files = sorted(filelist)

    copyfile = '%s/copyxattrfiles-%s-%s.txt' % (d.getVar('WORKDIR', True), pathtostring(src), pathtostring(dst))
    if os.path.exists(copyfile):
        os.remove(copyfile)
    with open(copyfile, 'w') as fdest:
        fdest.write('-C%s\n' % src)
        for f in files:
            fdest.write('%s\n' % f)

    cmd = "tar --xattrs --xattrs-include='*' --no-recursion -cf - -T %s -p | tar -p --xattrs --xattrs-include='*' -xf - -C %s" % (copyfile, dst)
    oe.path.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
    os.remove(copyfile)


def remove_empty_directories(tree):
    for dir, _, _ in os.walk(tree, topdown=False):
        try:
            os.rmdir(dir)
        except OSError as err:
            bb.debug(4, 'Not removing %s (it is probably not empty): %s' % (dir, err.strerror))
