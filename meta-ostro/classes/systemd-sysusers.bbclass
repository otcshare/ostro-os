inherit useradd_base

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
                    else
                        gid="--gid $id"
                    fi
                    perform_groupadd "${IMAGE_ROOTFS}" "$opts $gid $name" 10
                    ;;
                  u)
                    if [ "$id" = "-" ]; then
                        uid=""
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
