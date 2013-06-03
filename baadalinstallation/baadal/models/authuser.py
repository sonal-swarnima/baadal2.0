# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import *  # @UnusedWildImport
    import gluon
    import logger
    global auth; auth = gluon.tools.Auth()
###################################################################################

def login_callback(form):
    print(form.vars.username)
    logger.warn(auth.is_logged_in())
    logger.debug(auth.user.username)
