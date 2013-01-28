#!/bin/bash
#
# SD card backup script - GENTOO ONLY!
# Does not work on OSX due to filesystem issues.
#
# Works only with the default SD card setup
# from http://wiki.gentoo.org/wiki/Raspberry_Pi_Quick_Install_Guide
#
# Example partitions (if SD card is /dev/sdb):
#
#    Device Boot      Start         End      Blocks   Id  System
# /dev/sdb1               1        3201      102424    c  W95 FAT32 (LBA)
# /dev/sdb2            3202        7298      131104   82  Linux swap / Solaris
# /dev/sdb3            7299      242560     7528384   83  Linux
#
# Partition-sizes do not matter, just the order (sdb1=boot, sdb3=root)
#
DEVICE_DEFAULT="/dev/sdb"
EXCLUDE_ROOT_DIRS="boot/ dev/ lost+found/ mnt/ proc/ tmp/"

MOUNTPOINT="/mnt/rpi_sdcard"
BACKUPDIR="/home/chris/rpi-backup"

unamestr=`uname`
if [ "$unamestr" != "Linux" ]; then
  echo "Error: Script only work on Linux"
  exit 1
fi

if [ $EUID -ne 0 ]; then
  echo "Error: Script needs to run as root"
  exit 2
fi

echo -n "Use '$DEVICE_DEFAULT' [Y/n]? "
read use_default

if [ "$use_default" == "" ] || [ "$use_default" == "y" ] || [ "$use_default" == "Y" ]; then
  dev=$DEVICE_DEFAULT
else
  echo -n "Please enter device location (eg. '/dev/sdb')"
  read dev
fi
dev_boot="$dev""1"
dev_root="$dev""3"

#
# Start doing the backup
#
echo "Using device '$dev' (boot:$dev_boot, root:$dev_root)"

CMD_TAR="tar -pcf"

DIR_BOOT="${MOUNTPOINT}/boot"
DIR_ROOT="${MOUNTPOINT}/root"

DATESTR=`date +%Y-%m-%d_%k:%M`
BACKUPDIR="${BACKUPDIR}/backup_${DATESTR}"

mkdir -p $DIR_BOOT
mkdir -p $DIR_ROOT
mkdir -p $BACKUPDIR

echo "Mounting'boot' ($dev_boot) and 'root' ($dev_root)"
mount $dev_boot $DIR_BOOT
mount $dev_root $DIR_ROOT

echo "Backing up 'boot' ($dev_boot). This will take a moment..."
cd $DIR_BOOT
$CMD_TAR "${BACKUPDIR}/boot.tar" *

echo "Backing up 'root'($dev_root). This will take a while..."
cd $DIR_ROOT
for dir in `ls -d */`;  do
    if [[ "$EXCLUDE_ROOT_DIRS" == *"$dir"* ]]; then
        echo "- skipping '$dir'"
    else
        # Remove trailing slash
        dname=`echo $dir | sed 's/[/]$//'`
        tarfile="${BACKUPDIR}/${dname}.tar"
        echo "- backing up '$dir' into '$tarfile'..."
        $CMD_TAR $tarfile $dname
    fi
done


echo "Cleaning up..."
umount $DIR_BOOT
umount $DIR_ROOT

echo "Backup successful."
