rm -r /etc/apache2/ssl/
umount /var/nfs/tftpboot/ubuntu
rm -r /var/nfs
rm -r /var/www/*
ifconfig eth0 down
/etc/init.d/networking restart
