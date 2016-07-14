# Copyright (C) 2013 Intel Corporation
#
# Released under the MIT license (see COPYING.MIT)


# testimage.bbclass enables testing of qemu images using python unittests.
# Most of the tests are commands run on target image over ssh.
# To use it add testimage to global inherit and call your target image with -c testimage
# You can try it out like this:
# - first build a qemu core-image-sato
# - add INHERIT += "test-iot" in local.conf
# - then bitbake core-image-sato -c test_iot. That will run a standard suite of tests.

# You can set (or append to) TEST_SUITES in local.conf to select the tests
# which you want to run for your target.
# The test names are the module names in meta/lib/oeqa/runtime.
# Each name in TEST_SUITES represents a required test for the image. (no skipping allowed)
# Appending "auto" means that it will try to run all tests that are suitable for the image (each test decides that on it's own).
# Note that order in TEST_SUITES is important (it's the order tests run) and it influences tests dependencies.
# A layer can add its own tests in lib/oeqa/runtime, provided it extends BBPATH as normal in its layer.conf.

# TEST_LOG_DIR contains a command ssh log and may contain infromation about what command is running, output and return codes and for qemu a boot log till login.
# Booting is handled by this class, and it's not a test in itself.
# TEST_QEMUBOOT_TIMEOUT can be used to set the maximum time in seconds the launch code will wait for the login prompt.

inherit testimage
DEPLOY_DIR_TESTSUITE ?= "${DEPLOY_DIR}/testsuite"

# Extra target binaries not installed in the target image, required for image testing.
IOTQA_TESTIMAGEDEPENDS += "mraa-test mmap-smack-test tcp-smack-test udp-smack-test read-map shm-util gdb"
IOTQA_TESTIMAGEDEPENDS += "${@bb.utils.contains('IMAGE_FEATURES', 'app-privileges', 'app-runas', '', d)}"

# When added to the task dependencies below, they get build before running those tasks.
IOTQA_TASK_DEPENDS = "${@ ' '.join([x + ':do_build' for x in '${IOTQA_TESTIMAGEDEPENDS}'.split()])}"

# When added to TESTIMAGEDEPENDS, they get built also if running do_testimage
# (see testimage.bbclass) but not when merely building an image.
TESTIMAGEDEPENDS_append = " ${IOTQA_TASK_DEPENDS}"

#get layer dir
def get_layer_dir(d, layer):
    bbpath = d.getVar("BBPATH", True).split(':')
    for p in bbpath:
        if os.path.basename(p.rstrip('/')) == layer:
            break
    else:
        return ""
    return p

#get QA layer dir
def get_qa_layer(d):
    return get_layer_dir(d, "meta-iotqa")

#override the function in testimage.bbclass
def get_tests_list_iot(d, type="runtime"):
    manif_name = d.getVar("TEST_SUITES_MANIFEST", True)
    if not manif_name:
        manif_name = "iottest.manifest"
    mainfestList = manif_name.split()
    testsuites = reduce(lambda x,y:x+y, map(lambda x: get_tclist(d,x), mainfestList))
    bbpath = d.getVar("BBPATH", True).split(':')

    testslist = []
    for testname in testsuites:
        if testname.startswith('#') or testname in testslist:
            continue
        testslist.append(testname)
    return testslist
    
#get testcase list from specified layer
def get_tclist(d, fname):
    p = get_qa_layer(d)
    manif_path = os.path.join(p, 'conf', 'test', fname)
    if not os.path.exists(manif_path):
        bb.fatal("No such manifest file: ", manif_path)
    tcs = open(manif_path).readlines()
    return [ item.strip() for item in tcs ]

#bitbake task - run iot test suite
python do_test_iot() {
    global get_tests_list
    get_tests_list_old = get_tests_list
    get_tests_list = get_tests_list_iot
    testimage_main(d)
    get_tests_list = get_tests_list_old
}

addtask test_iot
do_test_iot[depends] += "${IOTQA_TASK_DEPENDS} ${PN}:do_build"
do_test_iot[lockfiles] += "${TESTIMAGELOCK}"

#overwrite copy src dir to dest
def recursive_overwrite(src, dest, notOverWrite=[r'__init__\.py'], ignores=[r".+\.pyc"]):
    import shutil, re
    notOverWrite = list(map(re.compile, notOverWrite))
    ignores = list(map(re.compile, ignores))
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        for f in files:
            fsrc = os.path.join(src, f)
            fdest = os.path.join(dest, f)
            if any(map(lambda x:x.match(f), notOverWrite)) and os.path.exists(fdest) or\
               any(map(lambda x:x.match(f), ignores)):
                continue
            recursive_overwrite(fsrc, fdest)
    else:
        try:
            shutil.copy2(src, dest)
        except IOError as e:
            bb.warn(str(e))
   
#export test asset
def export_testsuite(d, exportdir):
    oeqadir = d.expand('${COREBASE}/meta/lib/oeqa')
    recursive_overwrite(oeqadir, os.path.join(exportdir, "oeqa"))
    
    bbpath = d.getVar("BBPATH", True).split(':')
    for p in bbpath:
        if os.path.exists(os.path.join(p, "lib", "oeqa")):
            recursive_overwrite(src=os.path.join(p, "lib"),
                        dest=os.path.join(exportdir))
            bb.plain("Exported tests from %s to: %s" % \
                     (os.path.join(p, "lib"), exportdir) )


#dump build data to external file
def dump_builddata(d, tdir):
    import json

    savedata = {}
    savedata["imagefeatures"] = d.getVar("IMAGE_FEATURES", True).split()
    savedata["distrofeatures"] = d.getVar("DISTRO_FEATURES", True).split()
    manifest = d.getVar("IMAGE_MANIFEST", True)
    try:
        with open(manifest) as f:
            pkgs = f.readlines()
            savedata["pkgmanifest"] = [ pkg.strip() for pkg in pkgs ]
    except IOError as e:
        bb.fatal("No package manifest file found: %s" % e)

    bdpath = os.path.join(tdir, "builddata.json")
    with open(bdpath, "w+") as f:
        json.dump(savedata, f, skipkeys=True, indent=4, sort_keys=True)

# copy src_file(relative of layerdir) to tdir
def copy_qa_layer_file_to(d, src_file, tdir):
    import shutil, os
    layerdir = get_qa_layer(d)
    srcpath = os.path.join(layerdir, src_file)
    if os.path.isfile(srcpath):
        shutil.copy2(srcpath, tdir)
        bb.plain("copy %s to: %s" % (srcpath, tdir))
    else:
        bb.plain("missing file: %s" % srcpath)

# copy manifest file
def copy_manifest(d, tdir):
    srcpath = os.path.join(get_qa_layer(d), "conf", "test")
    import shutil
    shutil.copytree(srcpath, tdir)

def re_creat_dir(path):
    bb.utils.remove(path, recurse=True)
    bb.utils.mkdirhier(path)


#package test suite as tarball
def pack_tarball(d, tdir, fname):
    import tarfile
    tar = tarfile.open(fname, "w:gz")
    tar.add(tdir, arcname=os.path.basename(tdir))
    tar.close()

#bitbake task - export iot test suite
python do_test_iot_export() {
    import shutil
    deploydir = "deploy"
    exportdir = d.getVar("TEST_EXPORT_DIR", True)
    if not exportdir:
        exportdir = "iottest"
        d.setVar("TEST_EXPORT_DIR", exportdir)
    bb.utils.remove(exportdir, recurse=True)
    bb.utils.mkdirhier(exportdir)
    bb.utils.mkdirhier(os.path.join(exportdir, deploydir))
    export_testsuite(d, exportdir)
    plandir = os.path.join(exportdir, "testplan")
    copy_manifest(d, plandir)
    outdir = d.getVar("DEPLOY_DIR_TESTSUITE", True)
    bb.utils.mkdirhier(outdir)
    fname = os.path.join(outdir, "iot-testsuite.tar.gz")
    pack_tarball(d, exportdir, fname)
    bb.plain("export test suite to ", fname)
    re_creat_dir(deploydir)
    shutil.copytree(os.path.join(d.getVar("DEPLOY_DIR", True), "files"), os.path.join(deploydir,"files"))
    machine = d.getVar("MACHINE", True)
    filesdir = os.path.join(deploydir, "files", machine)
    bb.utils.mkdirhier(filesdir)
    dump_builddata(d, filesdir)
    fname = os.path.join(outdir, "iot-testfiles.%s.tar.gz" % machine)
    pack_tarball(d, deploydir, fname)
    bb.plain("export test files to ", fname)
}

addtask test_iot_export
do_test_iot_export[depends] += "${IOTQA_TASK_DEPENDS} ${PN}:do_build"
do_test_iot_export[lockfiles] += "${TESTIMAGELOCK}"
