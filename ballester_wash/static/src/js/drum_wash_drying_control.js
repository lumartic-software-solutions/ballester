﻿// -*- coding: utf-8 -*-
// Odoo, Open Source Member Barcode Scanner.
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

odoo.define('ballester_wash.drum_wash_drying_control', function (require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var Session1 = require('web.Session');
var Widget = require('web.Widget');
var Session = require('web.session');
var mixins = require('web.mixins');
var Notification = require('web.notification').Notification;
var NotificationManager = require('web.notification').NotificationManager;

var QWeb = core.qweb;
var _t = core._t;


var JobQueue = function(){
    var queue = [];
    var running = false;
    var scheduled_end_time = 0;
    var end_of_queue = (new $.Deferred()).resolve();
    var stoprepeat = false;

    var run = function(){
        if(end_of_queue.state() === 'resolved'){
            end_of_queue =  new $.Deferred();
        }
        if(queue.length > 0){
            running = true;
            var job = queue[0];
            if(!job.opts.repeat || stoprepeat){
                queue.shift();
                stoprepeat = false;
            }

            // the time scheduled for this job
            scheduled_end_time = (new Date()).getTime() + (job.opts.duration || 0);

            // we run the job and put in def when it finishes
            var def = job.fun() || (new $.Deferred()).resolve();

            // we don't care if a job fails ...
            def.always(function(){
                // we run the next job after the scheduled_end_time, even if it finishes before
                setTimeout(function(){
                    run();
                }, Math.max(0, scheduled_end_time - (new Date()).getTime()) );
            });
        }else{
            running = false;
            scheduled_end_time = 0;
            end_of_queue.resolve();
        }
    };

    // adds a job to the schedule.
    // opts : {
    //    duration    : the job is guaranteed to finish no quicker than this (milisec)
    //    repeat      : if true, the job will be endlessly repeated
    //    important   : if true, the scheduled job cannot be canceled by a queue.clear()
    // }
    this.schedule  = function(fun, opts){
        queue.push({fun:fun, opts:opts || {}});
        if(!running){
            run();
        }
    };

    // remove all jobs from the schedule (except the ones marked as important)
    this.clear = function(){
        queue = _.filter(queue,function(job){return job.opts.important === true;});
    };

    // end the repetition of the current job
    this.stoprepeat = function(){
        stoprepeat = true;
    };

    // returns a deferred that resolves when all scheduled
    // jobs have been run.
    // ( jobs added after the call to this method are considered as well )
    this.finished = function(){
        return end_of_queue;
    };

};


var ProxyDevice1  = core.Class.extend(mixins.PropertiesMixin,{
    init: function(parent,options){
        mixins.PropertiesMixin.init.call(this);
        var self = this;
        options = options || {};
        this.pos = parent;
        this.printer_ip = self.pos.printer_ip ;
        this.printer_port = self.pos.printer_port ;

        options.force_ip = this.pos.printer_ip;
        options.port = this.pos.printer_port;
        this.weighing = false;
        this.debug_weight = 0;
        this.use_debug_weight = false;

        this.paying = false;
        this.default_payment_status = {
            status: 'waiting',
            message: '',
            payment_method: undefined,
            receipt_client: undefined,
            receipt_shop:   undefined,
        };
        this.custom_payment_status = this.default_payment_status;

        this.receipt_queue = [];

        this.notifications = {};
        this.bypass_proxy = false;

        this.host       = '';
        this.keptalive  = false;

        this.set('status',{});

        this.set_connection_status('disconnected');
        this.autoconnect(options);
//        this.on('change:status',this,function(eh,status){
//            status = status.newValue;
//            if(status.status === 'connected'){
//                self.print_receipt();
//            }
//        });

        window.hw_proxy = this;
    },
    set_connection_status: function(status,drivers){
        var oldstatus = this.get('status');
        var newstatus = {};
        newstatus.status = status;
        newstatus.drivers = status === 'disconnected' ? {} : oldstatus.drivers;
        newstatus.drivers = drivers ? drivers : newstatus.drivers;
        this.set('status',newstatus);
    },
    disconnect: function(){
        if(this.get('status').status !== 'disconnected'){
            this.connection.destroy();
            this.set_connection_status('disconnected');
        }
    },

    // connects to the specified url
    connect: function(url){
        var self = this;

        url = 'http://' + self.printer_ip + ":" + self.printer_port;

        this.connection = new Session1(undefined,url, { use_cors: true});
        this.host   = url;
        this.set_connection_status('connecting',{});

        return this.message('handshake').then(function(response){
                if(response){
                    self.set_connection_status('connected');
                    localStorage.hw_proxy_url = url;
                    self.keepalive();
                }else{
                    self.set_connection_status('disconnected');
                }
            },function(){
                self.set_connection_status('disconnected');
            });
    },

    // find a proxy and connects to it. for options see find_proxy
    //   - force_ip : only try to connect to the specified ip.
    //   - port: what port to listen to (default 8069)
    //   - progress(fac) : callback for search progress ( fac in [0,1] )
    autoconnect: function(options){
        var self = this;
        this.set_connection_status('connecting',{});
       // options.force_ip = '192.168.1.102';
        options.force_ip = self.printer_ip;
        var found_url = new $.Deferred();
        var success = new $.Deferred();
        if ( options.force_ip ){
            // if the ip is forced by server config, bailout on fail
            found_url = this.try_hard_to_connect(options.force_ip, options);
        }else if( localStorage.hw_proxy_url ){
            // try harder when we remember a good proxy url
            found_url = this.try_hard_to_connect(localStorage.hw_proxy_url, options)
                .then(null,function(){
                    return self.find_proxy(options);
                });
        }else{
            // just find something quick
            found_url = this.find_proxy(options);
        }
        success = found_url.then(function(url){
                return self.connect(url);
            });
        
        success.fail(function(){
            self.set_connection_status('disconnected');
        });

        return success;
    },

    // starts a loop that updates the connection status
    keepalive: function(){
        var self = this;

        function status(){
            self.connection.rpc('/hw_proxy/status_json',{},{timeout:2500})
                .then(function(driver_status){
                    self.set_connection_status('connected',driver_status);
                },function(){
                    if(self.get('status').status !== 'connecting'){
                        self.set_connection_status('disconnected');
                    }
                }).always(function(){
                    setTimeout(status,5000);
                });
        }

        if(!this.keptalive){
            this.keptalive = true;
            status();
        }
    },

    message : function(name,params){
        var callbacks = this.notifications[name] || [];
        for(var i = 0; i < callbacks.length; i++){
            callbacks[i](params);
        }
        if(this.get('status').status !== 'disconnected'){
            return this.connection.rpc('/hw_proxy/' + name, params || {});
        }else{
            return (new $.Deferred()).reject();
        }
    },

    // try several time to connect to a known proxy url
    try_hard_to_connect: function(url,options){
        options   = options || {};
        var port  = ':' + (options.port || '8069');
        this.set_connection_status('connecting');

        if(url.indexOf('//') < 0){
            url = 'http://'+url;
        }

        if(url.indexOf(':',5) < 0){
            url = url+port;
        }
        // try real hard to connect to url, with a 1sec timeout and up to 'retries' retries
        function try_real_hard_to_connect(url, retries, done){

            done = done || new $.Deferred();

            $.ajax({
                url: url + '/hw_proxy/hello',
                method: 'GET',
                timeout: 1000,
            })
            .done(function(){
                done.resolve(url);
            })
            .fail(function(){
                if(retries > 0){
                    try_real_hard_to_connect(url,retries-1,done);
                }else{
                    done.reject();
                }
            });
            return done;
        }

        return try_real_hard_to_connect(url,3);
    },

    // returns as a deferred a valid host url that can be used as proxy.
    // options:
    //   - port: what port to listen to (default 8069)
    //   - progress(fac) : callback for search progress ( fac in [0,1] )
    find_proxy: function(options){
        options = options || {};
        var self  = this;
        var port  = ':' + (options.port || '8069');
        var urls  = [];
        var found = false;
        var parallel = 8;
        var done = new $.Deferred(); // will be resolved with the proxies valid urls
        var threads  = [];
        var progress = 0;

        urls.push('http://localhost'+port);
        // urls.push('http://192.168.191.78'+port);
        for(var i = 0; i < 256; i++){
            urls.push('http://192.168.0.'+i+port);
            urls.push('http://192.168.1.'+i+port);
            urls.push('http://10.0.0.'+i+port);
        }

        var prog_inc = 1/urls.length;

        function update_progress(){
            progress = found ? 1 : progress + prog_inc;
            if(options.progress){
                options.progress(progress);
            }
        }

        function thread(done){
            var url = urls.shift();

            done = done || new $.Deferred();

            if( !url || found || !self.searching_for_proxy ){
                done.resolve();
                return done;
            }

            $.ajax({
                    url: url + '/hw_proxy/hello',
                    method: 'GET',
                    timeout: 400,
                }).done(function(){
                    found = true;
                    update_progress();
                    done.resolve(url);
                })
                .fail(function(){
                    update_progress();
                    thread(done);
                });

            return done;
        }

        this.searching_for_proxy = true;

        var len  = Math.min(parallel,urls.length);
        for(i = 0; i < len; i++){
            threads.push(thread());
        }

        $.when.apply($,threads).then(function(){
            var urls = [];
            for(var i = 0; i < arguments.length; i++){
                if(arguments[i]){
                    urls.push(arguments[i]);
                }
            }
            done.resolve(urls[0]);
        });

        return done;
    },

    stop_searching: function(){
        this.searching_for_proxy = false;
        this.set_connection_status('disconnected');
    },

    // this allows the client to be notified when a proxy call is made. The notification
    // callback will be executed with the same arguments as the proxy call
    add_notification: function(name, callback){
        if(!this.notifications[name]){
            this.notifications[name] = [];
        }
        this.notifications[name].push(callback);
    },

    // returns the weight on the scale.
    scale_read: function(){
        var self = this;
        var ret = new $.Deferred();
        if (self.use_debug_weight) {
            return (new $.Deferred()).resolve({weight:this.debug_weight, unit:'Kg', info:'ok'});
        }
        this.message('scale_read',{})
            .then(function(weight){
                ret.resolve(weight);
            }, function(){ //failed to read weight
                ret.resolve({weight:0.0, unit:'Kg', info:'ok'});
            });
        return ret;
    },

    // sets a custom weight, ignoring the proxy returned value.
    debug_set_weight: function(kg){
        this.use_debug_weight = true;
        this.debug_weight = kg;
    },

    // resets the custom weight and re-enable listening to the proxy for weight values
    debug_reset_weight: function(){
        this.use_debug_weight = false;
        this.debug_weight = 0;
    },

    // ask for the cashbox (the physical box where you store the cash) to be opened
    open_cashbox: function(){
        return this.message('open_cashbox');
    },

    /*
     * ask the printer to print a receipt
     */
    print_receipt: function(receipt){
    	var self = this;
        if(receipt){
            this.receipt_queue.push(receipt);
        }
        function send_printing_job(){
            if (self.receipt_queue.length > 0){
                var r = self.receipt_queue.shift();
                self.message('print_xml_receipt',{ receipt: r },{ timeout: 5000 })
                    .then(function(){
                        send_printing_job();
                    },function(error){
                        if (error) {
                            alert(_t('Printing Error: ') + error.data.message);
                            return;
                        }
                        self.receipt_queue.unshift(r);
                    });
            }
        }
        send_printing_job();
    },

    // asks the proxy to log some information, as with the debug.log you can provide several arguments.
    log: function(){
        return this.message('log',{'arguments': _.toArray(arguments)});
    },

});


//Success Notification with thumbs-up icon
var Success = Notification.extend({
    template: 'member_barcode_success'
});

var NotificationSuccess = NotificationManager.extend({
    success: function(title, text, sticky) {
        return this.display(new Success(this, title, text, sticky));
    }
});


var WashDrumMode = Widget.extend({
	 events: {
	       // "click .o_wash_container_button": function(){ this.do_action('member_barcode_scanner.member_attendance_action_kanban'); },
	       // "click .continue_drum_button": function(){Session.employee_id = this.employee_id; Session.employee = this.employee; Session.employee_image_url = this.employee_image_url ;this.do_action('ballester_wash.action_ballester_drum_wash_display_screen'); },
	        'keypress #wash_drum' : 'on_manual_scan',
	    },
	on_manual_scan: function(e) {
	        if (e.which === 13) { // Enter
	            var value = $(e.currentTarget).val().trim();
	            if(value) {
	                this.on_barcode_scanned(value);
	                $(e.currentTarget).val('');
	            } else {
	                this.do_warn(_t('Error'), _t('Invalid user input'));
	            }
	        }
	    },
    start: function () {
        var self = this;
//        core.bus.on('barcode_scanned', this, this._onBarcodeScanned);
        self.session = Session;
        this.chrome = parent;
        this.gui    = undefined;
        var def = this._rpc({
                model: 'res.company',
                method: 'search_read',
                args: [[['id', '=', this.session.company_id]], ['name', 'ip_address', 'port', 'receipt_to_printer']],
            })
            .then(function (companies){
            	Session.company_name = self.company_name = companies[0].name;
            	Session.company_image_url = self.company_image_url = self.session.url('/web/image', {model: 'res.company', id: self.session.company_id, field: 'logo',});
                self.$el.html(QWeb.render("DrumWash", {widget: self}));
                Session.printer_ip =  self.printer_ip = companies[0].ip_address;
                Session.printer_port = self.printer_port = companies[0].port;
                Session.receipt_to_printer = self.receipt_to_printer = companies[0].receipt_to_printer;
                if (self.receipt_to_printer){
                	Session.proxy_device = self.proxy_device = new ProxyDevice1(self);
                }
                self.start_clock();
            });
        // Make a RPC call every day to keep the session alive
        self._interval = window.setInterval(this._callServer.bind(this), (60*60*1000*24));
        return $.when(def, this._super.apply(this, arguments));
    },
    on_barcode_scanned: function(barcode) {
      var self = this;
      Session.rpc('/member_barcode_scanner/register_attendee', {
           barcode: barcode,
      }).done(function(result) {
          if (result.success) {
             // self.notification_manager.success(result.success);
//              self.do_warn(_("Success"),_("Thanks for coming,Please collect your ticket."));
//              if (self.receipt_to_printer){
//                  var report = QWeb.render('Memberticketreceipt',{'event': result});
//                  return self.proxy_device.print_receipt(report);
//              }
//              else{
//                  var action = {
//                      'type': 'ir.actions.report.xml',
//                      'report_type': 'qweb-pdf',
//                      'report_name': 'member_barcode_scanner.print_ticket_report_view',
//                      'report_file': 'member_barcode_scanner.print_ticket_report_view',
//                      'data': {
//                          'doc_ids': [result.attendee_id],
//                          'doc_model': 'event.registration',
//                      },
//                      'context': {
//                          'active_id': result.attendee_id,
//                          'active_ids': [result.attendee_id],
//                          'active_model':'event.registration',
//                      },
//                      'display_name': 'report title',
//                  };
//                  return self.do_action(action);
        	      Session.attendance_state=  self.attendance_state = result.attendance_state
            	  Session.employee_id=  self.employee_id = result.employee_id
            	  Session.employee = self.employee = result.employee
            	  Session.employee_image_url = self.employee_image_url = result.employee_image_url
            	  self.$el.html(QWeb.render("DrumWashWelcome", {widget: self}));
		if (self.attendance_state == 'checked_in'){
			setTimeout(function () {
				self.do_action('ballester_wash.action_ballester_drum_wash_display_screen');
			    }, 2000);
		}

		else {
		setTimeout(function () {
				self.do_action('ballester_wash.action_ballester_drum_drying_control_screen');
			    }, 2000);

			
		}
//              }
          }else if (result.warning) {
              self.do_warn(_("Warning"), result.warning);

          }
      });
  },

  start_clock: function() {
      this.clock_start = setInterval(function() {this.$(".o_hr_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'}));}, 500);
      // First clock refresh before interval to avoid delay
      this.$(".o_hr_attendance_clock").text(new Date().toLocaleTimeString(navigator.language, {hour: '2-digit', minute:'2-digit'}));
  },

  destroy: function () {
      clearInterval(this.clock_start);
      this._super.apply(this, arguments);
  },

    _callServer: function () {
        // Make a call to the database to avoid the auto close of the session
        return ajax.rpc("/web/webclient/version_info", {});
    },

});

core.action_registry.add('ballester_drum_control_screen_act', WashDrumMode);


return {
    WashDrumMode: WashDrumMode,
    Success: Success,
    NotificationSuccess: NotificationSuccess,
    JobQueue: JobQueue,
    ProxyDevice1: ProxyDevice1,
};

});
