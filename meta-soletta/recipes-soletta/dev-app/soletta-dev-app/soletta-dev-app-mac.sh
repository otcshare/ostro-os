#! /bin/bash
MAC_ADDRESS=`ifconfig INTERFACE | grep "HWaddr" | awk '{print $NF}'`
sed -i "s@MACADDR@$MAC_ADDRESS@" /etc/avahi/services/soletta-dev-app.service
