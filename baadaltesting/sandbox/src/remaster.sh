# This module is referenced from http://askubuntu.com/questions/122505
function remaster_ubuntu
{
  $ECHO_PROGRESS "Remastering Ubuntu ISO for preseeding"

  kickstart=$1
  iso_out=$2

  cache_pwd=$PWD

  cd $UTILS

  mkdir -p iso
  mount -o ro,loop $UBUNTU iso

  mkdir -p ubuntuiso
  cp -rT iso ubuntuiso

  cd ubuntuiso
  echo en >isolinux/lang

  cp $kickstart ks.cfg
  #cp ../ks.preseed .
 
  sed -i 's:--:ks=cdrom\:/ks.cfg --:g' isolinux/txt.cfg
  sed -i 's:^.*timeout.*$:timeout 10:g' isolinux/isolinux.cfg

  cd ..
  rm -f $iso_out
  mkisofs -D -r -V "ATTENDLESS_UBUNTU" -cache-index -J -l -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -o $iso_out ubuntuiso 1>>$LOGS/log.out 2>>$LOGS/log.err

  umount iso
  rm -rf iso
  rm -rf ubuntuiso
  
  cd $cache_pwd

  $ECHO_OK Ubuntu ISO remastered for preseeding
}

