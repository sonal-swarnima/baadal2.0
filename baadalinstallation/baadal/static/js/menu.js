    function displayMainMenu(){
    	//alert('uff');
      if(jQuery('#menu_admin').length != 0){
      	loadMenu(jQuery('#menu_admin'), true);
      	loadMenu(jQuery('#menu_orgadmin'), false);
      	loadMenu(jQuery('#menu_faculty'), false);
      	loadMenu(jQuery('#menu_user'), false);
        jQuery('#configure').siblings().hide();
      }
      else if(jQuery('#menu_orgadmin').length != 0){
      	loadMenu(jQuery('#menu_orgadmin'), true);
      	loadMenu(jQuery('#menu_faculty'), false);
      	loadMenu(jQuery('#menu_user'), false);
      }
      else if(jQuery('#menu_faculty').length != 0){
      	loadMenu(jQuery('#menu_faculty'), true);
      	loadMenu(jQuery('#menu_user'), false);
      }
      else if(jQuery('#menu_user').length != 0){
      	loadMenu(jQuery('#menu_user'), true);
      }else
      {
      	$.cookie('menu_admin', null, {path: '/' });
      	$.cookie('menu_orgadmin', null, {path: '/' });
      	$.cookie('menu_faculty', null, {path: '/' });
      	$.cookie('menu_user', null, {path: '/' });
      }
    }
    
    function loadMenu(obj, show){
    	obj_id = obj.attr('id');
    	objs = obj.parent().siblings();
    	is_visible = $.cookie(obj_id);
    	if(is_visible == 'true'){
    		objs.show();
    	}else if(is_visible == 'false'){
    		objs.hide();
    	}else{
    		if(show){
    			objs.show();
    		}else{
    			objs.hide();
    		}
    	}
    	addToCookie(obj);
    }
	
    function addToCookie(obj){
    	obj_id = obj.attr('id');
    	is_visible = obj.parent().next().is(':visible');
    	$.cookie(obj_id, is_visible, {path: '/' });
    }
    
    function tab_refresh(){
    	$.cookie('tab_index',$("#tabs-task").tabs('option', 'active'));
    }
