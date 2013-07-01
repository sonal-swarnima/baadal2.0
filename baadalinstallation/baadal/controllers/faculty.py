# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    from gluon import auth
###################################################################################

@auth.requires_login()
def add_user_to_vm():
    return dict()
