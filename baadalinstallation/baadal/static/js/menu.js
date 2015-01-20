    function displayMainMenu(){

      if(jQuery('#menu_admin').length != 0){
          loadMainMenu(jQuery('#menu_admin'), true);
          loadSubMenu(jQuery('#configure'), false);
          loadMainMenu(jQuery('#menu_orgadmin'), false);
          loadMainMenu(jQuery('#menu_faculty'), false);
          loadMainMenu(jQuery('#menu_user'), false);
      }
      else if(jQuery('#menu_orgadmin').length != 0){
          loadMainMenu(jQuery('#menu_orgadmin'), true);
          loadMainMenu(jQuery('#menu_faculty'), false);
          loadMainMenu(jQuery('#menu_user'), false);
      }
      else if(jQuery('#menu_faculty').length != 0){
          loadMainMenu(jQuery('#menu_faculty'), true);
          loadMainMenu(jQuery('#menu_user'), false);
      }
      else if(jQuery('#menu_user').length != 0){
          loadMainMenu(jQuery('#menu_user'), true);
      }else
      {
          $.cookie('menu_admin', null, {path: '/' });
          $.cookie('menu_orgadmin', null, {path: '/' });
          $.cookie('menu_faculty', null, {path: '/' });
          $.cookie('menu_user', null, {path: '/' });
          $.cookie('configure', null, {path: '/' });
      }
    }
    
    function loadMainMenu(obj, show){
        loadMenu(obj, obj.parent().siblings(), show);
    }

    function loadSubMenu(obj, show){
        loadMenu(obj, obj.siblings(), show);    
    }

    function loadMenu(obj, children, show){
        obj_id = obj.attr('id');
        is_visible = $.cookie(obj_id);
        if(is_visible == 'true'){
            children.show();
        }else if(is_visible == 'false'){
            children.hide();
        }else{
            if(show){
                children.show();
            }else{
                children.hide();
            }
        }
        addToCookie(obj, children);
    }

    function addToMainCookie(obj){
        addToCookie(obj, obj.parent().siblings())
    }

    function addToSubCookie(obj){
        addToCookie(obj, obj.siblings())
    }
    
    function addToCookie(obj, children){
        obj_id = obj.attr('id');
        is_visible = children.is(':visible');
        $.cookie(obj_id, is_visible, {path: '/' });
    }
    
    function tab_refresh(){
        set_tab_cookie($("#tabs-task").tabs('option', 'active'));
    }

    function set_tab_cookie(tab_idx){
        $.cookie('tab_index', tab_idx);
    }
    
    document.getElementByXPath = function(sValue) { 
        var a = this.evaluate(sValue, this, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null); 
        if (a.snapshotLength > 0) { return a.snapshotItem(0); } 
    };
        
    document.getElementsByXPath = function(sValue){ 
        var aResult = new Array();
        var a = this.evaluate(sValue, this, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for ( var i = 0 ; i < a.snapshotLength ; i++ ){
            aResult.push(a.snapshotItem(i));
        }
        return aResult;
    };    