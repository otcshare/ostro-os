# Class for swupd integration -- generates input artefacts for consumption by
# swupd-server and calls swupd-server to process the inputs into update
# artefacts for consumption by swupd-client.
#
# Usage:
# * inherit this class in your core OS image. swupd-based OS's use bundles, the
#   primary one of which, os-core, is defined as the contents of this image.
# * Assign a list of names for bundles you wish to generate to the
#   SWUPD_BUNDLES variable i.e. SWUPD_BUNDLES = "feature_one feature_two"
# * Assign a list of packages for which their content should be included in
#   a bundle to a varflag of BUNDLE_CONTENTS which matches the bundle name
#   i.e. BUNDLE_CONTENTS[feature_one] = "package_one package_three package_six"
# * Ensure the OS_VERSION variable is assigned an integer value and increased
#   before each image build which should generate swupd update artefacts.
#
# See docs/Guide.md for more information.

inherit swupd-client

# Created for each bundle (including os-core) and the "full" directory,
# describing files and directories that swupd-server needs to include in the update
# mechanism (i.e. without SWUPD_FILE_BLACKLIST entries). Used by swupd-server.
SWUPD_ROOTFS_MANIFEST_SUFFIX = ".content.txt"
# Additional entries which need to be in images (for example, /etc/machine-id, but
# that are excluded from the update mechanism. Ignored by swupd-server,
# used by swupdimage.bbclass.
SWUPD_IMAGE_MANIFEST_SUFFIX = ".extra-content.txt"

# Name of the base image. Always set, constant (unlike PN, which is
# different in the different virtual images).
SWUPD_IMAGE_PN = "${@ d.getVar('PN_BASE', True) or d.getVar('PN', True)}"

# Main directory in which swupd is invoked. The actual output which needs
# to be published will be in the "www" sub-directory.
DEPLOY_DIR_SWUPD = "${DEPLOY_DIR}/swupd/${MACHINE}/${SWUPD_IMAGE_PN}"

# User configurable variables to disable all swupd processing or deltapack
# generation.
SWUPD_GENERATE ??= "1"
SWUPD_DELTAPACK_VERSIONS ??= ""

SWUPD_LOG_FN ??= "bbdebug 1"

# When doing format changes, this version number is used for the intermediate
# release. Default is OS_VERSION - 1. There's a separate sanity check for
# OS_VERSION in the .inc file, so this code should always work.
OS_VERSION_INTERIM ?= "${@ ${OS_VERSION} - 1 }"

# We need to preserve xattrs, which works with bsdtar out of the box.
# It also has saner file handling (less syscalls per file) than GNU tar.
# Last but not least, GNU tar 1.27.1 had weird problems extracting
# all requested entries with -T from an archive ("Not found in archive"
# errors for entries which were present and could be extraced or listed
# when using simpler file lists).
DEPENDS += "libarchive-native"

inherit distro_features_check
REQUIRED_DISTRO_FEATURES = "systemd"

python () {
    import os

    havebundles = (d.getVar('SWUPD_BUNDLES', True) or '') != ''
    deploy_dir = d.getVar('DEPLOY_DIR_SWUPD', True)

    # Always set, value differs among virtual image recipes.
    pn = d.getVar('PN', True)
    # The PN value of the base image recipe. None in the base image recipe itself.
    pn_base = d.getVar('PN_BASE', True)
    # For bundle images, the corresponding bundle name. None in swupd images.
    bundle_name = d.getVar('BUNDLE_NAME', True)

    # bundle-<image>-mega archives its rootfs as ${IMAGE_ROOTFS}.tar.
    # Every other recipe then can copy (do_stage_swupd_inputs) or
    # extract relevant files (do_image/create_rootfs()) without sharing
    # the same pseudo database. Not sharing pseudo instances is faster
    # and the expensive reading of individual files via pseudo only
    # needs to be done once.
    if havebundles:
        mega_rootfs = d.getVar('IMAGE_ROOTFS', True)
        mega_rootfs = mega_rootfs.replace('/' + pn +'/', '/bundle-%s-mega/' % (pn_base or pn))
        d.setVar('MEGA_IMAGE_ROOTFS', mega_rootfs)
        mega_archive = mega_rootfs + '.tar'
        workdir = d.getVar('WORKDIR', True)
        d.setVar('MEGA_IMAGE_ARCHIVE', mega_archive)
        mega_archive_rel = os.path.relpath(mega_archive, workdir)
        if os.path.sep not in mega_archive_rel:
           # The mega archive is in our work directory and must be
           # preserved for other virtual images even when rm_work.bbclass
           # is active.
           d.appendVar('RM_WORK_EXCLUDE_ITEMS', ' ' + mega_archive_rel)

    if pn_base is not None:
        # Swupd images must depend on the mega image having been
        # built, as they will copy contents from there. For bundle
        # images that is irrelevant.
        if bundle_name is None:
            mega_name = (' bundle-%s-mega:do_image_complete' % pn_base)
            d.appendVarFlag('do_image', 'depends', mega_name)

        return

    # do_swupd_update requires the full swupd directory hierarchy
    varflags = '%s/image %s/empty %s/www %s' % (deploy_dir, deploy_dir, deploy_dir, deploy_dir)
    d.setVarFlag('do_swupd_update', 'dirs', varflags)

    # For the base image only, set the BUNDLE_NAME to os-core and generate the
    # virtual image for the mega image
    d.setVar('BUNDLE_NAME', 'os-core')

    bundles = (d.getVar('SWUPD_BUNDLES', True) or "").split()
    extended = (d.getVar('BBCLASSEXTEND', True) or "").split()

    # We need to prevent the user defining bundles where the name might clash
    # with naming in meta-swupd and swupd itself:
    #  * mega is the name of our super image, an implementation detail in
    #     meta-swupd
    #  * full is the name used by swupd for the super manifest (listing all
    #     files in all bundles of the OS)
    def check_reserved_name(name):
        reserved_bundles = ['mega', 'full']
        if name in reserved_bundles:
            bb.error('SWUPD_BUNDLES contains an item named "%s", this is a reserved name. Please rename that bundle.' % name)

    for bndl in bundles:
        check_reserved_name(bndl)

    # Generate virtual images for all bundles.
    for bndl in bundles:
        extended.append('swupdbundle:%s' % bndl)
        dep = ' bundle-%s-%s:do_image_complete' % (pn, bndl)
        # do_stage_swupd_inputs will try and utilise artefacts of the bundle
        # image build, so must depend on it having completed
        d.appendVarFlag('do_stage_swupd_inputs', 'depends', dep)

    if havebundles:
        extended.append('swupdbundle:mega')

    # Generate real image files from the os-core bundle plus
    # certain additional bundles. All of these images can share
    # the same swupd update stream, the only difference is the
    # number of pre-installed bundles.
    for imageext in (d.getVar('SWUPD_IMAGES', True) or '').split():
        extended.append('swupdimage:%s' % imageext)

    d.setVar('BBCLASSEXTEND', ' '.join(extended))

    # The base image should depend on the mega-image having been populated
    # to ensure that we're staging the same shared files from the sysroot as
    # the bundle images.
    if havebundles:
        mega_name = (' bundle-%s-mega:do_image_complete' % pn)
        d.appendVarFlag('do_image', 'depends', mega_name)
        d.appendVarFlag('do_stage_swupd_inputs', 'depends', mega_name)

    # do_*swupd_* tasks need to re-run when ${DEPLOY_DIR_SWUPD}
    # got removed. We achieve that by creating the directory if needed
    # and adding a variable with the creation time stamp as value to
    # the do_stage_swupd_inputs vardeps. If that time stamp changes,
    # do_stage_swupd_inputs will be re-run.
    #
    # Uses a stamp file because this code runs several time during a build,
    # changing the value during a build causes hash mismatch errors, and the
    # directory ctime changes as content gets created in the directory.
    stampfile = os.path.join(deploy_dir, '.stamp')
    bb.utils.mkdirhier(deploy_dir)
    with open(stampfile, 'a+') as f:
        ctime = os.fstat(f.fileno()).st_ctime
    bb.parse.mark_dependency(d, stampfile)
    d.setVar('REDO_SWUPD', ctime)
    d.appendVarFlag('do_fetch_swupd_inputs', 'vardeps', ' REDO_SWUPD')
    d.appendVarFlag('do_stage_swupd_inputs', 'vardeps', ' REDO_SWUPD')
    d.appendVarFlag('do_swupd_update', 'vardeps', ' REDO_SWUPD')
}

# swupd-client expects a bundle subscription to exist for each
# installed bundle. This is simply an empty file named for the
# bundle in /usr/share/clear/bundles
def create_bundle_manifest(d, bundlename, dest=None):
    tgtpath = '/usr/share/clear/bundles'
    if dest:
        bundledir = dest + tgtpath
    else:
        bundledir = d.expand('${IMAGE_ROOTFS}%s' % tgtpath)
    bb.utils.mkdirhier(bundledir)
    open(os.path.join(bundledir, bundlename), 'w+b').close()

fakeroot do_rootfs_append () {
    import swupd.bundles

    bundle = d.getVar('BUNDLE_NAME', True)
    bundles = ['os-core']
    if bundle == 'mega':
        bundles.extend((d.getVar('SWUPD_BUNDLES', True) or '').split())
    else:
        bundles.append(bundle)
    # swupd-client expects a bundle subscription to exist for each
    # installed bundle. This is simply an empty file named for the
    # bundle in /usr/share/clear/bundles
    for bundle in bundles:
        swupd.bundles.create_bundle_manifest(d, bundle)
}
do_rootfs[depends] += "virtual/fakeroot-native:do_populate_sysroot"

do_image_append () {
    import swupd.rootfs

    swupd.rootfs.create_rootfs(d)
}

# The content lists of each rootfs get stored separately and
# need to be preserved when rm_work.bbclass is active.
# That information is used by do_stage_swupd_inputs in the
# base recipe.
RM_WORK_EXCLUDE_ITEMS += "swupd${SWUPD_ROOTFS_MANIFEST_SUFFIX} swupd${SWUPD_IMAGE_MANIFEST_SUFFIX}"
python do_swupd_list_bundle () {
    import swupd.bundles

    swupd.bundles.list_bundle_contents(d)
}
do_swupd_list_bundle[depends] = "${@ '${SWUPD_IMAGE_PN}:do_swupd_list_bundle' if '${SWUPD_IMAGE_PN}' != '${PN}' else '' }"
addtask do_swupd_list_bundle after do_image before do_build

# Some files should not be included in swupd manifests and therefore never be
# updated on the target (i.e. certain per-device or machine-generated files in
# /etc when building for a statefule OS). Add the target paths to this list to
# prevent the specified files being copied to the swupd staging directory.
# i.e.
# SWUPD_FILE_BLACKLIST = "\
#     /etc/mtab \
#     /etc/machine-id \
#"
SWUPD_FILE_BLACKLIST ??= ""

SWUPDIMAGEDIR = "${DEPLOY_DIR_SWUPD}/image"
SWUPDMANIFESTDIR = "${WORKDIR}/swupd-manifests"

fakeroot python do_stage_swupd_inputs () {
    import swupd.bundles

    if d.getVar('PN_BASE', True):
        bb.debug(2, 'Skipping update input staging for non-base image %s' % d.getVar('PN', True))
        return

    swupd.bundles.copy_core_contents(d)
    swupd.bundles.copy_bundle_contents(d)
}
addtask stage_swupd_inputs after do_swupd_list_bundle before do_swupd_update
do_stage_swupd_inputs[dirs] = "${SWUPDIMAGEDIR} ${SWUPDMANIFESTDIR} ${DEPLOY_DIR_SWUPD}/maps/"
do_stage_swupd_inputs[depends] += " \
    virtual/fakeroot-native:do_populate_sysroot \
    ${@ ' '.join(['bundle-${SWUPD_IMAGE_PN}-%s:do_swupd_list_bundle' % x for x in (d.getVar('SWUPD_BUNDLES', True) or '').split()]) } \
"

python do_fetch_swupd_inputs () {
    import swupd.bundles

    if d.getVar('PN_BASE', True):
        bb.debug(2, 'Skipping update input staging for non-base image %s' % d.getVar('PN', True))
        return

    # Get information from remote update repo.
    swupd.bundles.download_old_versions(d)
}
do_fetch_swupd_inputs[dirs] = "${SWUPDIMAGEDIR}"
addtask do_fetch_swupd_inputs before do_swupd_update

# Change this to SWUPD_TIMING_CMD = "time" in local.conf
# to enable timing the individual swupd server command invocations.
# Relies on a build host which has "time" as a shell or system
# command.
SWUPD_TIMING_CMD ?= ""

# do_swupd_update uses its own pseudo database, for several reasons:
# - Performance is better when the pseudo instance is not shared
#   with other tasks that run in parallel (for example, meta-isafw's do_analyse_image).
# - Wiping out the deploy/swupd directory and re-executing do_stage_swupd_inputs/do_swupd_update
#   really starts from a clean slate.
# - The log.do_swupd_update will show commands that can be invoked directly, without
#   having to enter a devshell (slightly more convenient).
do_swupd_update () {
    if [ -z "${BUNDLE_NAME}" ] || [ ! -z "${PN_BASE}" ] ; then
        bbdebug 1 'We only generate swupd updates for the base image, skipping ${PN}:do_swupd_update'
        exit
    fi

    if [ ! "${SWUPD_GENERATE}" -eq 1 ]; then
        bbnote 'Update generation disabled, skipping.'
        exit
    fi

    export SWUPD_CERTS_DIR="${STAGING_ETCDIR_NATIVE}/swupd-certs"
    export LEAF_KEY="leaf.key.pem"
    export LEAF_CERT="leaf.cert.pem"
    export CA_CHAIN_CERT="ca-chain.cert.pem"
    export PASSPHRASE="${SWUPD_CERTS_DIR}/passphrase"

    export XZ_DEFAULTS="--threads 0"

    ${SWUPD_LOG_FN} "New OS_VERSION is ${OS_VERSION}"
    # If the swupd directory already exists don't trample over it, but let
    # the user know we're not doing any update generation.
    if [ -e ${DEPLOY_DIR_SWUPD}/www/${OS_VERSION} ]; then
        bbwarn 'swupd image directory exists for OS_VERSION=${OS_VERSION}, not generating updates.'
        bbwarn 'Ensure OS_VERSION is incremented if you want to generate updates.'
        exit
    fi

    # do_stage_swupd_inputs creates image/${OS_VERSION} for us, but
    # only if there has been some change in the input data that causes
    # the tasks to be rerun. In production that is unlikely, but it
    # happens when experimenting with swupd update creation. In that case
    # we can safely re-use the most recent version.
    #
    # However, we must unpack full.tar again to get the additional file
    # attributes right under our pseudo instance, so wipe it out in this case.
    if ! [ -e ${DEPLOY_DIR_SWUPD}/image/${OS_VERSION} ]; then
        latest=$(ls image | grep '^[0-9]*$' | sort -n | tail -1)
        if [ "$latest" ]; then
           ln -s $latest ${DEPLOY_DIR_SWUPD}/image/${OS_VERSION}
           rm -rf image/$latest/full
        else
           bbfatal '${DEPLOY_DIR_SWUPD}/image/${OS_VERSION} does not exist and no previous version was found either.'
           exit 1
        fi
    fi

    swupd_format_of_version () {
        if [ ! -f ${DEPLOY_DIR_SWUPD}/www/$1/Manifest.MoM ]; then
            bbfatal "Cannot determine swupd format of $1, ${DEPLOY_DIR_SWUPD}/www/$1/Manifest.MoM not found."
            exit 1
        fi
        format=`head -1 ${DEPLOY_DIR_SWUPD}/www/$1/Manifest.MoM | perl -n -e '/^MANIFEST\s(\d+)$/ && print $1'`
        if [ ! "$format" ]; then
            bbfatal "Cannot determine swupd format of $1, ${DEPLOY_DIR_SWUPD}/www/$1/Manifest.MoM does not have MANIFEST with format number in first line."
            exit 1
        fi
        echo $format
    }

    # do_fetch_swupd_inputs() creates this file when a content
    # URL was set, so creating an empty file shouldn't be necessary
    # in most cases. Also determine whether we are switching
    # formats.
    #
    # When the new format is different compared to what was used by
    # latest.version, then swupd-server will automatically ignore
    # the old content. That includes the case where tool format
    # hasn't changed and only the distro format was bumped. In that
    # case, reusing old content would be possible, but swupd-server
    # would have to be improved to know that.
    if [ -e ${DEPLOY_DIR_SWUPD}/image/latest.version ]; then
        PREVREL=`cat ${DEPLOY_DIR_SWUPD}/image/latest.version`
        if [ ! -e ${DEPLOY_DIR_SWUPD}/www/$PREVREL/Manifest.MoM ]; then
            bbfatal "${DEPLOY_DIR_SWUPD}/image/latest.version specifies $PREVREL as last version, but there is no corresponding ${DEPLOY_DIR_SWUPD}/www/$PREVREL/Manifest.MoM."
            exit 1
        fi
        PREVFORMAT=`swupd_format_of_version $PREVREL`
        if [ ! "$PREVFORMAT" ]; then
            bbfatal "Format number not found in first line of ${DEPLOY_DIR_SWUPD}/www/$PREVREL/Manifest.MoM"
            exit 1
        fi
        # For now assume that SWUPD_DISTRO_FORMAT is always 0 and that thus
        # $PREVFORMAT also is the format of the previous tools.
        PREVTOOLSFORMAT=$PREVFORMAT

        if [ $PREVFORMAT -ne ${SWUPD_FORMAT} ] && [ $PREVREL -ge ${OS_VERSION_INTERIM} ]; then
            bbfatal "Building two releases because of a format change, so OS_VERSION - 1 = ${OS_VERSION_INTERIM} must be higher than last version $PREVREL."
        elif [ $PREVREL -ge ${OS_VERSION} ]; then
            bbfatal "OS_VERSION = ${OS_VERSION} must be higher than last version $PREVREL."
            exit 1
        fi
    else
        bbdebug 2 "Stubbing out empty latest.version file"
        touch ${DEPLOY_DIR_SWUPD}/image/latest.version
        PREVREL="0"
        PREVFORMAT=${SWUPD_FORMAT}
        PREVTOOLSFORMAT=${SWUPD_FORMAT}
    fi

    # swupd-server >= 3.2.8 uses a different name. Support old and new names
    # via symlinking.
    ln -sf latest.version ${DEPLOY_DIR_SWUPD}/image/LAST_VER

    ${SWUPD_LOG_FN} "Generating update from $PREVREL (format $PREVFORMAT) to ${OS_VERSION} (format ${SWUPD_FORMAT})"

    # Generate swupd-server configuration
    bbdebug 2 "Writing ${DEPLOY_DIR_SWUPD}/server.ini"
    if [ -e "${DEPLOY_DIR_SWUPD}/server.ini" ]; then
       rm ${DEPLOY_DIR_SWUPD}/server.ini
    fi
    cat << END > ${DEPLOY_DIR_SWUPD}/server.ini
[Server]
imagebase=${DEPLOY_DIR_SWUPD}/image/
outputdir=${DEPLOY_DIR_SWUPD}/www/
emptydir=${DEPLOY_DIR_SWUPD}/empty/
END

    GROUPS_INI="${DEPLOY_DIR_SWUPD}/groups.ini"
    bbdebug 2 "Writing ${GROUPS_INI}"
    if [ -e "${DEPLOY_DIR_SWUPD}/groups.ini" ]; then
       rm ${DEPLOY_DIR_SWUPD}/groups.ini
    fi
    touch ${GROUPS_INI}
    ALL_BUNDLES="os-core ${SWUPD_BUNDLES} ${SWUPD_EMPTY_BUNDLES}"
    for bndl in ${ALL_BUNDLES}; do
        echo "[$bndl]" >> ${GROUPS_INI}
        echo "group=$bndl" >> ${GROUPS_INI}
        echo "" >> ${GROUPS_INI}
    done

    # Activate pseudo explicitly for all following commands which need it.
    # We use a database that is specific to the OS_VERSION, because that
    # avoids (potential?) performance degradation that might occur when
    # the same database is used for a growing number of files. Placing
    # it inside the swupd deploy dir ensures that it gets wiped out
    # together with that.
    PSEUDO_LOCALSTATEDIR=${DEPLOY_DIR_SWUPD}/image/${OS_VERSION}.pseudo
    rm -rf $PSEUDO_LOCALSTATEDIR
    PSEUDO="${FAKEROOTENV} PSEUDO_LOCALSTATEDIR=$PSEUDO_LOCALSTATEDIR ${FAKEROOTCMD}"

    # Unpack the input rootfs dir(s) for use with the swupd tools. Might have happened
    # already in a previous run of this task.
    for archive in ${DEPLOY_DIR_SWUPD}/image/*/*.tar; do
        dir=$(echo $archive | sed -e 's/.tar$//')
        if [ -e $archive ] && ! [ -d $dir ]; then
            mkdir -p $dir
            bbnote Unpacking $archive
            env $PSEUDO bsdtar -xf $archive -C $dir
        fi
    done

    # Remove any remaining intermediate artifacts from a previous run.
    # Necessary because the corresponding cleanup in swupd-server is
    # disabled because of https://bugzilla.yoctoproject.org/show_bug.cgi?id=10623.
    rm -rf ${DEPLOY_DIR_SWUPD}/packstage

    invoke_swupd () {
        echo $PSEUDO "$@"
        ${SWUPD_TIMING_CMD} env $PSEUDO "$@"
    }

    waitall () {
        while [ $# -gt 0 ]; do
            pid=$1
            shift
            wait $pid
        done
    }

    if [ "${SWUPD_CONTENT_URL}" ]; then
        content_url_parameter="--content-url ${SWUPD_CONTENT_URL}"
    else
        content_url_parameter=""
    fi

    create_version () {
        swupd_format=$1
        tool_format=$2
        os_version=$3

        # env $PSEUDO bsdtar -acf ${DEPLOY_DIR}/swupd-before-create-update.tar.gz -C ${DEPLOY_DIR} swupd
        invoke_swupd ${STAGING_BINDIR_NATIVE}/swupd_create_update_$tool_format --log-stdout -S ${DEPLOY_DIR_SWUPD} --osversion $os_version --format $swupd_format

        ${SWUPD_LOG_FN} "Generating fullfiles for $os_version"
        # env $PSEUDO bsdtar -acf ${DEPLOY_DIR}/swupd-before-make-fullfiles.tar.gz -C ${DEPLOY_DIR} swupd
        invoke_swupd ${STAGING_BINDIR_NATIVE}/swupd_make_fullfiles_$tool_format --log-stdout -S ${DEPLOY_DIR_SWUPD} $os_version

        ${SWUPD_LOG_FN} "Generating zero packs, this can take some time."
        # env $PSEUDO bsdtar -acf ${DEPLOY_DIR}/swupd-before-make-zero-pack.tar.gz -C ${DEPLOY_DIR} swupd
        # Generating zero packs isn't parallelized internally. Mostly it just
        # spends its time compressing a single tar archive. Therefore we parallelize
        # by forking each command and then waiting for all of them to complete.
        jobs=""
        for bndl in ${ALL_BUNDLES}; do
            # The zero packs are used by the swupd client when adding bundles.
            # The zero pack for os-core is not needed by the swupd client itself;
            # in Clear Linux OS it is used by the installer. We could use some
            # space by skipping the os-core zero bundle, but for now it gets
            # generated, just in case that it has some future use.
            invoke_swupd ${STAGING_BINDIR_NATIVE}/swupd_make_pack_$tool_format --log-stdout $content_url_parameter -S ${DEPLOY_DIR_SWUPD} 0 $os_version $bndl | sed -u -e "s/^/$bndl: /" &
            jobs="$jobs $!"
        done

        # Generate delta-packs against previous versions chosen by our caller,
        # if possible. Different formats make this useless because the previous
        # version won't be able to update to the new version directly.
        # env $PSEUDO bsdtar -acf ${DEPLOY_DIR}/swupd-before-make-delta-pack.tar.gz -C ${DEPLOY_DIR} swupd
        for prevver in ${SWUPD_DELTAPACK_VERSIONS}; do
            old_swupd_format=`swupd_format_of_version $prevver`
            if [ $old_swupd_format -eq $swupd_format ]; then
                for bndl in ${ALL_BUNDLES}; do
                    ${SWUPD_LOG_FN} "Generating delta pack from $prevver to $os_version for $bndl"
                    invoke_swupd ${STAGING_BINDIR_NATIVE}/swupd_make_pack_$tool_format --log-stdout $content_url_parameter -S ${DEPLOY_DIR_SWUPD} $prevver $os_version $bndl | sed -u -e "s/^/$prevver $bndl: /" &
                    jobs="$jobs $!"
                done
            fi
        done

        waitall $jobs

        # Write version to www/version/format$swupd_format/latest.
        bbdebug 2 "Writing latest file"
        mkdir -p ${DEPLOY_DIR_SWUPD}/www/version/format$swupd_format
        echo $os_version > ${DEPLOY_DIR_SWUPD}/www/version/format$swupd_format/latest
        # env $PSEUDO bsdtar -acf ${DEPLOY_DIR}/swupd-done.tar.gz -C ${DEPLOY_DIR} swupd
    }

    if [ $PREVFORMAT -ne ${SWUPD_FORMAT} ]; then
        # Exact same content (including the OS_VERSION in the os-release file),
        # just different tool and/or format in the manifests.
        ln -sf ${OS_VERSION} ${DEPLOY_DIR_SWUPD}/image/${OS_VERSION_INTERIM}
        echo $PREVREL > ${DEPLOY_DIR_SWUPD}/image/latest.version
        create_version $PREVFORMAT $PREVTOOLSFORMAT ${OS_VERSION_INTERIM}
    fi
    echo $PREVREL > ${DEPLOY_DIR_SWUPD}/image/latest.version
    create_version ${SWUPD_FORMAT} ${SWUPD_TOOLS_FORMAT} ${OS_VERSION}
    echo ${OS_VERSION} > ${DEPLOY_DIR_SWUPD}/image/latest.version
}

SWUPDDEPENDS = "\
    virtual/fakeroot-native:do_populate_sysroot \
    rsync-native:do_populate_sysroot \
    bsdiff-native:do_populate_sysroot \
"

# We don't know exactly which formats will be in use during
# do_swupd_update. It depends on the content of the update
# repo, which is unavailable when dependencies are evaluated
# in preparation of the build.
#
# For now we simply build all supported server versions.
SWUPD_SERVER_FORMATS = "3 4"
SWUPDDEPENDS += "${@ ' '.join(['swupd-server-format%s-native:do_populate_sysroot' % x for x in '${SWUPD_SERVER_FORMATS}'.split()])}"

addtask swupd_update after do_image_complete before do_build
do_swupd_update[depends] = "${SWUPDDEPENDS}"

# pseudo does not handle xattrs correctly for hardlinks:
# https://bugzilla.yoctoproject.org/show_bug.cgi?id=9317
#
# This started to become a problem when copying rootfs
# content around for swupd bundle creation. As a workaround,
# we avoid having hardlinks in the rootfs and replace them
# with symlinks.
python swupd_replace_hardlinks () {
    import os
    import stat

    # Collect all inodes and which entries share them.
    inodes = {}
    for root, dirs, files in os.walk(d.getVar('IMAGE_ROOTFS', True)):
        for file in files:
            path = os.path.join(root, file)
            s = os.lstat(path)
            if stat.S_ISREG(s.st_mode):
                inodes.setdefault(s.st_ino, []).append(path)

    for inode, paths in inodes.items():
        if len(paths) > 1:
            paths.sort()
            bb.debug(3, 'Removing hardlinks: %s' % ' = '.join(paths))
            # Arbitrarily pick the first entry as symlink target.
            target = paths.pop(0)
            for path in paths:
                reltarget = os.path.relpath(target, os.path.dirname(path))
                os.unlink(path)
                os.symlink(reltarget, path)
}
ROOTFS_POSTPROCESS_COMMAND += "swupd_replace_hardlinks; "

# Check whether the constructed image contains any dangling symlinks, these
# are likely to indicate deeper issues.
# NOTE: you'll almost certainly want to override these for your distro.
# /run, /var/volatile and /dev only get mounted at runtime.
# Enable this check by adding it to IMAGE_QA_COMMANDS
# IMAGE_QA_COMMANDS += " \
#     swupd_check_dangling_symlinks \
# "
SWUPD_IMAGE_SYMLINK_WHITELIST ??= " \
    /run/lock \
    /var/volatile/tmp \
    /var/volatile/log \
    /dev/null \
    /proc/mounts \
    /run/resolv.conf \
"

python swupd_check_dangling_symlinks() {
    from oe.utils import ImageQAFailed

    rootfs = d.getVar("IMAGE_ROOTFS", True)

    def resolve_links(target, root):
        if not target.startswith('/'):
            target = os.path.normpath(os.path.join(root, target))
        else:
            # Absolute links are in fact relative to the rootfs.
            # Can't use os.path.join() here, it skips the
            # components before absolute paths.
            target = os.path.normpath(rootfs + target)
        if os.path.islink(target):
            root = os.path.dirname(target)
            target = os.readlink(target)
            target = resolve_links(target, root)
        return target

    # Check for dangling symlinks. One common reason for them
    # in swupd images is update-alternatives where the alternative
    # that gets chosen in the mega image then is not installed
    # in a sub-image.
    #
    # Some allowed cases are whitelisted.
    whitelist = d.getVar('SWUPD_IMAGE_SYMLINK_WHITELIST', True).split()
    message = ''
    for root, dirs, files in os.walk(rootfs):
        for entry in files + dirs:
            path = os.path.join(root, entry)
            if os.path.islink(path):
                target = os.readlink(path)
                final_target = resolve_links(target, root)
                if not os.path.exists(final_target) and not final_target[len(rootfs):] in whitelist:
                    message = message + 'Dangling symlink: %s -> %s -> %s does not resolve to a valid filesystem entry.\n' % (path, target, final_target)

    if message != '':
        message = message + '\nIf these symlinks not pointing to a valid destination is not an issue \
i.e. the link is to a file which only exists at runtime, such as files in /proc, add them to \
SWUPD_IMAGE_SYMLINK_WHITELIST to resolve this error.'
        raise ImageQAFailed(message, swupd_check_dangling_symlinks)
}
