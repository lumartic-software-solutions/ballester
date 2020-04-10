/** -*- coding: utf-8 -*-
 Odoo, Open Source Ballester Hr Attendance.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). 
*/
odoo.define('ballester_hr_attendance.custom', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var session = require('web.session');
var rpc = require('web.rpc');

var QWeb = core.qweb;
var _t = core._t;

rpc.query({
	model: 'res.users',
	method: 'search_read',
	args: [[['id', '=', session.uid]], ['menu_access_user','sidebar_visible']],
	}).done(function(res1) {
		var menu_access_user = res1[0]['menu_access_user']
		var sidebar_visible = res1[0]['sidebar_visible']
		if (menu_access_user == true){
			 $("#app-sidebar").css("display", "none");
			 $("#apps_icon").css("display", "none");
			 $(".o_sub_menu_content").css("display", "none");
			 $("#main-nav").css("display", "none");
              $("#app-sidebar").removeClass("toggle-sidebar");
		}else{
			$("#app-sidebar").css("display", "block");
			 $("#apps_icon").css("display", "block");
			 $("#main-nav").css("display", "block");
			 $(".o_sub_menu_content").css("display", "block");
             $("#app-sidebar").addClass("toggle-sidebar");
		}
	});

});

/**var session = require('web.session');
    var rpc = require('web.rpc');
    var id = session.uid;
    rpc.query({
                model: 'res.users',
                method: 'read',
                args: [[id], ['menu_access_user']],
            }).then(function(res) {
                var dbfield = res[0];
                var toggle = dbfield.menu_access_user;
                if (toggle === true) {
					$("#app-sidebar").css("display", "none");
                    $("#main-nav").css("display", "none");
			        $("#apps_icon").css("display", "none");
			       $(".o_sub_menu_content").css("display", "none");
                    $("#app-sidebar").removeClass("toggle-sidebar");
                } else {
					$("#app-sidebar").css("display", "block");
			      $("#apps_icon").css("display", "block");
			      $(".o_sub_menu_content").css("display", "block");
                    $("#app-sidebar").addClass("toggle-sidebar");
                };
    });
                             
});**/
    
