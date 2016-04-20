# Known issues and future work

For the latest list of issues in the meta-swupd layer, please see the Yocto
Project Bugzilla:
https://bugzilla.yoctoproject.org/buglist.cgi?quicksearch=[meta-swupd]&list_id=577685

* refuses to overwrite generated data — because the act of generating swupd
updates is time-consuming meta-swupd, by design, refuses to overwrite an
existing update stream warning that the `OS_VERSION` number should be
incremented.
* hardlinks and extended attributes — there's a bug in
[pseudo](https://www.yoctoproject.org/tools-resources/projects/pseudo) which
results in the extended attributes for a hardlink being incorrectly associated
with the directory entry, rather than the inode. See [bug #9317](https://bugzilla.yoctoproject.org/show_bug.cgi?id=9317)
* potentially copies a lot of duplicate files — when copying bundle contents
around it's very likely that the same file will exist in the swupd working
directory multiple times. We may be able to make this less disk space intensive
by using a utility like hardlink to deduplicate identical files. See [bug #9189](https://bugzilla.yoctoproject.org/show_bug.cgi?id=9189)
* copies then deletes, rather than just copying — the current/initial
implementation copies the entire mega-image rootfs for each bundle chroot-like
directory and then prunes away unwanted files. It will be much more efficient to
only copy the files which are required in the first instance. See [bug #9325](https://bugzilla.yoctoproject.org/show_bug.cgi?id=9325)
* Various other performance issues including `system()` calls in swupd-server
resulting in slow operation as pseudo is loaded multiple times [bug #9449](https://bugzilla.yoctoproject.org/show_bug.cgi?id=9449), inefficient
algorithm for determining previous OS versions [bug #9322](https://bugzilla.yoctoproject.org/show_bug.cgi?id=9322), sequential calls
to `swupd_make_pack` [bug #9224](https://bugzilla.yoctoproject.org/show_bug.cgi?id=9224).
