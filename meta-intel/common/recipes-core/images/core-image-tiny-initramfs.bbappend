# Set WKS file depending on the MACHINE picked by the user
def wks_intel(d):
    if d.getVar('MACHINE', True) == "intel-core2-32":
        d.setVar('WKS_FILE', "systemd-bootdisk-tiny32.wks")
    elif d.getVar('MACHINE', True) == "intel-corei7-64":
        d.setVar('WKS_FILE', "systemd-bootdisk-tiny64.wks")
    elif d.getVar('MACHINE', True) == "intel-quark":
        d.setVar('WKS_FILE', "mktinygalileodisk.wks")

WKS_FILE_poky-tiny ?= "${@wks_intel(d)}"
