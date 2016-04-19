FILESEXTRAPATHS_prepend := "${THISDIR}/files:"

SRC_URI = "git://github.com/gfto/toybox.git;protocol=https"
PV = "0.7.0+git-${SRCREV}"
SRCREV = "9fcaca8434ece1afcc9982c18a86cf12ac9af508"
S ="${WORKDIR}/git"

DEPENDS_append_smack = " smack attr"
do_configure_append_smack () {
    # Enable smack in toybox.
    sed -e 's/# CONFIG_TOYBOX_SMACK is not set/CONFIG_TOYBOX_SMACK=y/' -i .config

    # Enable LSM support. Not immediately obvious where that is relevant
    # (some Smack support also works without it), but it is better to
    # set this consistently.
    sed -e 's/CONFIG_TOYBOX_LSM_NONE=y/# CONFIG_TOYBOX_LSM_NONE is not set/' -i .config
}

# Toybox sh is not enabled by default and too incomplete to execute
# the initramfs-framework scripts. Therefore dash is needed in
# addition to toybox when replacing busybox.
RDEPENDS_${PN} += "dash"

# "awk" is expected by initramfs-framework. Toybox does not have it at all.
# Depending on gawk leads to a dependency on an old gawk or a recent one
# under GPLv3. For now that's okay, but it would be better to not depend
# on awk in initramfs-framework.
RDEPENDS_${PN} += "gawk"

# toybox mount ignores mount options.
RDEPENDS_${PN} += "util-linux-mount"

# "tr" is apparently still incomplete, but good enough for
# initramfs-framework.
do_configure_append () {
    sed -e 's/# CONFIG_TR is not set/CONFIG_TR=y/' -i .config
}

# We need a passwd command which understands the Ostro OS stateless
# setup. Only passwd from "shadow" works with that at the moment.
do_configure_append () {
    sed -e 's/CONFIG_PASSWD=y/# CONFIG_PASSWD is not set/' -i .config
}
RDEPENDS_${PN} += "shadow"

# "mesg" is expected by the default .profile. Avoid confusing errors
# by providing a stub. mesg is used to control whether other users
# can write to a users terminal. Ostro OS isn't a multi-user, interactive
# OS, so that loss of functionality isn't important.
SRC_URI += "file://mesg"
do_install_append () {
    install -d ${D}/${bindir}
    install ${WORKDIR}/mesg ${D}/${bindir}
}

# grep produces no output. Fall back to sed from coreutils. This
# works only in Ostro because normally, pulling in coreutils would
# override all of Toybox. But in ostro-image.bbclass, Toybox gets a priority
# boost that prevents that.
#
# TODO: investigate sed failure. Can be done by symlinking to it,
# because the grep toy is still in the binary.
do_compile_append () {
    grep -v -w grep toybox.links >toybox.links_ && mv toybox.links_ toybox.links
}
RDEPENDS_${PN}_append = " grep"

# Sets the compiler for native tools.
# Necessary for building generated/instlist when Smack is enabled.
HOSTCC="${BUILD_CC} ${BUILD_CFLAGS} ${BUILD_CPPFLAGS} ${BUILD_LDFLAGS}"
export HOSTCC

# Toybox must follow OE conventions for the location of the binaries,
# otherwise update-alternatives will not work properly (at least when
# using opkg - for example, /usr/lib/opkg/alternatives/base64 can only
# deal with /usr/bin/base64 or /bin/base64, but not both).
#
# The following definition could also (should?!) be moved to OE-core.
#
# Generated with:
# for i in <rootfs of image with Toybox and coreutils>/rootfs/usr/lib/opkg/alternatives/*; do
#    echo "ALTERNATIVES_DIRECTORY[$(basename $i)] = \"$(dirname $(head -1 $i))\"";
# done |
# sort |
# sed -e 's;/usr/bin;${bindir};' -e 's;/bin;${base_bindir};' -e 's;/usr/sbin;${sbindir};' -e 's;/sbin;${base_sbindir};' | grep -v '"/'
ALTERNATIVES_DIRECTORY[acpi] = "${bindir}"
ALTERNATIVES_DIRECTORY[addr2line] = "${bindir}"
ALTERNATIVES_DIRECTORY[arch] = "${bindir}"
ALTERNATIVES_DIRECTORY[ar] = "${bindir}"
ALTERNATIVES_DIRECTORY[as] = "${bindir}"
ALTERNATIVES_DIRECTORY[awk] = "${bindir}"
ALTERNATIVES_DIRECTORY[base64] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[basename] = "${bindir}"
ALTERNATIVES_DIRECTORY[bin-lsmod] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[blkid] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[blockdev] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[bunzip2] = "${bindir}"
ALTERNATIVES_DIRECTORY[bzcat] = "${bindir}"
ALTERNATIVES_DIRECTORY[cal] = "${bindir}"
ALTERNATIVES_DIRECTORY[cat] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[catv] = "${bindir}"
ALTERNATIVES_DIRECTORY[c++filt] = "${bindir}"
ALTERNATIVES_DIRECTORY[chattr] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[chcon] = "${bindir}"
ALTERNATIVES_DIRECTORY[chfn] = "${bindir}"
ALTERNATIVES_DIRECTORY[chgrp] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[chmod] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[chown] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[chpasswd] = "${sbindir}"
ALTERNATIVES_DIRECTORY[chroot] = "${sbindir}"
ALTERNATIVES_DIRECTORY[chrt] = "${bindir}"
ALTERNATIVES_DIRECTORY[chsh] = "${bindir}"
ALTERNATIVES_DIRECTORY[chvt] = "${bindir}"
ALTERNATIVES_DIRECTORY[cksum] = "${bindir}"
ALTERNATIVES_DIRECTORY[clear] = "${bindir}"
ALTERNATIVES_DIRECTORY[cmp] = "${bindir}"
ALTERNATIVES_DIRECTORY[comm] = "${bindir}"
ALTERNATIVES_DIRECTORY[count] = "${bindir}"
ALTERNATIVES_DIRECTORY[cp] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[cpio] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[csplit] = "${bindir}"
ALTERNATIVES_DIRECTORY[cut] = "${bindir}"
ALTERNATIVES_DIRECTORY[date] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[dc] = "${bindir}"
ALTERNATIVES_DIRECTORY[dd] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[deallocvt] = "${bindir}"
ALTERNATIVES_DIRECTORY[depmod] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[df] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[diff] = "${bindir}"
ALTERNATIVES_DIRECTORY[dircolors] = "${bindir}"
ALTERNATIVES_DIRECTORY[dirname] = "${bindir}"
ALTERNATIVES_DIRECTORY[dir] = "${bindir}"
ALTERNATIVES_DIRECTORY[dmesg] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[dos2unix] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[du] = "${bindir}"
ALTERNATIVES_DIRECTORY[dwp] = "${bindir}"
ALTERNATIVES_DIRECTORY[echo] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[egrep] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[eject] = "${bindir}"
ALTERNATIVES_DIRECTORY[elfedit] = "${bindir}"
ALTERNATIVES_DIRECTORY[env] = "${bindir}"
ALTERNATIVES_DIRECTORY[expand] = "${bindir}"
ALTERNATIVES_DIRECTORY[expr] = "${bindir}"
ALTERNATIVES_DIRECTORY[factor] = "${bindir}"
ALTERNATIVES_DIRECTORY[fallocate] = "${bindir}"
ALTERNATIVES_DIRECTORY[false] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[fdisk] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[fgconsole] = "${bindir}"
ALTERNATIVES_DIRECTORY[fgrep] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[find] = "${bindir}"
ALTERNATIVES_DIRECTORY[flock] = "${bindir}"
ALTERNATIVES_DIRECTORY[fmt] = "${bindir}"
ALTERNATIVES_DIRECTORY[fold] = "${bindir}"
ALTERNATIVES_DIRECTORY[freeramdisk] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[free] = "${bindir}"
ALTERNATIVES_DIRECTORY[fsck.minix] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[fsck] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[fsfreeze] = "${sbindir}"
ALTERNATIVES_DIRECTORY[fstype] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[fsync] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[getty] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[gprof] = "${bindir}"
ALTERNATIVES_DIRECTORY[grep] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[groups] = "${bindir}"
ALTERNATIVES_DIRECTORY[gunzip] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[gzip] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[halt] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[head] = "${bindir}"
ALTERNATIVES_DIRECTORY[help] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[hexdump] = "${bindir}"
ALTERNATIVES_DIRECTORY[hexedit] = "${bindir}"
ALTERNATIVES_DIRECTORY[hostid] = "${bindir}"
ALTERNATIVES_DIRECTORY[hostname] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[hwclock] = "${bindir}"
ALTERNATIVES_DIRECTORY[id] = "${bindir}"
ALTERNATIVES_DIRECTORY[ifconfig] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[init] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[inotifyd] = "${bindir}"
ALTERNATIVES_DIRECTORY[insmod] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[install] = "${bindir}"
ALTERNATIVES_DIRECTORY[ionice] = "${bindir}"
ALTERNATIVES_DIRECTORY[iorenice] = "${bindir}"
ALTERNATIVES_DIRECTORY[iotop] = "${bindir}"
ALTERNATIVES_DIRECTORY[ip] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[javac] = "${bindir}"
ALTERNATIVES_DIRECTORY[java] = "${bindir}"
ALTERNATIVES_DIRECTORY[join] = "${bindir}"
ALTERNATIVES_DIRECTORY[killall] = "${bindir}"
ALTERNATIVES_DIRECTORY[kill] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[lastb] = "${bindir}"
ALTERNATIVES_DIRECTORY[last] = "${bindir}"
ALTERNATIVES_DIRECTORY[lbracket] = "${bindir}"
ALTERNATIVES_DIRECTORY[ld.bfd] = "${bindir}"
ALTERNATIVES_DIRECTORY[ld.gold] = "${bindir}"
ALTERNATIVES_DIRECTORY[ld] = "${bindir}"
ALTERNATIVES_DIRECTORY[link] = "${bindir}"
ALTERNATIVES_DIRECTORY[ln] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[logger] = "${bindir}"
ALTERNATIVES_DIRECTORY[login] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[logname] = "${bindir}"
ALTERNATIVES_DIRECTORY[losetup] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[lsattr] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[ls] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[lsmod] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[lspci] = "${bindir}"
ALTERNATIVES_DIRECTORY[lsusb] = "${bindir}"
ALTERNATIVES_DIRECTORY[makedevs] = "${bindir}"
ALTERNATIVES_DIRECTORY[md5sum] = "${bindir}"
ALTERNATIVES_DIRECTORY[mesg] = "${bindir}"
ALTERNATIVES_DIRECTORY[mix] = "${bindir}"
ALTERNATIVES_DIRECTORY[mkdir] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[mkfifo] = "${bindir}"
ALTERNATIVES_DIRECTORY[mkfs.minix] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[mknod] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[mkpasswd] = "${bindir}"
ALTERNATIVES_DIRECTORY[mkswap] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[mktemp] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[modinfo] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[modprobe] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[more] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[mount] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[mountpoint] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[mv] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[nbd-client] = "${bindir}"
ALTERNATIVES_DIRECTORY[nc] = "${bindir}"
ALTERNATIVES_DIRECTORY[netcat] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[newgrp] = "${bindir}"
ALTERNATIVES_DIRECTORY[nice] = "${bindir}"
ALTERNATIVES_DIRECTORY[nl] = "${bindir}"
ALTERNATIVES_DIRECTORY[nm] = "${bindir}"
ALTERNATIVES_DIRECTORY[nohup] = "${bindir}"
ALTERNATIVES_DIRECTORY[nproc] = "${bindir}"
ALTERNATIVES_DIRECTORY[nsenter] = "${bindir}"
ALTERNATIVES_DIRECTORY[objcopy] = "${bindir}"
ALTERNATIVES_DIRECTORY[objdump] = "${bindir}"
ALTERNATIVES_DIRECTORY[od] = "${bindir}"
ALTERNATIVES_DIRECTORY[oneit] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[openvt] = "${bindir}"
ALTERNATIVES_DIRECTORY[partprobe] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[passwd] = "${bindir}"
ALTERNATIVES_DIRECTORY[paste] = "${bindir}"
ALTERNATIVES_DIRECTORY[patch] = "${bindir}"
ALTERNATIVES_DIRECTORY[pathchk] = "${bindir}"
ALTERNATIVES_DIRECTORY[pgrep] = "${bindir}"
ALTERNATIVES_DIRECTORY[pidof] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[ping6] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[ping] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[pinky] = "${bindir}"
ALTERNATIVES_DIRECTORY[pivot_root] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[pkill] = "${bindir}"
ALTERNATIVES_DIRECTORY[pmap] = "${bindir}"
ALTERNATIVES_DIRECTORY[poweroff] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[printenv] = "${bindir}"
ALTERNATIVES_DIRECTORY[printf] = "${bindir}"
ALTERNATIVES_DIRECTORY[pr] = "${bindir}"
ALTERNATIVES_DIRECTORY[ps] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[ptx] = "${bindir}"
ALTERNATIVES_DIRECTORY[pwd] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[pwdx] = "${bindir}"
ALTERNATIVES_DIRECTORY[ranlib] = "${bindir}"
ALTERNATIVES_DIRECTORY[readahead] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[readelf] = "${bindir}"
ALTERNATIVES_DIRECTORY[readlink] = "${bindir}"
ALTERNATIVES_DIRECTORY[readprofile] = "${sbindir}"
ALTERNATIVES_DIRECTORY[realpath] = "${bindir}"
ALTERNATIVES_DIRECTORY[reboot] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[renice] = "${bindir}"
ALTERNATIVES_DIRECTORY[reset] = "${bindir}"
ALTERNATIVES_DIRECTORY[rev] = "${bindir}"
ALTERNATIVES_DIRECTORY[rfkill] = "${sbindir}"
ALTERNATIVES_DIRECTORY[rm] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[rmdir] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[rmmod] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[runcon] = "${bindir}"
ALTERNATIVES_DIRECTORY[runlevel] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[scp] = "${bindir}"
ALTERNATIVES_DIRECTORY[sed] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[seq] = "${bindir}"
ALTERNATIVES_DIRECTORY[setsid] = "${bindir}"
ALTERNATIVES_DIRECTORY[sha1sum] = "${bindir}"
ALTERNATIVES_DIRECTORY[sha224sum] = "${bindir}"
ALTERNATIVES_DIRECTORY[sha256sum] = "${bindir}"
ALTERNATIVES_DIRECTORY[sha384sum] = "${bindir}"
ALTERNATIVES_DIRECTORY[sha512sum] = "${bindir}"
ALTERNATIVES_DIRECTORY[sh] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[shred] = "${bindir}"
ALTERNATIVES_DIRECTORY[shuf] = "${bindir}"
ALTERNATIVES_DIRECTORY[shutdown] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[size] = "${bindir}"
ALTERNATIVES_DIRECTORY[skill] = "${bindir}"
ALTERNATIVES_DIRECTORY[sleep] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[snice] = "${bindir}"
ALTERNATIVES_DIRECTORY[sort] = "${bindir}"
ALTERNATIVES_DIRECTORY[split] = "${bindir}"
ALTERNATIVES_DIRECTORY[ssh] = "${bindir}"
ALTERNATIVES_DIRECTORY[stat] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[stdbuf] = "${bindir}"
ALTERNATIVES_DIRECTORY[strings] = "${bindir}"
ALTERNATIVES_DIRECTORY[strip] = "${bindir}"
ALTERNATIVES_DIRECTORY[stty] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[su] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[sulogin] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[sum] = "${bindir}"
ALTERNATIVES_DIRECTORY[swapoff] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[swapon] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[switch_root] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[sync] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[sysctl] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[tac] = "${bindir}"
ALTERNATIVES_DIRECTORY[tail] = "${bindir}"
ALTERNATIVES_DIRECTORY[tar] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[taskset] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[tee] = "${bindir}"
ALTERNATIVES_DIRECTORY[test] = "${bindir}"
ALTERNATIVES_DIRECTORY[timeout] = "${bindir}"
ALTERNATIVES_DIRECTORY[time] = "${bindir}"
ALTERNATIVES_DIRECTORY[top] = "${bindir}"
ALTERNATIVES_DIRECTORY[touch] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[traceroute] = "${bindir}"
ALTERNATIVES_DIRECTORY[true] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[truncate] = "${bindir}"
ALTERNATIVES_DIRECTORY[tr] = "${bindir}"
ALTERNATIVES_DIRECTORY[tsort] = "${bindir}"
ALTERNATIVES_DIRECTORY[tty] = "${bindir}"
ALTERNATIVES_DIRECTORY[ulimit] = "${bindir}"
ALTERNATIVES_DIRECTORY[umount] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[uname] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[unexpand] = "${bindir}"
ALTERNATIVES_DIRECTORY[uniq] = "${bindir}"
ALTERNATIVES_DIRECTORY[unix2dos] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[unlink] = "${bindir}"
ALTERNATIVES_DIRECTORY[unshare] = "${bindir}"
ALTERNATIVES_DIRECTORY[uptime] = "${bindir}"
ALTERNATIVES_DIRECTORY[users] = "${bindir}"
ALTERNATIVES_DIRECTORY[usleep] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[utmpdump] = "${bindir}"
ALTERNATIVES_DIRECTORY[uudecode] = "${bindir}"
ALTERNATIVES_DIRECTORY[uuencode] = "${bindir}"
ALTERNATIVES_DIRECTORY[vconfig] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[vdir] = "${bindir}"
ALTERNATIVES_DIRECTORY[vi] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[vigr] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[vim] = "${bindir}"
ALTERNATIVES_DIRECTORY[vipw] = "${base_sbindir}"
ALTERNATIVES_DIRECTORY[vmstat] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[wall] = "${bindir}"
ALTERNATIVES_DIRECTORY[watch] = "${base_bindir}"
ALTERNATIVES_DIRECTORY[wc] = "${bindir}"
ALTERNATIVES_DIRECTORY[wget] = "${bindir}"
ALTERNATIVES_DIRECTORY[which] = "${bindir}"
ALTERNATIVES_DIRECTORY[whoami] = "${bindir}"
ALTERNATIVES_DIRECTORY[who] = "${bindir}"
ALTERNATIVES_DIRECTORY[w] = "${bindir}"
ALTERNATIVES_DIRECTORY[xargs] = "${bindir}"
ALTERNATIVES_DIRECTORY[xxd] = "${bindir}"
ALTERNATIVES_DIRECTORY[yes] = "${bindir}"
ALTERNATIVES_DIRECTORY[zcat] = "${base_bindir}"

# Fix for upstream 0.6.0 .bb: toybox_unstripped -> generated/unstripped/toybox
do_compile() {
    oe_runmake generated/unstripped/toybox && cp -a generated/unstripped/toybox toybox_unstripped

    # Create a list of links needed
    ${HOSTCC} -I . scripts/install.c -o generated/instlist
    ./generated/instlist long | sed -e 's#^#/#' \
        ${@ ' '.join(["-e 's;.*/%s;%s/%s;'" % (x, v, x) for x, v in d.getVarFlags('ALTERNATIVES_DIRECTORY').iteritems()]) } \
        > toybox.links
}
do_compile[vardeps] += "ALTERNATIVES_DIRECTORY"
