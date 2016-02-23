#!/bin/bash
username=$1
displayname=$2
#email=$2
size=$2
subuser=$username":swift"
echo $username
echo $subuser
#echo $email
echo $size
ssh -X root@172.16.0.73 "./object_user.sh $username $size"
rm /home/key.txt
scp root@172.16.0.73:/home/key.txt /home/key.txt
chown www-data:www-data /home/key.txt
