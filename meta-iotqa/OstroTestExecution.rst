.. _`How to Boot and Install Ostro image`: https://ostroproject.org/documentation/howtos/booting-and-installation.html
.. _`How to Set Authorized Keys for remoste ssh`: https://ostroproject.org/documentation/howtos/authorized-keys.html

Setup environment
=================
1. Host: Ubuntu 14.04 is tested and recommended.

  Install expect:  ``$ sudo apt-get install expect``
 
2. Target and assistant device set up: `How to Boot and Install Ostro image`_  

3. Target and assistant device (e.g. Galileo) should be remote accessible with ssh from Host machine `How to Set Authorized Keys for remoste ssh`_

4. Peripheral: Some test suite need peripheral setup, e.g. WiFi AP, assistant device for comms, refer to last section: `Specific Test Environment Setup`_

Run test
=========
1. Get test suites:

 - Fetch 2 test tar balls from ostroproject repository and copy to host machine: ``https://download.ostroproject.org/{path to build ID folder}/testsuite/intel-corei7-64/*``

   ``$ tar xvf iot-testsuite.tar.gz``

   ``$ tar xvf iot-testfiles.xxx.tar.gz -C iottest/``
  
   **Note**: xxx is target machine. E.g. intel-corei7-64, intel-core2-32, intel-quark, edison, etc.
    
 - Optinally, replace test cases with the latest cases from ostroproject/meta-iotqa github project after above step.
    
   ``$ git clone https://github.com/ostroproject/meta-iotqa.git``
   
   ``$ cp -r meta-iotqa/lib/oeqa/runtime iottest/oeqa/``
    
2. Run automated test:
     ``$ cd iottest``
 
     ``$ python  runtest.py -f testplan/xxx.manifest -m  [ target machine ]  -t [ target IP ] -t [ assistant device IP ] -s [ host IP ]``
     
     -  iottest.manifest is the one for acceptance test, which can be used in CI testing. <platform>.iottest.manifest is for the specific platform.
     
     -  Other xxx.manifest files are for different component, like bluetooth.manifest, wifi.manifest in iottest/testplan folder. It's very useful to rerun the network unstable cases manually.

3. Run manual test:

  - Some test cases are manual ones, in meta-iotqa project, ./conf/test/manul.csv includes all the general munual cases for ostro and ostro-xt. 

  - ./conf/test/manual-1.csv includes all the ostro-xt specific manual cases.
    
  - You can follow the test steps and expected result to check cases one by one.

Specific Test Environment Setup
===============================
For most of the WiFi, BT, CAN related automated test cases, test environment need to be configured as below, or you'll get fail test result.

1. **WiFi**: setup configuration file for 6 AP (5 hidden and 1 broadcasting)  — need to configure 2 files
   
- Open configuration file ``oeqa/runtime/wifi/files/config.ini`` to edit.

::

 [Connect]
 ssid_wep=<SSID name of Hidden-WEP encryption AP>
 passwd_wep=<password of Hidden-WEP encryption AP>
 ssid_80211ac=<SSID name of Hidden-802.11ac AP>
 passwd_80211ac=<password of Hidden-802.11ac AP>
 ssid_80211b=<SSID name of Hidden-802.11b AP>
 passwd_80211b=<password of Hidden-802.11b AP>
 ssid_80211g=<SSID name of Hidden-802.11g AP>
 passwd_80211g=<password of Hidden-802.11g AP>
 ssid_80211n=<SSID name of Hidden-802.11n AP>
 passwd_80211n=<password of Hidden-802.11n AP>
 ssid_broadcast=<SSID name of Broadcasting AP, which should be access internet directly>
 passwd_broadcast=<password of above broadcasting AP>

- Open the other configuration file ``oeqa/runtime/sanity/files/config.ini`` to edit. Note: this file must be configured with available AP (otherwise, it will affect iotivity cases)

::

 [Connect]
 type=hidden
 ssid=<SSID name of Hidden-802.11n AP>
 passwd=<password of Hidden-802.11n AP>

2. **BT**: need build and install **gatttool** from bluez project and copy the binary to ``/tmp`` of assistant device before running test

3. **CAN**: prepare a USB-CAN adapter. You can buy it from ``http://www.canusb.com/`` or refer to ``http://elinux.org/CAN_Bus#SocketCAN_Supported_Controllers``. Plug the CAN-USB adpater into usb port and reboot device. 