# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
###################################################################################
import logging

logger = logging.getLogger("web2py.app.baadal")
logger.setLevel(logging.DEBUG)

def debug(message):
    logger.log(message, level='DEBUG')

def info(message):
    logger.log(message, level='INFO')
    
def warn(message):
    logger.log(message, level='WARNING')
    
def error(message):
    logger.log(message, level='ERROR')