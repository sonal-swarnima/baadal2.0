#!/bin/bash

source ./controller_installation.cfg 2>> /dev/null

Normal_pkg_lst=(build-essential make g++ libssl-dev)

#Funtion to check root login
Chk_Root_Login()
{
        username=`whoami`
        if test $username != "root"; then

                echo "LOGIN AS SUPER USER(root) TO INSTALL BAADAL!!!"
                echo "EXITING INSTALLATION......................................"
                exit 1
        fi

        echo "User Logged in as Root............................................"
}

Instl_Pkg()
{

        for pkg in ${Normal_pkg_lst[@]}; do
                DEBIAN_FRONTEND=noninteractive apt-get -y install $pkg --force-yes
        done

}

Instl_haproxy_Pkg()
{
    cd /baadal/baadal/baadaltesting/sandbox/utils
    tar -xvzf haproxy-1.5.8.tar.gz
                        mv haproxy-1.5.8 /tmp/haproxy-1.5.8

                        cd /tmp/haproxy-1.5.8
				make TARGET=linux2628 USE_OPENSSL=1                                
                                make PREFIX=/opt/haproxy-ssl install
                                cp /opt/haproxy-ssl/sbin/haproxy /usr/sbin/
                        cd -
    cd -


        echo "Packages Installed Successfully..................................."

}

Write_Haproxy_Conf()
{
        echo "rewriting your apache config file to use mod_wsgi"

        echo '
global
        log /dev/log    local0
        log /dev/log    local1 notice
        chroot /var/lib/haproxy
        user haproxy
        group haproxy
        daemon

defaults
        log     global
        mode    http
        option  httplog
        option  dontlognull
        timeout server 50000
        timeout connect 5000
        timeout client 50000

frontend www
        bind 172.16.0.8:80
        option http-server-close
        default_backend web-backend

frontend www-https
        bind 172.16.0.8:443 ssl crt /etc/ssl/self/self_signed.pem
        reqadd X-Forwarded-Proto:\ https
        default_backend web-backend

backend web-backend
        redirect scheme https if !{ ssl_fc }
        server web-1 172.16.0.9:80 check
        server web-1 172.16.0.7:80 check backup

listen stats :1936
        stats enable
        stats scope www
        stats scope web-backend
        stats uri /
        stats realm Haproxy\ Statistics
        stats auth user:password' > /baadal/baadal/baadalinstallation/haproxy.cfg
}

Create_SSL_Certi()
{
        cd /baadal/baadal/baadalinstallation
        echo "current path"
        pwd

        mkdir /etc/ssl/self
        echo "creating Self Signed Certificate................................."
        openssl genrsa 1024 > /etc/ssl/self/self_signed.key
        chmod 400 /etc/ssl/self/self_signed.key
        openssl req -new -x509 -nodes -sha1 -days 365 -key /etc/ssl/self/self_signed.key -config controller_installation.cfg > /etc/ssl/self/self_signed.cert
        openssl x509 -noout -fingerprint -text < /etc/ssl/self/self_signed.cert > /etc/ssl/self/self_signed.info
        cat /etc/ssl/self/self_signed.key /etc/ssl/self/self_signed.cert > /etc/ssl/self/self_signed.pem
}


Start_haproxy()
{
    haproxy -f haproxy.cfg
}


Chk_Root_Login
Instl_Pkg
Instl_haproxy_Pkg
Write_Haproxy_Conf
Create_SSL_Certi
Start_haproxy
