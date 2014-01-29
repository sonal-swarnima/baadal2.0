#!/usr/bin/env python
# coding: utf8
import os
import ConfigParser
import MySQLdb as mdb
import xml.etree.ElementTree as ET

def xml_connect():
	tree = ET.parse(os.path.join(get_context_path(),'static/testdata.xml'))# parsing the xml file
	root = tree.getroot()
	return root

def get_config_file():
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(get_context_path(),'static/db.conf'));
    return config
    
def get_context_path():
    ctx_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
    return ctx_path 
    
def db_connection():
    Config = ConfigParser.ConfigParser()
    Config.read(os.path.join(get_context_path(),'static/db.conf'))
    host_ip=Config.get("db_info","host_ip")
    database_user_name=Config.get("db_info","database_user_name")
    database_name=Config.get("db_info","database_name")
    password=Config.get("db_info","password")
    db=mdb.connect(host_ip,database_user_name,password,database_name)
    return db


def get_app_name():
    Config = ConfigParser.ConfigParser()
    Config.read(os.path.join(get_context_path(),'static/db.conf'))
    path=Config.get("web2py_app_name","path")
    return path
