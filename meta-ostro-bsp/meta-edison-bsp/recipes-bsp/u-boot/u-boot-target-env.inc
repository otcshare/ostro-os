# Handle severals environments generation for u-boot
# and link the default one for Ifwi to u-boot-osip recipe

#Env binary size
ENV_SIZE = "0x10000"

#Env base Name
ENV_BASE_NAME = "${MACHINE}"
# Env base file correspond to common part of all environment
ENV_BASE_FILE = "${WORKDIR}/${ENV_BASE_NAME}.env"

# Env directory is where target variant files are stored
ENV_DIR = "${WORKDIR}/target_env"
# Env composed is directory where target env are composed
# by concatening of base environment file and variant files
# pattern name is applied the resulting files: base-variant.env
ENV_COMPOSED_DIR = "${WORKDIR}/target_composed"
# Env bin is directory where target env are store in binary form
# filename follows pattern name above : base-variant.bin
ENV_BIN_DIR = "${WORKDIR}/target_env_bin"

# Env deploy dir is the name of directory where binary envs will be deployed
ENV_DEPLOY_DIR="u-boot-envs"

# Env deploy src dir is the name of directory where txt envs will be deployed
ENV_SRC_DEPLOY_DIR="u-boot-envs-src"

# Env target to use for IFWI stitching process
ENV_IFWI_TARGET_NAME="ifwi"
# Env image is U-Boot primary environment (where internal U-Boot variables are stored)
# The same vairiable is also defined in u-boot-osip recip in charge of doing stitching
# process for IFWI
ENV_IMAGE = "${S}/env.bin"

do_build_mkimage_tool () {
   HOSTCC="${CC}" HOSTLD="${LD}" HOSTLDFLAGS="${LDFLAGS}" HOSTSTRIP=true oe_runmake  tools
}

python do_environment_mkimage() {
    import subprocess
    import shutil
    # list env variant target files
    target_root_dir = d.getVar('ENV_DIR',True)
    env_files = os.listdir(target_root_dir )
    # builds absolute paths
    env_files = [ os.path.join(target_root_dir,f) for f in env_files]

    env_bin_dir = d.getVar("ENV_BIN_DIR",True)
    # cleans if it exists env_bin directory
    shutil.rmtree(env_bin_dir, ignore_errors=True)
    # create env bin directory
    os.mkdir(env_bin_dir)
    # if a previous env image used for osip process exists delete it
    env_image = d.getVar('ENV_IMAGE',True)
    try:
        os.unlink(env_image)
    except OSError: pass
    bb.debug(1, 'Building binary environments in : %s' % env_bin_dir)
    # iterate targets list to build binary environment files
    for target_env in env_files :
        # get only filename without path and extension
        target_filename = os.path.splitext(os.path.basename(target_env))[0]
        # build output file path with ext
        target_bin = os.path.join(env_bin_dir,
            d.getVar('ENV_BASE_NAME',True) + '-' + target_filename + '.bin')
        # generated mkenvimage tool command line
        cmd_mkimg ='cat %s %s | grep -v -E "^$|^\#" |' \
                ' ./tools/mkenvimage -s %s -r -o %s -' \
                % ( d.getVar('ENV_BASE_FILE',True),target_env,
                d.getVar("ENV_SIZE",True), target_bin)
        bb.debug(1, 'Building binary for %s target:' % (target_filename))
        bb.debug(1, '%s' % cmd_mkimg)
        # execute shell command
        ret = subprocess.call(cmd_mkimg, shell=True)
        if ret: return ret
        if d.getVar('ENV_IFWI_TARGET_NAME',True) in target_bin :
            # create a symbolic link on default binary file env file to
            # avoid modifying to much osip part
            bb.debug(1, 'Create for IFWI stitching symlink %s to %s' % (env_image, target_bin))
            os.symlink(target_bin, env_image)
    return 0
}

do_deploy_append() {
    install -d ${DEPLOYDIR}
    # deploy  binary U-boot environments
    echo "Deploying U-boot Environments binary files in ${DEPLOYDIR}/${ENV_DEPLOY_DIR}"
    install -d ${DEPLOYDIR}/${ENV_DEPLOY_DIR}
    cp ${ENV_BIN_DIR}/*.bin ${DEPLOYDIR}/${ENV_DEPLOY_DIR}
}

addtask build_mkimage_tool after do_compile before do_environment_mkimage
addtask environment_mkimage after do_build_mkimage_tool before do_deploy
