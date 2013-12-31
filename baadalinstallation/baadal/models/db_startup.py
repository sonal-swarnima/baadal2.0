# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
###################################################################################

import os
from helper import get_context_path
from gluon import current

def get_startup_data():
    from xml.dom import minidom

    xmldoc = minidom.parse(os.path.join(get_context_path(), 'static/startup_data.xml'))
    return xmldoc


if not db(db.constants).count():
    xmldoc = get_startup_data()
    itemlist = xmldoc.getElementsByTagName('table')
    
    for item in itemlist:
        
        tableref = db.get(item.attributes['name'].value)
        rows = item.getElementsByTagName('row')
        _dict = {}
        for row in rows:
            idx = False
            for attr in row.attributes.keys():
                _dict[attr] = row.attributes[attr].value
                if attr == 'id': idx = True
            tableref.insert(**tableref._filter_fields(_dict, id=idx))

        db.commit()

MAC_PRIVATE_IP_POOL = { 
                '54:52:00:01:17:98' : '10.208.21.74',
                '54:52:00:01:17:89' : '10.208.21.75',
                '54:52:00:01:17:88' : '10.208.21.76',
                '54:52:00:01:17:87' : '10.208.21.77',
                '54:52:00:01:17:86' : '10.208.21.78',
                '54:52:00:01:17:85' : '10.208.21.79',
                '54:52:00:01:17:84' : '10.208.21.80',
                '54:52:00:01:17:83' : '10.208.21.81',
                '54:52:00:01:17:82' : '10.208.21.82',
                '54:52:00:01:17:81' : '10.208.21.83',
                '54:52:00:01:17:80' : '10.208.21.84',
                '54:52:00:01:17:79' : '10.208.21.86',
                '54:52:00:01:17:78' : '10.208.21.87',
                '54:52:00:01:17:77' : '10.208.21.88',
                '54:52:00:01:17:76' : '10.208.21.89',
                '54:52:00:01:17:01' : '10.208.23.61',
                '54:52:00:01:17:02' : '10.208.23.62',
                '54:52:00:01:17:03' : '10.208.23.63',
                '54:52:00:01:17:04' : '10.208.23.64',
                '54:52:00:01:17:05' : '10.208.23.65',
                '54:52:00:01:17:06' : '10.208.23.66',
                '54:52:00:01:17:07' : '10.208.23.67',
                '54:52:00:01:17:92' : '10.208.23.68',
                '54:52:00:01:17:93' : '10.208.23.69',
                '54:52:00:01:17:94' : '10.208.23.70' }

current.MAC_PRIVATE_IP_POOL = MAC_PRIVATE_IP_POOL