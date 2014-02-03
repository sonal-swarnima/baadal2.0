python-ldap 
perl-modules 
libpam-krb5 
libpam-cracklib 
php5-auth-pam 
libnss-ldap 
krb5-user 
ldap-utils 
libldap-2.4-2 
nscd 
ca-certificates 
ldap-auth-client 
krb5-config "OR" libkrb5-dev




from gluon.contrib.login_methods.pam_auth import pam_auth
auth.settings.login_methods=[pam_auth()]
