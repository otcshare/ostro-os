FILESEXTRAPATHS_prepend := "${THISDIR}/linux-yocto:"

### Config "fix" fragments

# security fixes
SRC_URI_append = " file://security.cfg"
SRC_URI_append_edison = " file://security-x86.cfg"
SRC_URI_append_intel-quark = " file://security-x86.cfg"
SRC_URI_append_intel-core2-32 = " file://security-x86.cfg"
SRC_URI_append_intel-corei7-64 = " file://security-x64.cfg"
SRC_URI_append_edison = " file://edison-iptables.cfg"
SRC_URI_append_edison = " file://KEYS_Fix_keyring_ref_leak_in-join_session_keyring.patch"
SRC_URI_append_intel-quark = " file://KEYS_Fix_keyring_ref_leak_in-join_session_keyring.patch"
SRC_URI_append_intel-core2-32 = " file://KEYS_Fix_keyring_ref_leak_in-join_session_keyring.patch"
SRC_URI_append_intel-corei7-64 = " file://KEYS_Fix_keyring_ref_leak_in-join_session_keyring.patch"

### Hardware support fragments

# I2C sensors
SRC_URI_append_intel-quark = " file://sensors.cfg"
SRC_URI_append_edison = " file://sensors.cfg"
SRC_URI_append_beaglebone = " file://sensors.cfg"
#  Minnow Max has I2C
SRC_URI_append_intel-corei7-64 = " file://sensors.cfg"
SRC_URI_append_intel-core2-32 = " file://sensors.cfg"
# backport BH1750 light sensor support on Minnow Max and NUC
SRC_URI_append_intel-corei7-64 = " file://0001-iio-light-add-support-for-ROHM-BH1710-BH1715-BH1721-.patch"
SRC_URI_append_intel-core2-32 = " file://0001-iio-light-add-support-for-ROHM-BH1710-BH1715-BH1721-.patch"
SRC_URI_append_intel-corei7-64 = " file://bh1750.cfg"
SRC_URI_append_intel-core2-32 = " file://bh1750.cfg"

# backport BH1750 light sensor support on Galileo Gen 2
SRC_URI_append_intel-quark = " file://bh1750.cfg"
SRC_URI_append_intel-quark = " file://0001-iio-light-add-support-for-ROHM-BH1710-BH1715-BH1721-.patch"

#  BeagleBone Black enable all I2Cs
SRC_URI_append_beaglebone = " file://0001-v3.15.0-ARM-dts-am335x-boneblack-configure-i2c1-and-2.patch"

# user space SPI support
SRC_URI_append_intel-quark = " file://uspi.cfg"
SRC_URI_append_edison = " file://uspi.cfg"
SRC_URI_append_beaglebone = " file://uspi.cfg"

# IIO support
SRC_URI_append_beaglebone = " file://iio.cfg"

# NFC support and drivers
SRC_URI_append = " file://nfc.cfg"
SRC_URI_append_intel-quark = " file://nfc-spi.cfg"
SRC_URI_append_edison = " file://nfc-spi.cfg"
SRC_URI_append_beaglebone = " file://nfc-spi.cfg"
#  Minnow Max has SPI
SRC_URI_append_intel-corei7-64 = " file://nfc-spi.cfg"
SRC_URI_append_intel-quark = " file://nfc-i2c.cfg"
SRC_URI_append_edison = " file://nfc-i2c.cfg"
SRC_URI_append_beaglebone = " file://nfc-i2c.cfg"
#  Minnow Max has I2C
SRC_URI_append_intel-corei7-64 = " file://nfc-i2c.cfg"

# USB-serial interface support and drivers
SRC_URI_append = " file://usb-serial.cfg"

# USB-ethernet support and drivers for Edison
SRC_URI_append_edison = " file://edison-usb-ethernet.cfg"

# CAN-bus support and drivers
SRC_URI_append = " file://can.cfg"
SRC_URI_append_intel-quark = " file://can-spi.cfg"
SRC_URI_append_edison = " file://can-spi.cfg"
SRC_URI_append_beaglebone = " file://can-spi.cfg"
#  MinnowMax has SPI
SRC_URI_append_intel-corei7-64 = " file://can-spi.cfg"
SRC_URI_append_intel-core2-32 = " file://can-x86.cfg"
SRC_URI_append_intel-corei7-64 = " file://can-x86.cfg"

# RealTek WiFi chip used on Gigabyte GB-BXBT-3825
SRC_URI_append_intel-core2-32 = " file://wireless.cfg"
SRC_URI_append_intel-corei7-64 = " file://wireless.cfg"

# 6lowpan support
SRC_URI_append = " file://6lowpan.cfg"

# 6lowpan over 802154 support and drivers
SRC_URI_append = " file://6lowpan-802154.cfg"

# 6lowpan over Bluetooth LE support
SRC_URI_append = " file://6lowpan-btle.cfg"
SRC_URI_append_intel-quark = " file://debug-fs.cfg"

# Bluetooth and Bluetooth LE support on Galileo Gen 2
SRC_URI_append_intel-quark = " file://bluetooth.cfg"

# Fix panic on USB fuzzing (Edison kernel is too old)
SRC_URI_append_intel-quark = " file://fix-usb-fuzzing-panic.patch"
SRC_URI_append_intel-core2-32 = " file://fix-usb-fuzzing-panic.patch"
SRC_URI_append_intel-corei7-64 = " file://fix-usb-fuzzing-panic.patch"
SRC_URI_append_beaglebone = " file://fix-usb-fuzzing-panic.patch"

# Galileo 2 GPIO
SRC_URI_append_intel-quark = " file://galileo2.cfg"
SRC_URI_append_intel-quark = " file://iio.cfg"
SRC_URI_append_intel-quark = " file://0001-i2c-ACPI-Use-0-to-indicate-that-device-does-not-have.patch"
SRC_URI_append_intel-quark = " file://0002-i2c-ACPI-Assign-IRQ-for-devices-that-have-GpioInt-au.patch"
SRC_URI_append_intel-quark = " file://0003-i2c-slave-add-error-messages-to-slave-core.patch"
SRC_URI_append_intel-quark = " file://0004-i2c-check-for-proper-length-of-the-reg-property.patch"
SRC_URI_append_intel-quark = " file://0005-i2c-core-fix-typo-in-comment.patch"
SRC_URI_append_intel-quark = " file://0006-i2c-core-Reduce-stack-size-of-acpi_i2c_space_handler.patch"
SRC_URI_append_intel-quark = " file://0007-i2c-core-only-use-set_scl-for-bus-recovery-after-cal.patch"
SRC_URI_append_intel-quark = " file://0008-i2c-fix-leaked-device-refcount-on-of_find_i2c_-error.patch"
SRC_URI_append_intel-quark = " file://0009-gpio-ACPI-Add-support-for-retrieving-GpioInt-resourc.patch"
SRC_URI_append_intel-quark = " file://0010-GPIO-ACPI-export-acpi_gpiochip_request-free-_interru.patch"
SRC_URI_append_intel-quark = " file://0011-gpio-ACPI-Return-EPROBE_DEFER-if-the-gpiochip-was-no.patch"
SRC_URI_append_intel-quark = " file://0012-i2c-ACPI-Rework-I2C-device-scanning.patch"
SRC_URI_append_intel-quark = " file://0013-mfd-core-redo-ACPI-matching-of-the-children-devices.patch"
SRC_URI_append_intel-quark = " file://0014-mfd-intel_quark_i2c_gpio-load-gpio-driver-first.patch"
SRC_URI_append_intel-quark = " file://0015-mfd-intel_quark_i2c_gpio-support-devices-behind-i2c-.patch"
SRC_URI_append_intel-quark = " file://0016-gpio-pca953x-store-driver_data-for-future-use.patch"
SRC_URI_append_intel-quark = " file://0017-gpio-pca953x-support-ACPI-devices-found-on-Galileo-G.patch"
SRC_URI_append_intel-quark = " file://0018-at24-enable-ACPI-device-found-on-Galileo-Gen2.patch"
SRC_URI_append_intel-quark = " file://0019-pwm-pca9685-enable-ACPI-device-found-on-Galileo-Gen2.patch"
SRC_URI_append_intel-quark = " file://0020-acpi-added-a-custom-DSDT-file.patch"
SRC_URI_append_intel-quark = " file://0021-gpio-pca953x-provide-GPIO-base-based-on-_UID.patch"
SRC_URI_append_intel-quark = " file://0022-pca9685-PCA9685-PWM-and-GPIO-multi-function-device.patch"
SRC_URI_append_intel-quark = " file://0023-acpi-updated-DSDT-table-for-SPI-devices.patch"
SRC_URI_append_intel-quark = " file://0024-spi-pxa2xx-fixed-ACPI-based-enumeration-of-SPI-devic.patch"
SRC_URI_append_intel-quark = " file://0025-staging-iio-add-support-for-ADC1x8s102.patch"
SRC_URI_append_intel-quark = " file://0026-adc1x8s102-support-ACPI-based-enumeration.patch"
SRC_URI_append_intel-quark = " file://0027-gpio-pca953x-add-drive-property.patch"

# Disable GFX console and support
SRC_URI_append_intel-core2-32 = " file://no-gfx.cfg"
SRC_URI_append_intel-corei7-64 = " file://no-gfx.cfg"

# enable usb gadget
SRC_URI_append_intel-quark = " file://usb-gadget.cfg"

KERNEL_MODULE_AUTOLOAD_append_intel-quark = " g_acm_ms"
KERNEL_MODULE_PROBECONF_append_intel-quark = " g_acm_ms"

module_conf_g_acm_ms_intel-quark = "options g_acm_ms file=/dev/mmcblk0p1 removable=1 idVendor=0x8086 idProduct=0xDEAD"

# Backport ambient capabilities support
SRC_URI_append_intel-quark = " file://0001-capabilities-ambient-capabilities.patch"
SRC_URI_append_intel-quark = " file://0002-capabilities-add-a-securebit-to-disable-PR_CAP_AMBIE.patch"
SRC_URI_append_intel-core2-32 = " file://0001-capabilities-ambient-capabilities.patch"
SRC_URI_append_intel-core2-32 = " file://0002-capabilities-add-a-securebit-to-disable-PR_CAP_AMBIE.patch"
SRC_URI_append_intel-beaglebone = " file://0001-capabilities-ambient-capabilities.patch"
SRC_URI_append_intel-beaglebone = " file://0002-capabilities-add-a-securebit-to-disable-PR_CAP_AMBIE.patch"
SRC_URI_append_intel-corei7-64 = " file://0001-capabilities-ambient-capabilities.patch"
SRC_URI_append_intel-corei7-64 = " file://0002-capabilities-add-a-securebit-to-disable-PR_CAP_AMBIE.patch"

SRC_URI_append_edison = " file://0001-edison-capabilities-ambient-capabilities.patch"
SRC_URI_append_edison = " file://0002-edison-capabilities-add-a-securebit-to-disable-PR_CAP_AMBIE.patch"
