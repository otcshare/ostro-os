# Check that the user has explicitly chosen how to build images.
OSTRO_IMAGE_BUILD_MODE_SELECTED ?= ""
addhandler ostro_sanity_check_eventhandler
ostro_sanity_check_eventhandler[eventmask] = "bb.event.SanityCheck"
python ostro_sanity_check_eventhandler() {
    if not d.getVar('OSTRO_IMAGE_BUILD_MODE_SELECTED', True):
        bb.fatal('''local.conf must be explicitly edited to select between building
production and development images. See the comments in local.conf.sample
and doc/howtos/building-images.rst.''')
}

# /run, /proc, /var/volatile and /dev only get mounted at runtime.
OSTRO_QA_IMAGE_SYMLINK_WHITELIST = " \
    /dev/null \
    /proc/mounts \
    /run/lock \
    /run/resolv.conf \
    /var/volatile/log \
    /var/volatile/tmp \
"

# Additional image checks.
python ostro_qa_image () {
    qa_sane = True

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
    whitelist = d.getVar('OSTRO_QA_IMAGE_SYMLINK_WHITELIST', True).split()
    for root, dirs, files in os.walk(rootfs):
        for entry in files + dirs:
            path = os.path.join(root, entry)
            if os.path.islink(path):
                target = os.readlink(path)
                final_target = resolve_links(target, root)
                if not os.path.exists(final_target) and not final_target[len(rootfs):] in whitelist:
                    bb.error("Dangling symlink: %s -> %s -> %s does not resolve to a valid filesystem entry." %
                             (path, target, final_target))
                    qa_sane = False

    if not qa_sane:
        bb.fatal("Fatal QA errors found, failing task.")
}

do_image[postfuncs] += "ostro_qa_image"
