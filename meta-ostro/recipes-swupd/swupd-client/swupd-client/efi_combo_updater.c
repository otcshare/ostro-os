#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <glib.h>

#define OUTBUF_SIZE 4096

const char EFI_TYPE[] = "EF00";
const char EFI_BACKUP_TYPE[] = "2700";

const char ROOT_BLOCK_DEVICE_CMD[] =
  "mount |grep \"/dev/sd\" "
  "|grep \"on / type\" |sed 's/[0-9].*$//'";

const char ROOT_BLOCK_DEVICE_SD_CMD[] =
  "mount |grep \"/dev/mmcblk\" "
  "|grep \"on / type\" |sed 's/p[0-9].*$//'";

const char EFI_PARTITION_NR_CMD[] =
  "sgdisk -p %s 2> /dev/null |grep %s "
  "|sed -e 's/[ ]*//' |cut -d ' ' -f 1";

const char EFI_BACKUP_PARTITION_NR_CMD[] =
  "sgdisk -p %s 2> /dev/null |grep %s "
  "|sed -e 's/[ ]*//' |cut -d ' ' -f 1";


/* Runs a command, with optional parameters.
   The combined stderr & stdout are returned through
   a pointer, if provided.
   The retval is the retval of the command.*/

int execute(char **output, const char *fmt, ...) {
  va_list ap;
  FILE *fp;
  char *command;
  static char outbuf[OUTBUF_SIZE];
  unsigned int answer_len;
  int i;

  va_start(ap, fmt);
  assert(vasprintf(&command, fmt, ap) > 0);
  va_end(ap);
  #if defined(DEBUG)
  printf("COMMAND => %s\n", command);
  #endif
  assert(fp = popen(command, "r"));
  fgets(outbuf, sizeof(outbuf)-1, fp);
  if (output) {
    answer_len = strnlen(outbuf, OUTBUF_SIZE - 1);
    assert(answer_len <= (OUTBUF_SIZE - 1));
    for (i = 0; i <= answer_len; i++)
      if (outbuf[i] == '\n')
        outbuf[i] = '\0';
    #if defined(DEBUG)
    printf("RESULT => %s\n"
           "answer_len => %u\n", outbuf, answer_len);
    #endif
    if (answer_len > 1) {
      *output = malloc(answer_len);
      strcpy(*output, outbuf);
    }
    else
      *output = 0;
  }
  free(command);
  return WEXITSTATUS(pclose(fp));
}

int main(void) {
  char *root_block_device = NULL;
  char *efi_partition_nr;
  char *efi_backup_partition_nr;
  char part_prefix[] = { '\0', '\0'};
  unsigned int update_needed;
  int retval;

  /* Identify the block device with the rootfs, which is the
     same containing the EFI partitions.*/
  execute(&root_block_device, ROOT_BLOCK_DEVICE_CMD);
  if (root_block_device == NULL) {
    execute(&root_block_device, ROOT_BLOCK_DEVICE_SD_CMD);
    *part_prefix = 'p';
  }
  printf("ROOT_BLOCK_DEVICE %s\n", root_block_device);
  printf("Partition prefix: \"%s\"\n", part_prefix);

  /* Identify the active EFI partition. */
  assert(execute(&efi_partition_nr, EFI_PARTITION_NR_CMD,
                 root_block_device, EFI_TYPE) == 0);
  printf("EFI_PARTITION_NR %s\n", efi_partition_nr);

  /* Identify the inactive EFI partition. */
  assert(execute(&efi_backup_partition_nr, EFI_BACKUP_PARTITION_NR_CMD,
                 root_block_device, EFI_BACKUP_TYPE) == 0);
  printf("EFI_BACKUP_PARTITION_NR %s\n", efi_backup_partition_nr);

  /* Cleanup possible leftovers.*/
  execute(NULL, "umount /tmp/mnt 2>&1");
  execute(NULL, "rm -rf /tmp/mnt 2>&1");

  /* Check if the current efi combo file is up-to-date. */
  assert(execute(NULL, "mkdir /tmp/mnt 2>&1") ==0);
  assert(execute(NULL, "mount %s%s%s /tmp/mnt/ 2>&1",
                       root_block_device, part_prefix,
                       efi_partition_nr) == 0);
  update_needed = execute(NULL, "diff /tmp/mnt/EFI/BOOT/*.efi "
                                "/boot/EFI/BOOT/*.efi 2>&1");

  if (!update_needed)
    return 0;

  /*Update required, so mount the inactive EFI partition.*/
  assert(execute(NULL, "umount /tmp/mnt/ 2>&1") == 0);
  assert(execute(NULL, "mount %s%s%s /tmp/mnt/ 2>&1",
                       root_block_device, part_prefix,
                       efi_backup_partition_nr) == 0);

  /* Nuke the old content and deploy the new one.*/
  assert(execute(NULL, "rm /tmp/mnt/EFI/BOOT/*") == 0);
  assert(execute(NULL, "sync") == 0);
  assert(execute(NULL, "cp /boot/EFI/BOOT/*.efi "
                       "/tmp/mnt/EFI/BOOT/") == 0);
  assert(execute(NULL, "sync") == 0);
  assert(execute(NULL, "umount /tmp/mnt/ 2>&1") == 0);
  assert(execute(NULL, "sync") == 0);


  /* Make the inactive partition active and vice-versa.*/
  assert(execute(NULL, "sgdisk -t %s:%s -t %s:%s %s",
                       efi_partition_nr, EFI_BACKUP_TYPE,
                       efi_backup_partition_nr, EFI_TYPE,
                       root_block_device) == 0);
  assert(execute(NULL, "sync") == 0);
}
