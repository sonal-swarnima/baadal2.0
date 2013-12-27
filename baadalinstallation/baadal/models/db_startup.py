# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import db
###################################################################################

import os
from helper import get_context_path

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
            for attr in row.attributes.keys():
                _dict[attr] = row.attributes[attr].value
            tableref.insert(**tableref._filter_fields(_dict))

        db.commit()
