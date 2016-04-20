# Implementation Overview

An image that inherits this class will automatically have bundle 'chroots' created which contain the filesystem contents of the specified bundles.
The mechanism to achieve this is that several virtual image recipes are created, one for each defined bundle plus a 'mega' image recipe.
The 'mega' image contains the base image plus all of the bundles (and their contents), whilst bundle images contain only the base image plus the contents of a single bundle.

We build the mega image first, then the base image (the one which inherits the `swupd-image` class) and finally all of the bundle images  . Each non-mega image has a manifest generated that lists all of the file contents of the image.

Each bundle 'chroot'-like directory and the rootfs of the base image are all populated from the contents of the mega image's rootfs. The reason for this is to ensure that all files which are modified during some kind of post-processing step, i.e. passwd and groups updated during postinsts, are fully populated.
This may not be an ideal compromise and requires further thought (i.e. see the known issue about alternatives above).

Once the images and their manifests have been created each bundle image manifest is compared to the base image manifest in order to generate a delta list of files in the bundle image which don't exist in the base image.
Files in this list are then preserved in the bundle directory for processing by swupd-server in order to generate update artefacts.
