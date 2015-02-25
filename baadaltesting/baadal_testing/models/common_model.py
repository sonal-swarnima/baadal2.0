# -*- coding: utf-8 -*-
###################################################################################
# Added to enable code completion in IDE's.
if 0:
    import gluon
    global auth; auth = gluon.tools.Auth()
    from gluon import db, request, session
    from gluon import *  # @UnusedWildImport
    from applications.baadal.models import *  # @UnusedWildImport
###################################################################################

def get_task_num_form():
    form = FORM('Show:',
                INPUT(_name = 'task_num', _class='task_num', requires = IS_INT_IN_RANGE(1,101), _id='task_num_id'),
                A(SPAN(_class='icon-refresh'), _onclick = 'tab_refresh();$(this).closest(\'form\').submit()', _href='#'))
    return form



def get_task_form():
    form = FORM('Show:',
                INPUT(_name = 'Description', _class='task_num',_id='task_num_id'),
                A(SPAN(_class='icon-refresh'), _onclick = 'tab_refresh();$(this).closest(\'form\').submit()', _href='#'))
    return form


def get_task_list(events):

    tasks = []
    for event in events:
        print event.requester_id
        element = {'event_id'  :event.id,
                   'task_type' :event.task_type,
                   'task_id'   :event.task_id,
                   'server_name':event.server_name,
                   'test_case_list':event.test_case_list,
                   'user_name' :event.requester_id,
                   'attention_time':event.attention_time,
                   'start_time':event.start_time,
                   'file_name' :event.file_name,
                   'end_time'  :event.end_time}
        tasks.append(element)
    return tasks


def get_task_by_status(task_status, task_num):
    events = db(db.task_queue_event.status.belongs(task_status)).select(orderby = ~db.task_queue_event.start_time, limitby=(0,task_num))
    return get_task_list(events)



# Get user name and email
def get_user_details(user_id):
    if user_id < 0:
            return ('System User',None, None)
    else:
        user = db.auth_user[user_id]
        if user :
            username = auth_user.first_name + ' ' + auth_user.last_name
            email = auth_user.email if auth_user.mail_subscribed else None
 
            return (username, email, auth_user.username)
        else:
            return (None, None, None)


def get_full_name(user_id):
    return get_user_details(user_id)[0]
