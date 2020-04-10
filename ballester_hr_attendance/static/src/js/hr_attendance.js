/** -*- coding: utf-8 -*-
 Odoo, Open Source Ballester Hr Attendance.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). 
*/
odoo.define('ballester_hr_attendance.hr_attendance', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var session = require('web.session');
var ajax = require('web.ajax');
var GreetingMessage = require('hr_attendance.greeting_message');
var Dialog = require('web.Dialog');
var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;


GreetingMessage.include({
	
	events: {
        "click .attendance_answers": function(event) {  this.set_attendance_status(event,this.attendance.id)},
//        "click .o_hr_attendance_button_no": function() {  this.set_attendance_status(this.attendance.id,status)},
	},
	check_stage: function() {
		var self =this;   
		var stage ='none';
	    if(this.attendance.check_out){ 
	    	stage = 'checkout' ; 
	    }else{  
	    	stage = 'checkin';
	    } 
	   return stage;
	},
	set_attendance_status: function(event,attendance) { 
	    var self =this;   
	    var stage = this.check_stage();
	    var answer = event.target.getAttribute("answer_id");
	    var question = event.target.getAttribute("question_id");
	    if (answer && question) {
		    this._rpc({
		        model: 'hr.attendance',
		        method
		        : 'set_attendance_status',
		        args: [[],attendance,stage,answer,question],
		    })
		    .then(function (result) {
		        if (result.success) {
//		        	if (status == true){
//		        		self.do_action(self.next_action, {clear_breadcrumbs: true});
//		        	}else{
//		        		new Dialog(self, {
//		                    title: _t('Confirmation Dialog'),
//		                    size: 'medium',
//		                    $content: $('<div>', {
//		                        html: _t("Please go to meet HR head!"),
//		                    }),
//		                    buttons: [
//		                        {text: _t('Close'), close: true, classes: 'btn-primary'},
//		                        {text: _t('Ok'), click: function () {
//		                        	self.do_action(self.next_action, {clear_breadcrumbs: true});
//		                        }
//		                    },
//		                ]}).open();
//		        	}
		        	if (result.execution_type == 'none'){
		        		var validate = "[question_id="+question+"]"
			   	        $(validate).css("display", "none");
		        	}else if (result.execution_type == 'continue'){
		        		self.do_action(self.next_action, {clear_breadcrumbs: true});
		        	}else{
		        		new Dialog(self, {
	                    title: _t('Confirmation Dialog'),
	                    size: 'medium',
	                    $content: $('<div>', {
	                        html: _t("Please go to meet HR head!"),
	                    }),
	                    buttons: [
//	                        {text: _t('Close'), close: true, classes: 'btn-primary'},
	                        {text: _t('Close'), click: function () {
	                        	this._rpc({
	                		        model: 'hr.attendance',
	                		        method
	                		        : 'delete_answer',
	                		        args: [[],result.user_input_line_id],
	                		    });
	                          },close: true, classes: 'btn-primary'},
	                        {text: _t('Ok'), click: function () {
	                        	this._rpc({
	                		        model: 'hr.attendance',
	                		        method
	                		        : 'send_notifications_mail',
	                		        args: [[],result.user_input_line_id,attendance],
	                		    })
	                		    .then(function (result) {
	                		        if (result.success) {
	                		        	self.do_action(self.next_action, {clear_breadcrumbs: true});
	                		        }else{
	                		        	 self.do_warn(result.warning);
	                		        }
	                		    });
	                        }
	                    },
	                ]}).open();
	        	}
		        	
		        	
		        } else if (result.warning) {
		            self.do_warn(result.warning);
		        }
		    });
	    }
    },
    
    set_information: function(){
    	var self =this;   
    	var stage = this.check_stage();
        if (this.attendance){
        	this._rpc({
    	        model: 'hr.attendance',
    	        method: 'set_information',
    	        args: [[],this.attendance.id,stage],
    	    })
    	    .then(function (result) {
    	        if (result.success) {
    	        	$('.attendance_description').append(result.description);
    	        	$('.attendance_description').addClass('set_description');
    	        	if (result.information_details.length > 0){
    	        		var set_data = ""
    	        		for (var i = 0; i < result.information_details.length; i++) { 
    	        			set_data += "<span class='warning_msg' question_id='" +result.information_details[i]['question_id']+"'>"+result.information_details[i]['question']+ "</span><br/>"
    	        			for (var j = 0; j < result.information_details[i]['answer_list'].length; j++) {
    	        				set_data += "<button t-if='widget.attendance' class='attendance_answers custom_btn btn btn-primary btn-sm'"+
    	        				"question_id='" +result.information_details[i]['question_id']+"'"+
    	        				"answer_id='" +result.information_details[i]['answer_list'][j]['answer_id'] + "'>" +
    	        				result.information_details[i]['answer_list'][j]['answer'] +"</button>"
    	        			}
    	        			set_data +='<br/>'
    	        		}
    	        		if (stage == 'checkin'){
	    	        		$('.attendance_entry_question').append(set_data);
	    	        	}else if (stage == 'checkout'){
	    	        		$('.attendance_exit_question').append(set_data);
	    	        	}else{
	    	        		self.do_warn('No Found Attendance !');
	    	        	}
	    	        }else{
		        		self.do_warn('No Found Instruction Information !');
		        	}
    	        } else if (result.warning) {
    	            self.do_warn(result.warning);
    	        }
    	    });
        }
    },
    
    welcome_message: function() {
        var self = this;
        var now = new Date((new Date(this.attendance.check_in)).valueOf() - (new Date()).getTimezoneOffset()*60*1000);
        this.return_to_main_menu = setTimeout( function() {  }, 5000);
//        self.do_action(self.next_action, {clear_breadcrumbs: true});
        this.set_information();
        if (now.getHours() < 5) {
            this.$('.o_hr_attendance_message_message').append(_t("Good night"));
        } else if (now.getHours() < 12) {
            if (now.getHours() < 8 && Math.random() < 0.3) {
                if (Math.random() < 0.75) {
                    this.$('.o_hr_attendance_message_message').append(_t("The early bird catches the worm"));
                } else {
                    this.$('.o_hr_attendance_message_message').append(_t("First come, first served"));
                }
            } else {
                this.$('.o_hr_attendance_message_message').append(_t("Good morning"));
            }
        } else if (now.getHours() < 17){
            this.$('.o_hr_attendance_message_message').append(_t("Good afternoon"));
        } else if (now.getHours() < 23){
            this.$('.o_hr_attendance_message_message').append(_t("Good evening"));
        } else {
            this.$('.o_hr_attendance_message_message').append(_t("Good night"));
        }
        if(this.previous_attendance_change_date){
            var last_check_out_date = new Date((new Date(this.previous_attendance_change_date)).valueOf() - (new Date()).getTimezoneOffset()*60*1000);
            if(now.valueOf() - last_check_out_date.valueOf() > 1000*60*60*24*7){
                this.$('.o_hr_attendance_random_message').html(_t("Glad to have you back, it's been a while!"));
            } else {
                if(Math.random() < 0.02){
                    this.$('.o_hr_attendance_random_message').html(_t("If a job is worth doing, it is worth doing well!"));
                }
            }
        }
    },
    
    farewell_message: function() {
        var self = this;
        var now = new Date((new Date(this.attendance.check_out)).valueOf() - (new Date()).getTimezoneOffset()*60*1000);
        this.return_to_main_menu = setTimeout( function() {  }, 5000);
//        self.do_action(self.next_action, {clear_breadcrumbs: true});
        this.set_information();
        if(this.previous_attendance_change_date){
            var last_check_in_date = new Date((new Date(this.previous_attendance_change_date)).valueOf() - (new Date()).getTimezoneOffset()*60*1000);
            if(now.valueOf() - last_check_in_date.valueOf() > 1000*60*60*12){
                this.$('.o_hr_attendance_warning_message').append(_t("Warning! Last check in was over 12 hours ago.<br/>If this isn't right, please contact Human Resources."));
                clearTimeout(this.return_to_main_menu);
                this.activeBarcode = false;
            } else if(now.valueOf() - last_check_in_date.valueOf() > 1000*60*60*8){
                this.$('.o_hr_attendance_random_message').html(_t("Another good day's work! See you soon!"));
            }
        }

        if (now.getHours() < 12) {
            this.$('.o_hr_attendance_message_message').append(_t("Have a good day!"));
        } else if (now.getHours() < 14) {
            this.$('.o_hr_attendance_message_message').append(_t("Have a nice lunch!"));
            if (Math.random() < 0.05) {
                this.$('.o_hr_attendance_random_message').html(_t("Eat breakfast as a king, lunch as a merchant and supper as a beggar"));
            } else if (Math.random() < 0.06) {
                this.$('.o_hr_attendance_random_message').html(_t("An apple a day keeps the doctor away"));
            }
        } else if (now.getHours() < 17) {
            this.$('.o_hr_attendance_message_message').append(_t("Have a good afternoon"));
        } else {
            if (now.getHours() < 18 && Math.random() < 0.2) {
                this.$('.o_hr_attendance_message_message').append(_t("Early to bed and early to rise, makes a man healthy, wealthy and wise"));
            } else {
                this.$('.o_hr_attendance_message_message').append(_t("Have a good evening"));
            }
        }
    },

});

});
