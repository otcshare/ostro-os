.. _authorized-keys:

Adding Authorized Keys for Remote ssh Access
############################################

In Ostro |trade| OS **development** images only, root automatically gets logged in on a local 
console or serial port connection. By default though, Ostro OS prevents remote logins to your 
target device.  You can enable remote access as root via ``ssh`` in your development image by installing 
your personal public key in the ``~root/.ssh/authorized_keys`` file.  This tech note explains how.

You’ll first need to have a private/public key pair on your workstation to enable ``ssh`` access to the target device.  You can use
an existing host ssh key pair, found in ``$HOME/.ssh``. 
A private/public key pair will be stored in two files for example, ``.ssh/id_rsa`` and ``.ssh/id_rsa.pub``.

If you don't see private/public key files, you'll need to generate them.

Generating a Private/Public Key Pair
====================================

On Linux systems (or Windows systems with `Git Bash`_ installed) use the ``ssh-keygen`` utility to generate
an ssh key pair by following its instructions ::

   $ ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

   # Creates a new ssh key using the provided email as a label
   Generating public/private rsa key pair.
   Enter a file in which to save the key ($HOME/.ssh/id_rsa): [Press enter]
   # Press enter to accept the default file names or provide a name for development use, for example

   Enter passphrase (empty for no passphrase): [Type a passphrase]
   # If you're only using this key for local development work, you could skip a passphrase and press Enter
   Enter same passphrase again: [Type passphrase again]

At this point the tool will generate an ssh key pair and store the public and private keys in separate files in the ``$HOME/.ssh/`` folder.

On Windows systems, you can also use **PuTTYgen** to generate a key pair:

#. If needed, download PuTTYgen from the `PuTTY download page`_ (you may already have
   it installed on your Windows system).  
#. Launch the program and click the **Generate** button and follow its instructions.  
   (If you're only using this key for 
   local development work, you could skip a passphrase.) 
#. Save the two key-pair files by clicking the **Save public key** and **Save private key** buttons.
#. You'll also need a one-line format of your public key for adding to the ``authorized_keys`` file described below. 
   Select and copy all the text displayed in PuTTYgen's *Public key for pasting into Open SSH authorized_keys file* window 
   and, using a text editor such as notepad, save this text to a file you'll be using later.

If you'll be using the ``PuTTY`` client for ssh access, open the PuTTY client and provide the private key file name in the "Private key file for authentication" field on the PuTTY Configuration screen options (under Connection/SSH/Auth). 

You can read more information about key generation and use of pass phrases from GitHub's `generating an ssh key help`_ and other online sources.

.. _`PuTTY download page`: http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html
.. _`Git Bash`: https://git-for-windows.github.io/
.. _`generating an ssh key help`: https://help.github.com/articles/generating-an-ssh-key/


Build-Time Configuration of Authorized Keys
=========================================== 

The recommended approach for enabling remote ``ssh`` access is to install authorized public ssh keys by 
setting OSTRO_ROOT_AUTHORIZED_KEYS in your ``local.conf`` configuration file and building them into your image.

#. Look in your ``local.conf`` file and find the line:::

   # OSTRO_ROOT_AUTHORIZED_KEYS = "ssh-rsa AAA...== john@example.com\nssh-dss AA...FPaQ== joan@example.com"

   Uncomment it, and replace the quoted string with the contents of the public key file(s) you'd like to authorize
   for remote access.  (If you used PuTTYgen, use the one-line public key text file's contents you saved.) Separate
   multiple public keys with "\\n", as in the example shown. 
   The contents of this configuration key will be placed in ``~root/.ssh/authorized_keys`` when the image is built.

#. Make note of your devices IP address using ``ifconfig`` for example, if you've got a local console or serial port connection.

#. Login from your host using ``ssh`` with your private key (from host) and the IP address of your device, for example: ::

    $ ssh root@192.168.2.2 -i $HOME/.ssh/id_rsa

   Or on Windows, you can use the ``PuTTY`` client (configured with your private ssh key) for ssh access.  
   Since root does not have a password, you won't be asked for one and you'll be logged in.


Run-Time Configuration of Authorized Keys
=========================================

On an existing Ostro OS image running on your target device, you can follow these steps to copy your public key from your host 
computer to the ``authorized_keys`` file on the target. After a reboot, this will configure the system to permit remote ``ssh`` access using your 
private key.

#. Connect to your target device using a serial port terminal program
#. Add the contents of your workstation’s ``$HOME/.ssh/id_rsa.pub`` public key file to the device's ``~root/.ssh/authorized_keys`` using 
   one of these methods (if you used PuTTYgen to generate the keys, use the one-line public key text file's contents you saved.):

   * Display the contents of your ``$HOME/.ssh/id_rsa.pub`` file and cut it, then edit the ``authorized_keys`` file 
     on the target with ``vi`` and paste the key information on a new line (multiple authorized keys are permitted,
     one per line)::

          ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABA...sp8QJGV elena@example.com
          ssh-rsa AABAQDYoqTVJoNmtiDz...yc8bcvxxs/E8okDby patrick@example.com

   * Alternatively, copy the ``id_rsa.pub`` to a USB thumb drive on the host, plug it into your target system, 
     and use ``cat`` to append its contents, something like this
     (your device name may be different)::
  
          # mkdir key
          # mount /dev/sdb1 key
          # cat key/id_rsa.pub >> ~root/.ssh/authorized_keys
  
#. Make note of your devices IP address (using ``ifconfig`` for example) and reboot the device.
#. Login from your host using ``ssh`` with your private key (from host) and the IP address of your device, for example: ::

    $ ssh root@192.168.2.2 -i $HOME/.ssh/id_rsa

   Since root does not have a password, you won't be asked for one and you'll be logged in.


