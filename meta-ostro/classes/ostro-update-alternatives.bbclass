# This code only runs in recipes which inherit update-alternatives.bbclass.
# It manipulates the postinst scripts created by update-alternatives.bbclass
# so that "update-alternatives --install" calls take
# ${ALTERNATIVE_PRIORITY_<package name in upper case and with underscores>:-<def priority>}
# as priority parameter, i.e. it becomes possible to override the default priority
# set in the recipe at install time via env variables.
def ostro_manipulate_postinst_alternatives(d):
    import re

    pn = d.getVar('BPN', True)
    suffix = (''.join([x if x.isalnum() else '_' for x in pn])).upper()
    replacements = set()
    def new_alt_priority(m):
        replacement = '${ALTERNATIVE_PRIORITY_%s:-%s}' % (
                         suffix,
                         m.group(2),
                       )
        if not replacement in replacements:
            bb.note('adding support for %s update-alternatives image variable' % replacement)
            replacements.add(replacement)
        return m.group(1) + replacement

    regex = re.compile(r'''(update-alternatives\s+--install\s+\S+\s+\S+\s+\S+\s+)(\S+)''')
    for pkg in (d.getVar('PACKAGES', True) or "").split():
        postinst = d.getVar('pkg_postinst_%s' % pkg, True)
        if postinst:
            postinst = regex.sub(new_alt_priority, postinst)
            d.setVar('pkg_postinst_%s' % pkg, postinst)

python populate_packages_updatealternatives_append () {
    ostro_manipulate_postinst_alternatives(d)
}
