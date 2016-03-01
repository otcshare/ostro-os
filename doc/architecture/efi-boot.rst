.. _efi-boot:


EFI support in Ostro |trade| OS
###############################

On x86 devices, Ostro OS supports EFI mode through the creation
of a single-binary EFI application.


Background
==========
On typical distros (Fedora, Ubuntu, etc.) there are distinct
components that implement:

- boot loader,
- kernel command line (usually part of the bootloader configuration),
- kernel, and
- initramfs (if present)

This typical model provides more choices to the user, but it introduces
additional points of failure in the security chain because the EFI BIOS
only verifies the authenticity of the bootloader.
The bootloader has the burden of verifying the kernel, the initramfs,
and its own configuration data, which must be signed individually.

The first part (BIOS verification of the bootloader) cannot be avoided,
because it's the first ring of the chain of trust.
The following (BIOS verification of kernel and initramfs) can only
introduce an additional risk, due to different implementation of what
is basically the same set of functionality already present in the BIOS.


EFI support in Ostro OS
=======================
Ostro OS relies on a single-binary approach, where the bootloader
(but only a small part of it), the kernel command line, the kernel and
the initramfs are all packaged in a single signed file.

Each component is placed in a separate section within the combo-binary.
Only the EFI stub is used from the bootloader.

The stub accomplishes these main functions:

- Make the entire combo binary look like an EFI application to the EFI BIOS.
- Extract the kernel command line from its section inside the binary.
- Hand-over execution to the kernel section.

Advantages
----------

- Only one file is handled, where most of the handling is performed by the
  BIOS, and only one implementation exists for each functionality.
- There is no risk of components going out of sync: there is only one file to update.
- There is less vulnerability to corruption of the EFI partition, during update.
  The EFI partition is of type FAT, as required by the EFI specifications.
  It is significantly more exposed to corruptions than other
  more modern file systems.

Disadvantages
-------------

- Multiple boot options support requires support
  through the EFI BIOS (more on this in the following point) but not all
  BIOS implementations fully implement parts of the EFI
  specifications that are not indispensable for booting.
- The implementation of multi-boot selection will require either the creation
  of an additional EFI binary or the implementation of an EFI shell script.
  This sort of expertise might not be very common among Ostro OS developers.
- Changing the contents of the command line requires rebuilding the EFI combo,
  unless there is a mechanism in place to support an alternative (to be developed).
