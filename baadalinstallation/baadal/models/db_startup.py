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
        if tableref:
            rows = item.getElementsByTagName('row')
            attrib_dict = {}
            for row in rows:
                idx = False
                for attr in row.attributes.keys():
                    attrib_dict[attr] = row.attributes[attr].value
                    if attr == 'id': idx = True
                tableref.insert(**tableref._filter_fields(attrib_dict, id=idx))
    
            db.commit()
