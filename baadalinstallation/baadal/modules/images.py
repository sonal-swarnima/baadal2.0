
imageprofiles = [
{
    'Id' : '10.237.20.236:5000/python' ,
    'cmd' : 'bash -c "tail -f /dev/null"',
    #'cmd' : 'bash',
    #'mountdestdir' : '/usr/app/src',
    'mountdestdir':None,
    'restartpolicy' : 2    ,
    'type': 'python',
    'port' : 'None' ,
    'permissiondrop' : [],
    'permissionadd' : [],
    'links' : [],
    'updatemysql':False
},
{
    'Id' : '10.237.20.236:5000/djangopythonweb' ,
    'cmd' : [],
    #'cmd' : 'bash',
    #'mountdestdir' : '/usr/src/app',
    'mountdestdir':None,
    'restartpolicy' : 2    ,
    'port' : 8000,
    'type' : 'python +django',
    'permissiondrop' : [],
    'permissionadd' : [],
    'links' : [],
     'updatemysql':False
},
{
    'Id' : '10.237.20.236:5000/apachephusion' ,
    'cmd' : [],
    #'cmd' : 'bash',
    #'mountdestdir' : '/var/www/app',
    'mountdestdir':None,
    'restartpolicy' : 2    ,
    'port' : 80,
    'type' : 'php +apache',
    'permissiondrop' : ["SETFCAP","SETPCAP","SYS_CHROOT"],
    'permissionadd' : [],
         'links' : [],
     'updatemysql':False
},{
'Id':'10.237.20.236:5000/wordpress',
'cmd' : 'bash -c "tail -f /dev/null"',
    #'cmd' : 'bash',
    'mountdestdir' : None,
    'restartpolicy' : 2    ,
    'port' : 80,
    'type' : 'wordpress',
    'permissiondrop' : [],
    'permissionadd' : [],
    #'links' : [('/some-mysql' ,'mysql')]
    'links':[],
    'updatemysql':True,
    
},{
'Id':'10.237.20.236:5000/ubuntu',
'cmd' : 'bash -c "tail -f /dev/null"',
    #'cmd' : 'bash',
    'mountdestdir' : None,
    'restartpolicy' : 2    ,
     'port' : None,
    'type' : 'ubuntu',
    'permissiondrop' : [],
    'permissionadd' : [],
    'links' : [],
     'updatemysql':False
},
{
    'Id' : '10.237.20.236:5000/apachemysql' ,
    'cmd' : 'bash -c "tail -f /dev/null"',
    #'cmd' : 'bash',
    #'mountdestdir' : '/var/www/app',
     'mountdestdir' : None,
    'restartpolicy' : 2    ,
    'port' : 80,
    'type' : 'php +apache+mysql',
    'permissiondrop' : ["SETFCAP","SETPCAP","SYS_CHROOT"],
    'permissionadd' : [],
         'links' : [],
     'updatemysql':True
}
]

def getImageProfile(templateid):
    return imageprofiles[templateid-1];

def getImageProfileList():
    return imageprofiles;
