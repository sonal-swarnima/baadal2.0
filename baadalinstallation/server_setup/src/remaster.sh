# This module is referenced from http://askubuntu.com/questions/122505
function remaster_ubuntu
{
  package_install genisoimage

  $ECHO_PROGRESS "Remastering Ubuntu ISO for preseeding"

  kickstart=$1
  transfer=$2
  iso_out=$3

  cache_pwd=$PWD

  cd $UTILS

  mkdir -p iso
  mount -o ro,loop $UBUNTU iso 1>>$LOGS/log.out 2>>$LOGS/log.err

  mkdir -p ubuntuiso 1>>$LOGS/log.out 2>>$LOGS/log.err
  cp -rT iso ubuntuiso

  umount iso
  rm -rf iso

  cd ubuntuiso
  echo en >isolinux/lang

  cp $kickstart ks.cfg

  cp -R $transfer transfer

  sed -i 's:--:ks=cdrom\:/ks.cfg --:g' isolinux/txt.cfg
  sed -i 's:^.*timeout.*$:timeout 10:g' isolinux/isolinux.cfg
  #sed -i '1id-i netcfg/dhcp_failed note' preseed/ubuntu-server.seed
  #sed -i '1id-i netcfg/dhcp_options select Configure network manually' preseed/ubuntu-server.seed

  cd ..
  rm -f $iso_out
  mkisofs -D -r -V "ATTENDLESS_UBUNTU" -cache-index -J -l -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -o $iso_out ubuntuiso 1>>$LOGS/log.out 2>>$LOGS/log.err

  rm -rf ubuntuiso

  cd $cache_pwd

  $ECHO_OK Ubuntu ISO remastered for preseeding
}

