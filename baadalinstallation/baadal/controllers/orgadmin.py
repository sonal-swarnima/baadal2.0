@auth.requires_login()
def list_all_orglevel_vm():
    try:
        vm_list = get_all_orglevel_vm_list()
        return dict(vmlist=vm_list)
    except:
        exp_handlr_errorpage()
