inherit useradd_base

# Generates shell code for systemd_sysusers_create() which looks up
# $name in the gid or uid tables to determine a new value for $id.
# Very simplistic, better solution is expected to come from OE-core
# (see below).
# Example output:
#    case $name in foo) id=10;; bar) id=20;; *) bbfatal "...";; esac
def systemd_sysusers_lookup_staticid(tables_variable, d):
    if d.getVar('USERADDEXTENSION', True) != 'useradd-staticids':
        return ''
    result = [ 'case $name in' ]
    bbpath = d.getVar('BBPATH', True)
    tables = d.getVar(tables_variable, True)
    for conf_file in tables.split():
        path = bb.utils.which(bbpath, conf_file)
        with open(path) as f:
            for line in f:
                if not line.startswith('#'):
                    columns = line.strip().split(':')
                    if len(columns) >= 3:
                        # Same format for passwd and groups. Only these two
                        # entries are supported for systemd sysusers, the
                        # rest is ignored.
                        name = columns[0]
                        id = columns[2]
                        result.append('%s) id=%s;;' % (name, id))
    if d.getVar('USERADD_ERROR_DYNAMIC', True) in ('1', 'error'):
        result.append('*) bbfatal "systemd sysuser $name of type $type in $conf has no static ID. Search for ' + tables_variable + ' in ostro.conf for further information.";;')
    result.append('esac')
    return ' '.join(result)

systemd_sysusers_create () {
    set -x
    opts="--system --root ${IMAGE_ROOTFS}"
    for conf in ${IMAGE_ROOTFS}/${libdir}/sysusers.d/*.conf; do
        if [ -e "$conf" ]; then
            grep -v '^#' "$conf" | while read -r type name id remaining; do
                case "$type" in
                  g)
                    if [ "$id" = "-" ]; then
                        gid=""
                        ${@systemd_sysusers_lookup_staticid('USERADD_GID_TABLES', d)}
                        if [ "$id" != "-" ]; then
                           gid="--gid $id"
                        fi
                    else
                        gid="--gid $id"
                    fi
                    perform_groupadd "${IMAGE_ROOTFS}" "$opts $gid $name" 10
                    ;;
                  u)
                    if [ "$id" = "-" ]; then
                        uid=""
                        ${@systemd_sysusers_lookup_staticid('USERADD_UID_TABLES', d)}
                        if [ "$id" != "-" ]; then
                           uid="--uid $id"
                        fi
                    else
                        uid="--uid $id"
                    fi
                    comment=$(echo "$remaining" | cut -d '"' -f 2)
                    home=$(echo "$remaining" | cut -d '"' -f 3 | sed -e 's/^ *//' -e 's/ *$//')
                    perform_useradd "${IMAGE_ROOTFS}" "$opts $uid --home-dir ${home:-/} --shell /sbin/nologin --comment \"$comment\" $name" 10
                    ;;
                  "")
                    ;;
                  *)
                    bbfatal "Unsupported sysusers.d type in: $type $name $id $remaining"
                    ;;
                esac
            done
        fi
    done
}

ROOTFS_POSTPROCESS_COMMAND += "${@bb.utils.contains('DISTRO_FEATURES', 'systemd', 'systemd_sysusers_create;', '', d)}"

# The code above was written before some similar code was made
# available in OE-core. However, that code is still not suitable
# (https://bugzilla.yoctoproject.org/show_bug.cgi?id=9789) and thus we
# have to use our own version.
ROOTFS_POSTPROCESS_COMMAND_remove = "systemd_create_users"
