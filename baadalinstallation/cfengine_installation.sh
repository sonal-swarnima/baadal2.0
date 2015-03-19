source /baadal/baadal/baadalinstallation/controller_installation.cfg 2>> /dev/null

Pkg_List=(git zip unzip tar openssh-server build-essential python2.7:python2.5 python-dev vim)
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


Instl_cfengine_Pkg()
{
    cd /baadal/baadal/baadaltesting/sandbox/utils
    sudo dpkg -i cfengine-community_3.6.3-1_amd64.deb
}


Instl_Pkg(){
    for pkg in ${Pkg_List[@]}; do
        DEBIAN_FRONTEND=noninteractive apt-get -y install $pkg --force-yes
    done

    Instl_cfengine_Pkg
}

Setup_Cfengine_Server()
{

    cd /var/cfengine/masterfiles
    mkdir myPromises
    mkdir myTemplates
    
    #start cfengine server
    cp -fr /var/cfengine/masterfiles/* /var/cfengine/inputs/
    /etc/init.d/cfengine3 start
 
    cp -rf /baadal/baadal/baadalinstallation/server_setup/src/cfengine/promise_scripts/* /var/cfengine/masterfiles/
 
    #generate key to be shared among hosts
    mkdir /var/cfengine/masterfiles/myPromises/host_ssh_key
    ssh-keygen -t rsa -f /var/cfengine/masterfiles/myPromises/host_ssh_key/id_rsa -N ""

    touch /var/cfengine/masterfiles/myPromises/host_ssh_key/authorized_keys
    wget http://$CONTROLLER_IP/.ssh/id_rsa.pub
    cat id_rsa.pub > /var/cfengine/masterfiles/myPromises/host_ssh_key/authorized_keys
    cat /var/cfengine/masterfiles/myPromises/host_ssh_key/id_rsa.pub >> /var/cfengine/masterfiles/myPromises/host_ssh_key/authorized_keys

    #Bootstrap cfengine server in the end
    cf-agent --bootstrap $CFENGINE_IP
}

Chk_Root_Login
Instl_cfengine_Pkg
Instl_Pkg
Setup_Cfengine_Server
