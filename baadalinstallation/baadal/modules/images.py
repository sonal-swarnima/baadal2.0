
imageprofiles = [
{
    'Id' : 'repository:5000/python' ,
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
    'updatemysql':False,
    'workingdir':'/root'
},
{
    'Id' : 'repository:5000/djangogit' ,
    'cmd' : 'bash -c "tail -f /dev/null"',
    #'cmd' : 'bash',
    #'mountdestdir' : '/usr/src/app',
    'mountdestdir':None,
    'restartpolicy' : 2    ,
    'port' : 8000,
    'type' : 'python +django',
    'permissiondrop' : [],
    'permissionadd' : [],
    'links' : [],
     'updatemysql':False,
     'workingdir':'/usr/src/app'
},
{
    'Id' : 'repository:5000/apachegit' ,
    'cmd' : 'bash -c "tail -f /dev/null"',
    #'cmd' : 'bash',
    #'mountdestdir' : '/var/www/app',
    'mountdestdir':None,
    'restartpolicy' : 2    ,
    'port' : 80,
    'type' : 'php +apache',
    'permissiondrop' : ["SETFCAP","SETPCAP","SYS_CHROOT"],
    'permissionadd' : [],
         'links' : [],
     'updatemysql':False,
     'workingdir':'/var/www/app'
},{
'Id':'repository:5000/wordpress',
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
    
     'workingdir':'/var/www/html'
},{
'Id':'repository:5000/ubuntu',
'cmd' : 'bash -c "tail -f /dev/null"',
    #'cmd' : 'bash',
    'mountdestdir' : None,
    'restartpolicy' : 2    ,
     'port' : None,
    'type' : 'ubuntu',
    'permissiondrop' : [],
    'permissionadd' : [],
    'links' : [],
     'updatemysql':False,
     'workingdir':'/root'
},
{
    'Id' : 'repository:5000/apachephpmysqlgit' ,
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
     'updatemysql':True,
     'workingdir':'/var/www/app'
},
{
    'Id' : 'repository:5000/gcc' ,
    'cmd' : 'bash -c "tail -f /dev/null"',
    #'cmd' : 'bash',
    #'mountdestdir' : '/var/www/app',
     'mountdestdir' : None,
    'restartpolicy' : 2    ,
    'port' : None,
    'type' : 'gcc',
    'permissiondrop' : ["SETFCAP","SETPCAP","SYS_CHROOT"],
    'permissionadd' : [],
         'links' : [],
     'updatemysql':False,
     'workingdir' :'/root'
},
{
'Id' : 'repository:5000/matlab' ,
    'cmd' : '',
    #'cmd' : 'bash',
    #'mountdestdir' : '/var/www/app',
     'mountdestdir' : None,
    'restartpolicy' : 2    ,
    'port' : 8080,
    'type' : 'matlab',
    'permissiondrop' : [],
    'permissionadd' : [],
         'links' : [],
     'updatemysql':False,
     'workingdir' :'/usr/local'
},{
'Id' : 'repository:5000/python_ml' ,
    'cmd' : '',
    #'cmd' : 'bash',
    #'mountdestdir' : '/var/www/app',
     'mountdestdir' : None,
    'restartpolicy' : 2    ,
    'port' : None,
    'type' : 'python+mldev',
    'permissiondrop' : [],
    'permissionadd' : [],
         'links' : [],
     'updatemysql':False,
     'workingdir' :'/usr/src/app'


}
]

def getImageProfile(templateid):
    return imageprofiles[templateid-1];

def getImageProfileList():
    return imageprofiles;

def getImage(imageId):
    print(imageId)
    for i,imageprofile in enumerate(imageprofiles):
        if imageprofile['Id'] == imageId:
            imageprofile['templateid'] = i+1
            return imageprofile
    
    return {'templateid':1,'type':'Unknown'}
