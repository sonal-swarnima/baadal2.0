def request_vm():

    form = get_create_vm_form()
    
    if form.accepts(request.vars, session, onvalidation=set_configuration_elem):
        add_user_to_vm(form.vars.id)
        logger.debug('VM requested successfully')
        add_vm_request_to_queue(form.vars.id)
        redirect(URL(c='default', f='index'))
    return dict(form=form)


def list_my_vm():
    vm_list = get_my_vm_list()
    return dict(vmlist=vm_list)

