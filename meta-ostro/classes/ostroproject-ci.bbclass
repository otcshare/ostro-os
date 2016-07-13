# Used by ostroproject-ci.inc to make some changes which cannot be done
# directly in the include file.

# The CI uses auto.conf to make some changes which are meant to be active
# only in the CI, like enabling isafw and buildhistory. None of those
# are meant to be active when normal developers use the eSDK. At best
# they cause overhead, but others (like making OS_VERSION depend on
# a CI variable) outright prevent using the eSDK.
#
# Instead of trying to filter the auto.conf, we take full control
# over its content here.
python ostroproject_ci_clean_auto () {
    autoconf = d.expand('${SDK_OUTPUT}/${SDKPATH}/conf/auto.conf')
    with open(autoconf, 'w') as f:
        # MACHINE must be set.
        f.write('MACHINE = "%s"\n' % d.getVar('MACHINE', True))
        # Currently required because the user cannot add it themselves.
        # It would be better if the users edited some file to choose
        # the image mode.
        f.write('require conf/distro/include/ostro-os-development.inc\n')
}

SDK_POSTPROCESS_COMMAND_append_task-populate-sdk-ext = "ostroproject_ci_clean_auto; "
