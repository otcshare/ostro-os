# Implementation Overview

An image that inherits the `swupd-image` class will automatically have bundle
'chroots' created which contain the filesystem contents of the specified
bundles. These chroots can then be processed by swupd to generate update
artefacts.

The mechanisms used to generate the swupd inputs differ based on how the bundle
is defined. Regardless, for any image recipe which inherits`swupd-image`, a
virtual image will be created named the *mega* image.
The 'mega' image contains the base image plus all of the bundles, including a
bundle's additional packages and IMAGE_FEATURES.
Similar virtual recipes are generated for each bundle which sets
`BUNDLE_FEATURES`, the reason for doing so is because an `IMAGE_FEATURE` such as
`ptest-pkgs` doesn't strictly map to an installable package list, so instead we
build a bundle image with the feature enabled and compare the files in the
bundle image to the base image in order to determine the bundle's contents.

The purpose of the *mega* image is to have a complete rootfs with fully
processed versions of all of the OS's files. The reason for this is to ensure
that all files which are modified during some kind of post-processing step i.e.
passwd and groups updated during postinsts, prelinked binaries, extended
attributes set, are fully processed before they are used to generate update
artefacts.

We must have this fully processed file source to ensure that any image and
rootfs post-processing, such as prelinking and security features which set
extended attributes, have been applied to the version of the file which will be
used.

Once the *mega* image is built its contents are used to populate the rootfs of
the base image and the `os-core` bundle directory in the swupd inputs directory.

Next each bundle's contents are copied to the swupd inputs directory. In the
common case where `BUNDLE_FEATURES` are not set the image's package manager is
used to install the bundle's contents into an empty directory and these contents
are then overwritten by the corresponding files from the *mega* image's rootfs.
If `BUNDLE_FEATURES` has been set for a bundle the contents of the generated
bundle image are compares to the contents of the base image and any files which
exist in the bundle image but not the base image have the corresponding files
copied from the *mega* image's rootfs to the bundle's swupd input directory.

**TODO**: address the concern around postinsts, i.e. passwd and groups

Once all of the inputs for swupd have been staged we then call the swupd
binaries to generate the update artefacts.
