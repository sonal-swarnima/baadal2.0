# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import request
###################################################################################
import logging

def get_configured_logger(name):
    logger = logging.getLogger(name)
    if (len(logger.handlers) == 0):
        # This logger has no handlers, so we can assume it hasn't yet been configured.
        import os
        formatter="%(asctime)s %(levelname)s %(funcName)s():%(lineno)d %(message)s"
        handler = logging.handlers.RotatingFileHandler(os.path.join(request.folder,'logs/%s.log'%(name)),maxBytes=1000000,backupCount=5)
        handler.setFormatter(logging.Formatter(formatter))

        handler.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

    return logger


def debug(message):
    logger.log(message, level='DEBUG')

def info(message):
    logger.log(message, level='INFO')
    
def warn(message):
    logger.log(message, level='WARNING')
    
def error(message):
    logger.log(message, level='ERROR')

logger = get_configured_logger(request.application)
from gluon import current
current.logger = logger
