/**
 *  -*- coding: utf-8 -*-
 *  Odoo, Open Source  Itm Material Theme.
 *  License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).# 
 * 
 */
/* Copyright 2017 Openworx.
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl). */

odoo.define('itm_material.sidebar-toggle', function (require) {
    "use strict";
    
    var session = require('web.session');
    var rpc = require('web.rpc');
    var id = session.uid;
    rpc.query({
                model: 'res.users',
                method: 'read',
                args: [[id], ['sidebar_visible']],
            }).then(function(res) {
                var dbfield = res[0];
                var toggle = dbfield.sidebar_visible;
             
                if (toggle === true) {
		    $("#app-sidebar").css("display", "none");
                    $(".app-sidebar-panel").css("display", "none");
                    $("#app-sidebar").removeClass("toggle-sidebar");
			

                } 
		 else if (toggle === false) {
                    $("#app-sidebar").addClass("toggle-sidebar");
                };
    });
                             
});
    
