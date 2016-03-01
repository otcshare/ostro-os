.. _UEFI-secure-boot:

UEFI Secure Boot
################

This technical note guides you through signing, installing, and using UEFI Secure
Boot. This documentation doesn't cover all possible tools you could use, but instead
selects one set of commonly available tools as an example.


Prerequisites
=============

These system prerequisites should be available in Debian and Ubuntu Linux systems as
well as Fedora.

- NSS certutil: in Debian-based systems this is found in the libnss3-tools package
  and in Fedora in nss-tools package
- pesign package


Creating Signing Keys
=====================

The following sections provide instructions for creating a certificate authority (CA) and
creating a UEFI signing keypair. We do recommend that you 
obtain a signing certificate from a real CA. This typically needs to be an
EV-type code signing certificate.

.. note:

   Certificate names, CN, OU, O, C and URL field values are examples only, you should
   use values correct for your organizaton and location for your case.
   Rules for these fields are the same as for any other X.509 certificate.


Creating a CA certificate
-------------------------

Create a directory for CA and initialize a certificate database::

    mkdir -p ~/efi-sign/ca
    certutil -d ~/efi-sign/ca -N

Generate a self-signed CA certificate::

    efikeygen -d ~/efi-sign/ca --ca --self-sign --nickname="UEFI Test CA" \
       --common-name="CN=UEFI Test CA,OU=OTC,O=Intel Corporation,C=FI" \
       --url="http://www.intel.com" --serial=00


Creating and Signing a Signing Certificate
------------------------------------------

Generate a signing key and sign it with the CA::

    efikeygen -d ~/efi-sign/ca --signer="UEFI Test CA" --nickname="UEFI Secure Boot Signer" \
       --common-name="CN=UEFI Secure Boot Signer,OU=OTC,O=Intel Corporation,C=FI" \
       --url="http://www.intel.com" --serial=01

Export the signing certificate as PKCS#12::

    pk12util -d ~/efi-sign/ca -o ~/efi-sign/ca/signer.p12 -n "UEFI Secure Boot Signer"

Create a directory for signer and initialize certificate database::

    mkdir -p ~/efi-sign/signer
    certutil -d ~/efi-sign/signer -N

Import the signed keypair to the signer certificate database::

    pk12util -d ~/efi-sign/signer -i ~/efi-sign/ca/signer.p12


Using the Signing Key
---------------------

Export the CA and signer public keys in DER format::

    certutil -d ~/efi-sign/ca -L -n "UEFI Test CA" \
       -r >~/efi-sign/ca/uefi-test-ca.cer
    certutil -d ~/efi-sign/signer -L -n "UEFI Secure Boot Signer"  \
       -r >~/efi-sign/signer/uefi-test-sign.cer

Copy those files to a USB flash stick for later use and safe-keeping.

Sign the EFI binary using the signing key, assuming the EFI partition is mounted on /mnt::

    pesign -s -n ~/efi-sign/signer -c "UEFI Secure Boot Signer" \
       -i /mnt/EFI/BOOT/bootx64.efi -o /tmp/bootx64.efi
    sudo mv /tmp/bootx64.efi /mnt/EFI/BOOT/


Installing Signing Keys to AMI BIOS
===================================

#) Enter BIOS Setup program by hitting Del key during POST.
#) In the Setup program, select Security / Secure Boot Menu
#) Secure Boot: Enabled
#) Secure Boot Mode: Custom
#) Proceed to Key Management sub-menu
#) Delete All Secure Boot Variables
#) Set new PK

   a) Answer No to load the key from a file
   b) Select USB flash storage device
   c) Select the uefi-test-ca.cer file
   d) Select import as X.509 certificate

#) Append new KEK

   a) Answer No to load the key from a file
   b) Select USB flash storage device
   c) Select the uefi-test-sign.cer file
   d) Select import as X.509 certificate

#) Append new Authorized Signature

   a) Answer No to load the key from a file
   b) Select USB flash storage device
   c) Select the uefi-test-sign.cer file
   d) Select import as X.509 certificate

#) Exit and save the settings

You may also want to set Administrator Password to BIOS Setup to avoid
"evil maid" attacks from interfering with your Secure Boot key configuration.


Booting Up with Secure Boot
===========================

From this point onward, the system will only boot up with a properly signed
EFI binary. Once the kernel is up and running, responsibility for system
integrity is transferred to the kernel.

