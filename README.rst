About the ostro-os repository
===========================

The ostro-os repository is a combination of several different components
in a single repository. It contains everything that is needed to build
Ostro OS:

- bitbake
- openembedded-core
- meta-intel
- meta-ostro
- meta-oic
- meta-intel-iot-middleware
- meta-intel-iot-security
- meta-ostro-fixes
- meta-ostro-bsp
- meta-iot-web
- meta-yocto
- meta-iotqa
- meta-appfw
- meta-java
- meta-soletta
- meta-openembedded
- meta-swupd

The top-level directory comes from openembedded-core and meta-ostro
(including this README.rst), everything else is in its own
sub-directory. The ostro-os repository gets updated by importing
commits from the component's repostories.

Updating the repository
=======================

Everyone with a copy of the repository can use ``scripts/combo-layer`` to
import commits from the components. However, typically this happens
automatically as part of the continous integration setup and only core
maintainers will ever need to do that manually.

Normal developers can either:

1. Make changes in a fork of the ostro-os repository. Submitting a pull
   request is okay and will trigger a test build with the modification.
   However, the pull request typically cannot be merged and must be
   split up into pull requests into the component repositories.
2. Directly modify component repositories and switch to them in a local
   build by replacing the paths to them in ``conf/bblayers.conf`` of
   the build.

The first approach is more suitable for changes affecting many
different repositories, the second more for localized changes.

Shared maintenance of ostro-os via combo-layer works because the
``last_revision`` property which gets changed after each import gets
committed to the combined repostory.

To do this, first copy ``conf/combo-layer-local-sample.conf`` into
``conf/combo-layer-local.conf`` and set the paths for each component
repository to a suitable location.

Then run:

- ``scripts/combo-layer init`` (only once)
- ``scripts/combo-layer update <component>`` where <component> is either one of
   components above (for updating just that one) or empty (for updating all)
- optional: ``git commit --amend`` the last auto-generated commit

Branching
=========

Each branch in this repository tracks one branch in each component. To
create a new branch:

- checkout a new branch at a suitable base
- change the "branch" properties in ``conf/combo-layer.conf``
- change the branch part in the ``last_revision`` sections
- commit
- continue as before

This works best if the last imported revision from each component is
the branching point of that component. Ensure that by updating before
the components branch. If it is too late, either select commits
interactively (``combo-layer --interactive``) or import too many commits
and then drop unwanted ones via ``git rebase`` or ``git reset
--hard``. Remember to keep ``last_revision`` correct when doing that.
