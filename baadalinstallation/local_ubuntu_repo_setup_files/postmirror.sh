#!/bin/bash
# environment
export TEMPFILE=/tmp/apt-mirror-mail.tmp.${RANDOM}
export LOGFILE=/var/local_rep/apt-mirror.log
 
# run clean script
CS=/var/local_rep/var/clean.sh
chmod 777 ${CS}
sh ${CS} 2>&1 >> ${LOGFILE}
 
# send status mail to apt-mirror
echo From: `whoami`@`hostname` >> ${TEMPFILE}
echo To: `whoami` >> ${TEMPFILE}
echo Subject: apt-mirror fetch status from `date` >> ${TEMPFILE}
echo >> ${TEMPFILE}
cat ${LOGFILE} >> ${TEMPFILE}
 
rm ${TEMPFILE}
