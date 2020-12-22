/** -*- coding: utf-8 -*-
 Odoo, Open Source Ballester Screen.
 License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
*/
odoo.define('ballester_wash.container_drying_control_display', function (require) {
"use strict";

var core = require('web.core');
var Widget = require('web.Widget');
var session = require('web.session');
var ajax = require('web.ajax');
var ActionManager = require('web.ActionManager');
var view_registry = require('web.view_registry');
var QWeb = core.qweb;

var _t = core._t;
var _lt = core._lt;


var ContainerDryingDisplayScreen = Widget.extend({
	events: _.extend({}, Widget.prototype.events, {
//		'click .continue_button': 'continue_button',
		// ===========  main screen ===========
		'click .main': 'main',
		//'click .product_wash' :'product_wash',
		'click .my_profile': 'action_my_profile',
		// ===========  exit Popup ===========
		'click .repair_order_backscreen': 'repair_order_backscreen',
		'click .confirm_exit_popup': 'confirm_exit_popup',
		// ===========  main 1 button ===========
		'click .entry_of_products': 'entry_of_products',
		// ===========  main 2 button ===========
               'click .output_of_products': 'output_of_products',
		// ===========  main 3 button ===========
		'click .warehouse': 'warehouse',
		// Add an item button
		'click .display_container_detail': 'display_container_detail',
		// Validate Barcode  button
		'click .validate_barcode': 'validate_barcode',
		'click .container_compliance_screen':'container_compliance_screen',
		'click .repairorder_button':'repairorder_button',
		'change #barcode_number': 'barcode',
	        'change .products': 'products',
		// lot details wizard
		'click .lot_details_wizard': 'lot_details_wizard',
		// ===========  main 4 button ===========
// Create   wash
		'click .dryingwash_button': 'dryingwash_button',
		'click .destructionwash_button' : 'destructionwash_button',
		'click .dryingendwash_button' :'dryingendwash_button',
			
//onchange wash product
		'click .onchange_product' :'onchange_product',
		'click  .compliance_wash_order': 'compliance_wash_order',
		'click .main_container_screen': 'main_container_screen',
		'click .compliance_value':'compliance_value',
		//'click .start_repair_button':'start_repair_button',
		'click .stoprepairorder_button': 'stoprepairorder_button',
		'click .startrepairorder_button' :'startrepairorder_button',
		'click .repairorder_button_screen':'repairorder_button_screen',
		'click .repair_compliance_button' : 'repair_compliance_button',
		'click .containertransfer_button':'containertransfer_button',
		'click .add_part_button':'add_part_button',
		'click .view_repair_order_button':'view_repair_order_button',
		'click .add_repair_part':'add_repair_part',
		'click .backto_wash_button':'backto_wash_button'
,		'click .compliance_submit':'compliance_submit',
		'click .save_repair_parts':'save_repair_parts',
		'click .edit_repair_parts':'edit_repair_parts',
		//'change #product' : 'ProductOnChangeEvent',
		'click .btndelete' :'btndelete',
		'click .backto_repair':'backto_repair',
		//'click .create_emptying_wash_order' : 'create_emptying_wash_order',
	}),
	init: function(parent, context) {
        this._super(parent, context);
        var operation_data = [];
        var self = this;
        if (context.tag == 'ballester_container_drying_display_screen_act') {
            self._rpc({
                model: 'operation.wash.dashboard',
                method: 'get_operation_info',
            }, []).then(function(result){

            	self.operation_data = result[0]
                self.product_list = self.operation_data.product_list
                self.barcode_list = self.operation_data.barcode_list
		self.repair_location_list = self.operation_data.repair_location_list
                self.set_unused_barcode_list = self.operation_data.set_unused_barcode_list
                self.unused_barcode_list = self.operation_data.unused_barcode_list
                self.employee_id = session.employee_id
                self.employee = session.employee
		        self.recycled_product = self.operation_data.recycled_product
                self.employee_image_url = session.employee_image_url
		console.log("IIIIIIIIIIIIIIIIII",self )
            }).done(function(){
            	self.render();
                self.href = window.location.href;

            });
        }
    },
    willStart: function() {
        return $.when(ajax.loadLibs(this), this._super());
    },
    render: function () {
	   var super_render = this._super;
       var self = this;
      console.log(">>dxddddd>>>>>>>>>>>>>>>>>>>>>>>>>>>")

       return  self.$el.html(QWeb.render("ContainerDryingDisplay", {widget: self}));
    },
    reload: function () {
        window.location.href = this.href;
    },
    main: function (event) {
        var self = this;
      console.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        event.stopPropagation();
        event.preventDefault();
        self.repair_button = false
	$('.modal-backdrop').remove();
	self.transfer_button = false
	return  self.do_action('ballester_wash.action_ballester_container_drying_display_screen');
    },
    confirm_exit_popup: function (event) {
        var self = this;
        event.stopPropagation();
	$('.modal-backdrop').remove();
        event.preventDefault();
        return  self.do_action('ballester_wash.action_ballester_container_drying_control_screen');
    },
    entry_of_products: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return  self.$el.html(QWeb.render("EntryOfProductsButton", {widget: self}));
    },
    output_of_products: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return  self.$el.html(QWeb.render("OutputOfProductsButton", {widget: self}));
    },
    warehouse: function(event){
        var self = this;
        event.stopPropagation();
        event.preventDefault();
        return  self.$el.html(QWeb.render("WarehouseButton", {widget: self}));
    },





    generate_barcode: function(event){
    	 var self = this;
         event.stopPropagation();
         event.preventDefault();
         self._rpc({
             model: 'operation.wash.dashboard',
             method: 'get_operation_info',
         }, []).then(function(result){
            self.operation_data = result[0]
            self.product_list = self.operation_data.product_list
//            self.ler_list = self.operation_data.ler_list
            self.barcode_list = self.operation_data.barcode_list
            self.set_unused_barcode_list = self.operation_data.set_unused_barcode_list
            self.unused_barcode_list = self.operation_data.unused_barcode_list
            self.employee_id = session.employee_id
            self.employee = session.employee
            self.employee_image_url = session.employee_image_url
         }).done(function(){
        	 self.href = window.location.href;
        	 return  self.$el.html(QWeb.render("GenerateBarcodeButton", {widget: self}));
         });
    },
//  selectign barcode from wash product

    barcode: function(event) {
      	var self = this;
	   	event.stopPropagation();
	   	event.preventDefault();
	   	var product_data = [];
		var ctx = {};
                ctx['display_barcode_details']= "True";
		var emp = self.employee_id 
		$('.modal-backdrop').remove();
	   	var number_of_barcode = $("#barcode_number").val();
	   	if (number_of_barcode != ''){
			   	//	 generating barcode
		        self._rpc({
		                model: 'operation.wash.dashboard',
		                method: 'search_barcode',
				context : ctx,
		                args: [[],number_of_barcode,emp],		            })
			
                              .then(function(result) {
				if (result.success) {
					$('#barcode_number').attr("disabled", true) 
					if (result.wash_order_data[0]['state'] != 'repair_create') {

						$("#table_detail").css("display", "none");
				      $("#table_detail").css("display", "none");
					if (result.wash_order_data){
				$("#image_container").css("display", "inline");
				if (result.product_img_url != undefined ){
				document.getElementById('image_container')
					    .setAttribute(
						'src', 'data:image/png;base64,' + result.product_img_url
					    ); }
					$("#table_detail").css("display", "inline");
                                       console.log(">>>>>>>>>result.wash_order_data>>>>>>>>>",result.wash_order_data )
					
					$("#cancel_wash_order_button").css("display", "inline");
                                         if (result.wash_order_data[0]['state'] == 'end_wash') {
							
							$("#drying_wash_order").css("display", "inline");
							$("#drying_end_wash_order").css("display", "none");
							$("#backto_wash_order").css("display", "none");
							$("#destruction_wash_order").css("display", "none");
					}
					 else if(result.wash_order_data[0]['state'] == 'start_drying') {
							self.stop_drying = true
				                       
							$("#drying_end_wash_order").css("display", "inline");
							$("#destruction_wash_order").css("display", "inline");
							$("#backto_wash_order").css("display", "none");
							$("#drying_wash_order").css("display", "none");
					}
					 else if(result.wash_order_data[0]['state'] == 'stop_drying') {
							self.check_compliance = true
							$("#compliance_wash_order").css("display", "inline");
							$("#backto_wash_order").css("display", "inline");
							$("#drying_end_wash_order").css("display", "none");
					}
					 else if(result.wash_order_data[0]['state'] == 'quality_control') {
                                                        console.log("ff----------------")
							self.quality_control = true
							$("#quality_control").css("display", "inline");
					}
					
					$( "#table_detail").after(

						"<tr id='tr_detail'><td style='width: 250px;font-size:20px; color:blue'>No of Washing Order: </td><td style='font-size:20px; color:blue'>" + result.wash_order_data[0]['order_number'] + "</td></tr><tr id='tr1_detail'> <td style='font-size:20px; color:blue'>  Type Of Order:</td><td style='font-size:20px; color:blue'>"+ result.wash_order_data[0]['type_of_order']+
					  "\</td></tr> <tr id='tr2_detail'><td style='font-size:20px; color:blue'> Dangerous characteristics: </td><td style='font-size:20px; color:blue'>" + result.wash_order_data[0]['dangerous_characteristics'] + "</td></tr> <tr id='tr3_detail'> <td style='font-size:20px; color:blue'>  Variants:</td><td style='font-size:20px; color:blue'>" + result.wash_order_data[0]['variants'] +  "</td></tr> <tr id='tr4_detail'> <td style='font-size:25px; color:blue'>  <b>State:</b></td><td style='font-size:25px; color:blue'><b>" +  result.wash_order_data[0]['state'] + "</b></td></tr> <tr id='tr5_detail'> <td style='font-size:20px; color:blue'>   LER: </td><td style='font-size:20px; color:blue'>" +  result.wash_order_data[0]['ler'] +  "</td></tr> <tr id='tr6_detail'> <td style='font-size:20px; color:blue'>  UN code: </td><td style='font-size:20px; color:blue'>" 
+ result.wash_order_data[0]['un_code'] + "</td></tr> <tr id='tr7_detail'> <td style='font-size:20px; color:blue'>  Recycled Product: </td><td style='font-size:20px; color:blue'>" 
+ result.wash_order_data[0]['recycled_product'] +"</td></tr>" );
                                      
					}
					}
	
	if (result.wash_order_data[0]['state'] == 'repair_create') {
				console.log("ssssssssssssssssssssssssssssssssss",self)
				$("#table_detail").css("display", "none");
				      $("#table_detail").css("display", "none");
					if (result.wash_order_data){
				$("#image_container").css("display", "inline");
				if (result.product_img_url != undefined ){
				document.getElementById('image_container')
					    .setAttribute(
						'src', 'data:image/png;base64,' + result.product_img_url
					    ); }
					$("#table_detail").css("display", "inline");
                                       console.log(">>>>>>>>>result.wash_order_data>>>>>>>>>",result.wash_order_data )
					$('.modal-backdrop').remove();
					$("#cancel_wash_order_button").css("display", "none");
					$("#drying_wash_order").css("display", "none");
					$("#backto_wash_order").css("display", "none");
					$("#drying_end_wash_order").css("display", "none");
					$("#destruction_wash_order").css("display", "none");
					$("#compliance_wash_order").css("display", "none");
					$("#view_repair_order").css("display", "inline");
					$( "#table_detail").after(

						"<tr id='tr_detail'><td style='width: 250px;font-size:20px; color:blue'>No of Washing Order: </td><td style='font-size:20px; color:blue'>" + result.wash_order_data[0]['order_number'] + "</td></tr><tr id='tr1_detail'> <td style='font-size:20px; color:blue'>  Type Of Order:</td><td style='font-size:20px; color:blue'>"+ result.wash_order_data[0]['type_of_order']+
					  "\</td></tr> <tr id='tr2_detail'><td style='font-size:20px; color:blue'> Dangerous characteristics: </td><td style='font-size:20px; color:blue'>" + result.wash_order_data[0]['dangerous_characteristics'] + "</td></tr> <tr id='tr3_detail'> <td style='font-size:20px; color:blue'>  Variants:</td><td style='font-size:20px; color:blue'>" + result.wash_order_data[0]['variants'] +  "</td></tr> <tr id='tr4_detail'> <td style='font-size:20px; color:blue'>  <b>State:</b></td><td style='font-size:20px; color:blue'>" +  result.wash_order_data[0]['state'] + "</td></tr> <tr id='tr5_detail'> <td style='font-size:20px; color:blue'>   LER: </td><td style='font-size:20px; color:blue'>" +  result.wash_order_data[0]['ler'] +  "</td></tr> <tr id='tr6_detail'> <td style='font-size:20px; color:blue'>  UN code: </td><td style='font-size:20px; color:blue'>" 
+ result.wash_order_data[0]['un_code'] + "</td></tr> <tr id='tr7_detail'> <td style='font-size:20px; color:blue'>  Recycled Product: </td><td style='font-size:20px; color:blue'>" 
+ result.wash_order_data[0]['recycled_product'] +"</td></tr>" );
                                      
					}
					}

				

					}
				if (result.warning) {
                                        self.do_warn(_("Warning"),_("'There is no wash order for this barcode! \n Please Enter Valid Number !'"));

					}
					

			} );


	   		 }
		else{
	    	   self.do_warn(_("Warning"),_("Please Enter the Number First!"));
	       }
	  },




dryingwash_button: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	var number_of_barcode = $("#barcode_number").val(); 
	var ctx = {};
	$('.modal-backdrop').remove();
	ctx['drying_wash_order']= "True";
	var emp = self.employee_id 
     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'search_barcode',
		context : ctx,
                args: [[],number_of_barcode,emp],
               }) 
		.then(function(result){
		if (result.success) {
				$('.modal-backdrop').remove();
				self.continue_button = true
                                self.stop_drying = true
				self.destruction = true
				self.img_url = result.wash_order_data[0]['img_url']
				    self.barcode = result.wash_order_data[0]['barcode']
				    self.order_number = result.wash_order_data[0]['order_number']
				    self.order_type = result.wash_order_data[0]['type_of_order']
				    self.dangerous_char = result.wash_order_data[0]['dangerous_characteristics']
				    self.variants = result.wash_order_data[0]['variants']
				    self.ler = result.wash_order_data[0]['ler']
				    self.un_code = result.wash_order_data[0]['un_code']
				    self.recycled_product_name = result.wash_order_data[0]['recycled_product']
				    self.state = result.wash_order_data[0]['state']
				$("#drying_end_wash_order").css("display", "inline");
				$("#destruction_wash_order").css("display", "inline");
				$("#drying_wash_order").css("display", "none");
				$("#backto_wash_order").css("display", "none");
				return  self.$el.html(QWeb.render("ContainerDryingDisplay", {widget: self}));

				}
		else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

},


containertransfer_button: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	var number_of_barcode = self.barcode; 
	var ctx = {};
	$('.modal-backdrop').remove();
	ctx['container_transfer_wash_order']= "True";
	var emp = self.employee_id

	var transfer_location_id =  $("#transfred_location").val()
     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'transfer_to_storewash',
		context : ctx,
                args: [[],number_of_barcode , transfer_location_id,emp],
               }) 
		.then(function(result){
		if (result.success) {
				$('.modal-backdrop').remove();
				 self.$el.html(QWeb.render("ConfirmWash", {widget: self}));
			setTimeout(function () {
				self.do_action('ballester_wash.action_ballester_container_drying_control_screen');
			    }, 2000);

				}
		else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

},

ProductOnChangeEvent: function (event)
    {	
        var selectedproductValue = document.getElementById('product').value;
        var domain_dp = []
	$('.modal-backdrop').remove();
	if (selectedproductValue != undefined){

		var first_step = selectedproductValue.split("[")
		var second_step = first_step[1].split("]")
		
            	domain_dp.push(['default_code', '=', second_step[0]])
		}
        this._rpc({
            model: 'operation.wash.dashboard',
            method: 'product_data',
            args: [domain_dp],
        })
        .then(function (result) {
		if(result.lot_list != [])
		{
		   var lot_list = result.lot_list
		   var optionsAsString = "";
	           for(var i = 0; i < Object.keys(lot_list).length  ; i++)
			{
			     var lot_detail = lot_list[i]
                            optionsAsString += "<option value='" + lot_detail['name'] + "'" + "ids='"+ lot_detail['id'] +"'>" + lot_detail['name'] + "</option>";
		            
			}
		$( '.barcodes' ).append( optionsAsString );
		}

		else {
		     $('.barcodes').val('');
		}
		if (result.pro_name != '') {
				
			 $('#product_description_id').val(result.pro_name);
			}

		else{
			 $('#product_description_id').val('');
			}

		  
        });

},


products: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
        var product = document.getElementById("product").value ;
	var repair_order = self.repair_order
        var wash_order = self.wash_order
        var number_of_barcode = self.barcode; 
	var ctx = {};
	$('.modal-backdrop').remove();

        if (product){
		self._rpc({
                model: 'operation.wash.dashboard',
                method: 'get_product_data',
		context : ctx,
                args: [[],product],
               }) 
		.then(function(result){
			
		});
		
		}
			
	
},

view_repair_order_button: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	$('.modal-backdrop').remove();

	var number_of_barcode = $("#barcode_number").val();
	self._rpc({
                model: 'operation.wash.dashboard',
                method: 'view_repair_data',
                args: [[],number_of_barcode],
               }) 
		.then(function(result){
		
		if (result.repair_data){
	            self.img_url = result.repair_data[0]['img_url']
		    self.barcode = result.repair_data[0]['barcode']
		    self.order_number = result.repair_data[0]['order_number']
		    self.order_type = result.repair_data[0]['type_of_order']
		    self.dangerous_char = result.repair_data[0]['dangerous_characteristics']
		    self.variants = result.repair_data[0]['variants']
		    self.repair_state = result.repair_data[0]['state']
		    self.ler = result.repair_data[0]['ler']
		    self.un_code = result.repair_data[0]['un_code']
		    self.recycled_product_name = result.repair_data[0]['recycled_product']
		    self.delivery_location = result.repair_data[0]['delivery_location']
		    self.delivery_location = result.repair_data[0]['delivery_location']
		    self.repair_order = result.repair_data[0]['repair_order']
		    self.add_repair = true
		    self.start_button =true
		    self.wash_order = result.repair_data[0]['wash_id']
		$('.modal-backdrop').remove();
		return  self.$el.html(QWeb.render("RepairOrderDisplay", {widget: self}));

		}
		});
},

/**add_repair_part: function(event){
	var self = this; 
       event.stopPropagation();
       event.preventDefault();
	var repair_order = self.repair_order;
	var number_of_barcode = self.barcode; 
	var ctx = {};
	ctx['add_repiar_parts']= "True";
	var table = document.getElementById("repair_parts_table");    
        var table_row = document.getElementById("repair_parts_table").rows;
        var product_list =[]
	var product_selection = ''
	
	self._rpc({
            model: 'product.product',
            method: 'name_search',
	    args: ['', [],'ilike'],
		
        })
        .then(function (result) {
	if(result ! = undefined) {
	    var product_selection = '<select class="products" id="product" style="overflow-y: auto!important; font-size: 18px;">'
		$(".products").editableSelect();
		var size = 0, key;
		    for (key in result) {
			if (result.hasOwnProperty(key)) size++;
		    }
	       for(var i=0 ; i <= size; i++ ){
			var product_info = result[i]
			if (product_info){
				      var name=  product_info[1]
					name = name.replace("''","");
					product_selection +=
					"<option  value='"+ name + "'"+  "ids='" + product_info[0] + "'>"  + name + "</option> "
			}
		} 
	
	   product_selection += '</select>'
		}
	else{
	    var product_selection ='<select class="products" id="product"  style="overflow-y: auto!important; font-size: 18px;"><option> No Data Found !</option> </select>' 
		
		}

        $(".products").editableSelect();
	self._rpc({
                model: 'operation.wash.dashboard',
                method: 'get_repair_data',
		context : ctx,
                args: [[],repair_order],
               }) 
		.then(function(result){
		if (result.success) {
     	            if (table_row.length > 2){
			   $(".products").editableSelect();
		    	   $( "#repair_parts_table tr:nth-last-child(2)").after("<tr class='active'>"+
		    			   "<td style='width: 50%;' >"+ product_selection + "</td>"+
					 "<td style='width: 40%; '> <input type='number' name='qty' class='product_qty' min='0' max='100' id='product_qty' style='height: 40px;'/></td>"+
		    			  
		    			   "<td style='width: 10%;'><button class='fa fa-trash-o btndelete' name='delete' aria-hidden='true'/></td>"+
		    			   "</tr>");
		       }
			else{
			$(".products").editableSelect();
			$( '#repair_parts_table').prepend("<tr class='active'>"+
		    			   "<td style='width: 50%;' >"+ product_selection +"</td>"+
					 "<td style='width: 40%; '> <input type='number' name='qty' class='product_qty' min='0' max='100' style='height: 40px;' id='product_qty'/></td>"+
		    			   
		    			   "<td style='width: 10%;'><button class='fa fa-trash-o btndelete' name='delete' aria-hidden='true'/></td>"+
		    			   "</tr>");


			}
		       $(".products").editableSelect();
		}
	
	});
	
	}); 
},**/


add_repair_part: function(event){
	var self = this; 
       event.stopPropagation();
       event.preventDefault();
	var repair_order = self.repair_order;
	var number_of_barcode = self.barcode; 
	var ctx = {};
	ctx['con_add_repair_parts']= "True";
	var table = document.getElementById("repair_parts_table");    
        var table_row = document.getElementById("repair_parts_table").rows;
        var product_list =[]
	var product_selection = ''
	$('.modal-backdrop').remove();
	
	$(".products").editableSelect();
	self._rpc({
                model: 'operation.wash.dashboard',
                method: 'get_repair_data',
		context : ctx,
                args: [[]],
               }) 
		.then(function(result){
		if (result.success) {
     	            if (table_row.length > 2){
			   $(".products").editableSelect();
		    	   $( "#repair_parts_table tr:nth-last-child(2)").after("<tr class='active'>"+
		    			   "<td style='width: 50%;' >"+ result.product_list + "</td>"+
					 "<td style='width: 40%; '> <input type='number' name='qty' class='product_qty' min='0' max='100' id='product_qty' style='height: 40px;'/></td>"+
		    			  
		    			   "<td style='width: 10%;'><button class='fa fa-trash-o btndelete' name='delete' aria-hidden='true'/></td>"+
		    			   "</tr>");
		       }
			else{
			$(".products").editableSelect();
			$( '#repair_parts_table').prepend("<tr class='active'>"+
		    			   "<td style='width: 50%;' >"+ result.product_list +"</td>"+
					 "<td style='width: 40%; '> <input type='number' name='qty' class='product_qty' min='0' max='100' style='height: 40px;' id='product_qty'/></td>"+
		    			   
		    			   "<td style='width: 10%;'><button class='fa fa-trash-o btndelete' name='delete' aria-hidden='true'/></td>"+
		    			   "</tr>");


			}
		       $(".products").editableSelect();
		}
	
	});
	
},



add_part_button: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	var number_of_barcode = self.barcode; 
	var ctx = {};
	$('.modal-backdrop').remove();
	return  self.$el.html(QWeb.render("AddPartsRepair", {widget: self}));

},

compliance_wash_order: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	$('.modal-backdrop').remove();
	var barcode = $("#barcode_number").val();
	var number_of_barcode = ''
        if (barcode != undefined){

		number_of_barcode= barcode
	}
	else{
		number_of_barcode = self.barcode
	
	} 
        
	var ctx = {};
	ctx['compliance_wash_order']= "True";
     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'check_compliance',
		context : ctx,
                args: [[],number_of_barcode],
               }) 
		.then(function(result){
		
		if (result.question_set) {

			if(result.wash_order_data){

				 self.img_url = result.wash_order_data[0]['img_url']
		    self.barcode = result.wash_order_data[0]['barcode']
		    self.order_number = result.wash_order_data[0]['order_number']
		    self.order_type = result.wash_order_data[0]['type_of_order']
		    self.dangerous_char = result.wash_order_data[0]['dangerous_characteristics']
		    self.variants = result.wash_order_data[0]['variants']
		    self.state = result.wash_order_data[0]['state']
		    self.ler = result.wash_order_data[0]['ler']
		    self.un_code = result.wash_order_data[0]['un_code']
		    self.recycled_product_name = result.wash_order_data[0]['recycled_product']
		    self.delivery_location = result.wash_order_data[0]['delivery_location']
				if(result.wash_order_data[0]['state'] == 'quality_control')

				{	
					self.repair_button = true
					self.continue_button = false

					}

				}
			self.question_set = result.question_set
		        self.choice =  result.question_set
			self.wash_order =  result.wash_order
			self.survey_id =  result.survey_id
			self.page_id =  result.page_id
			self.question_id =  result.question_id
			self.barocde =   result.barocde
			self.location_id =  result.location_id
			self.dest_location_id =   result.dest_location_id
			$('.modal-backdrop').remove();
			return  self.$el.html(QWeb.render("ComplianceDisplay", {widget: self}));
		     
				}
		else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

},


repairorder_button: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
        
	var wash_order = self.wash_order; 
	$('.modal-backdrop').remove();
	var ctx = {};
     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'create_repair',
		context : ctx,
                args: [[],wash_order],
               }) 
		.then(function(result){
		  if (result.repair_data) {
			self.add_repair = true
			self.repair_state = result.repair_data[0]['repair_state']
			self.repair_order = result.repair_data[0]['repair_order']
			return  self.$el.html(QWeb.render("RepairOrderDisplay", {widget: self}));
		     
				}
		else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

},

repairorder_button_screen: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
        var barcode = $("#barcode_number").val(); 
        var number_of_barcode = ''
	if(barcode != undefined){
		var number_of_barcode = barcode
	}
	else{
		var number_of_barcode = self.barcode

	}
	$('.modal-backdrop').remove();
	var ctx = {};
     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'create_repair_screen',
		context : ctx,
                args: [[],number_of_barcode],
               }) 
		.then(function(result){
		  if (result.repair_data) {
			self.add_repair = true
			self.barcode = result.wash_order_data[0]['barcode']
		    self.order_number = result.wash_order_data[0]['order_number']
		    self.order_type = result.wash_order_data[0]['type_of_order']
		    self.dangerous_char = result.wash_order_data[0]['dangerous_characteristics']
		    self.variants = result.wash_order_data[0]['variants']
		    self.state = result.wash_order_data[0]['state']
		    self.img_url = result.wash_order_data[0]['img_url']
		    self.ler = result.wash_order_data[0]['ler']
		    self.un_code = result.wash_order_data[0]['un_code']
		    self.recycled_product_name = result.wash_order_data[0]['recycled_product']
		    self.delivery_location = result.wash_order_data[0]['delivery_location']
			self.wash_order = result.repair_data[0]['wash_id']
			self.repair_state = result.repair_data[0]['repair_state']
			self.repair_order = result.repair_data[0]['repair_order']
			return  self.$el.html(QWeb.render("RepairOrderDisplay", {widget: self}));
		     
				}
		else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

},

stoprepairorder_button: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	var repair_order = self.repair_order; 
	var ctx = {};
     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'stop_repair',
		context : ctx,
                args: [[],repair_order],
               }) 
		.then(function(result){
		  if (result.success) {
			$('.modal-backdrop').remove();
			self.compliance_button =true
			self.repair_state = 'done'
			return  self.$el.html(QWeb.render("RepairOrderDisplay", {widget: self}));
		     
				}
		else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

},


repair_compliance_button: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	
	var repair_order = self.repair_order; 
	var wash_order = self.wash_order; 
	var ctx = {};
	console.log("dddddd<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'check_repair_compliance',
		context : ctx,
                args: [[],repair_order],
               }) 
		.then(function(result){
		  if (result.question_set) {
			console.log(">>>>>>>>>>>>>>",result)
			self.question_set = result.question_set
		        self.choice =  result.question_set
			self.survey_id =  result.survey_id
			self.emp_id =  result.emp_id
			self.page_id =  result.page_id
			self.question_id =  result.question_id
			$('.modal-backdrop').remove();
			return  self.$el.html(QWeb.render("ComplianceDisplay", {widget: self}));
		     
				}
		else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

},



startrepairorder_button: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	var repair_order = self.repair_order;
	var ctx = {};
     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'start_repair',
		context : ctx,
                args: [[],repair_order],
               }) 
		.then(function(result){
		  if (result.success) {
                         console.log("ssssssssssssself",self)
			 $('.modal-backdrop').remove();
			self.end_button =true
			self.repair_state = 'under_repair'
			
			var action = self.$el.html(QWeb.render("RepairOrderDisplay", {widget: self}));
			$('.modal-backdrop').remove();
			return  action;
		     
				}
		  else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

},

 save_repair_parts: function(event){
	   	var self = this;
		$('.modal-backdrop').remove();
	   	event.stopPropagation();
	   	event.preventDefault();
		var repair_order = self.repair_order;
		var record_data= [];
			    //	 append product to create barcode
	   		var allow_save = true;
	   		$('#repair_parts_table tr.active').each(function(){
		  		var product = $(this).find('td .products')

		  		if (product.val() == ''){
		  			product.css('border-bottom-color','red');
		  			allow_save = false
		  		}else{
		  			product.css('border-bottom-color','#ccc');
		  		}
	   		})
	   		if (allow_save == true){
	   		    var count_lines = 0
			  	$('#repair_parts_table tr.active').each(function(){
			  		count_lines += 1;
			  			var product_ids = $(".es-list li[value='" + $(this).find('td .products').val() + "']").attr('ids');
				
			var qty = document.getElementById('product_qty').value;

			 if ( product_ids != undefined && qty != undefined ){
			   	    			record_data.push({
				   	    		    'product': product_ids,
								'qty' :qty,
				   	    		});
						}
			   	    	
			   	})
			
			   if  (count_lines == record_data.length) {
				   self._rpc({
			                model: 'operation.wash.dashboard',
			                method: 'save_repair_part',
			                args: [[],record_data,repair_order],
			            })
			            .then(function(result) {
			            	if (result.success) {
			            		// readonly location           		
			            		$('#repair_parts_table tr.active').each(function(i){
			            			 var html = $(this).html();
			        				 var span = $("<tr class='active'>"+
			        						"<td style='width: 50%;'  class='set_product_ids'><span id='product_value'>"+ result.repair_data[i]['product_id'] +"</span></td>"+

"<td style='width: 50%;'  class='set_qty'><span id='set_qty'>"+  result.repair_data[i]['price_unit']+"</span></td>"+
                                                                    
			            		            "</tr>");
			                         $(this).replaceWith(span);
							   	})
			            		 $("#save_repair_parts").css("display", "none");
			            		// display validate barcode button
			            		 $("#edit_repair_parts").css("display", "inline");
			            		// display edit barcode button
			            		 $("#backto_repair").css("display", "inline");
			            		// remove add an item
			            		$('#repair_parts_table #add_an_item').remove();
			            		self.do_warn(_("Success"),result.success);
			            		
			            	}else{
			            		self.do_warn(_("Warning"),result.warning);
			            	}
		             });
			   }
	   		}else{
	   		 self.do_warn(_("Warning"),_("Please fill in all the required fields !"));
	   		}
	   		  
	    
	  },



 edit_repair_parts: function(event){
		   	var self = this;
		   	event.stopPropagation();
		   	event.preventDefault();
		   	var barcode_data = []
          //edit inventory adjustments
			$('.modal-backdrop').remove();
		   	$('#repair_parts_table tr.active').each(function(i){
     			     var product = $(this).find('td.set_product_ids');
			   	var barcode = $(this).find('td.set_lot_id');
				var qty = $(this).find('td.set_qty');
				var name =  $(this).find('td.set_name');
				var product_list =[]
				var product_selection = ''
				var barcode_selection = ''
				
				self._rpc({
				    model: 'product.product',
				    method: 'name_search',
				    args: ['', [],'ilike'],
					
				})
				.then(function (result) {
				if(result ! = undefined) {
				    var product_selection = '<select class="products" id="product" style="overflow-y: auto!important; font-size: 18px;">'
				
					var size = 0, key;
					    for (key in result) {
						if (result.hasOwnProperty(key)) size++;
					    }
				       for(var i=0 ; i <= size; i++ ){
						var product_info = result[i]
						if (product_info){
					      var name=  product_info[1]
						var pro_name = name.replace("''","");

						if (name == product.text()){
						product_selection +=
						"<option  selected='selected' value='"+pro_name + "'"+  "ids='" + product_info[0] + "'>"  + pro_name + "</option> "
						
						}else{
                                               product_selection +=
						"<option  value='"+pro_name + "'"+  "ids='" + product_info[0] + "'>"  + pro_name + "</option> "

						}
						}
				}
				
				   product_selection += '</select>'
					}
				else{
				    var product_selection ='<select class="products" id="product"  style="overflow-y: auto!important; font-size: 18px;"><option> No Data Found !</option> </select>' 
					
					}


		 var domain_dp = []
		product = document.getElementById('product').value;
		var first_step = product.split("[")
		var second_step = first_step[1].split("]")
            	domain_dp.push(['default_code', '=', second_step[0]])
					this._rpc({
					    model: 'operation.wash.dashboard',
					    method: 'product_data',
					    args: [domain_dp],
					})
					.then(function (result) {
						if(result.lot_list != [])
						{
						barcode_selection ='<select class="select2 barcodes" id ="barcode" style="overflow-y: auto!important; font-size: 18px;">'
						   var lot_list = result.lot_list
						   console.log("OOOOOOOrelot_listOOOOO",Object.keys(lot_list).length)
						   for(var i = 0; i < Object.keys(lot_list).length  ; i++)
							{

							     var lot_detail = lot_list[i]
							    console.log(">>>>>lot_list>>>>>>>>>>>", lot_detail['name'] )
							if( lot_detail['name'] == barcode.text()){
							barcode_selection += "<option selected='selected' value='" + lot_detail['name'] + "'" + "ids='"+ lot_detail['id'] +"'>" + lot_detail['name'] + "</option>";

							}
							else{
							    barcode_selection += "<option value='" + lot_detail['name'] + "'" + "ids='"+ lot_detail['id'] +"'>" + lot_detail['name'] + "</option>"; }
							    
							}
						console.log("<<<<<<<<<optionsAsString<<<<Sdcdc",optionsAsString)
						 barcode_selection += '</select>'
						}
				
	              var data = "<tr class='active'>"+
	                         "<td style='width: 25%;' class='set_product_ids'>"+product_selection+"</td>"+
	                         "<td style='width: 15%;' class='set_name'>"+ name.html() +"</td>"+
	                         "<td style='width: 20%;' class='set_lot_id'>"+barcode_selection+"</td>"+
	                         "<td style='width: 15%; class='location'>" +"</td>"+
	                         "<td style='width: 15%;'  class='dest_location'>"+ "</td>"+
	                         "<td style='width: 10%;'  class='set_qty'>"+qty.html()+"</td>"+
	                         "</tr>"
	              $(this).replaceWith(data);
			 });
			});
		   	})
		   	$('.products')
		       .editableSelect();
                       $(".locations").editableSelect();
			$(".dest_locations").editableSelect();
	        $("#repair_parts_table tbody").append("<tr id='add_an_item'>" +
                    "<td colspan='4' class='o_field_x2many_list_row_add add_repair_part'>" +
                    "<a href='#'>Add Repair Parts</a>" +
                    "</td></tr>")
            // hide validate button 
	        $("#edit_repair_parts").css("display", "none");
	        // visible save button
	        $("#save_repair_parts").css("display", "inline");
 	  },



backto_repair: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	var repair_order = self.repair_order;
	var ctx = {};
	self.start_button = true
	self.add_repair = false
	$('.modal-backdrop').remove();
	return self.$el.html(QWeb.render("RepairOrderDisplay", {widget: self}));
},


dryingendwash_button: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	var barcode = $("#barcode_number").val(); 
        var number_of_barcode = ''
	if(barcode != undefined){
		var number_of_barcode = barcode
	}
	else{
		var number_of_barcode = self.barcode

	}
	var ctx = {};
	ctx['end_drying_wash_order']= "True";
	var emp = self.employee_id 
     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'search_barcode',
		context : ctx,
                args: [[],number_of_barcode,emp],
               }) 
		.then(function(result){
		if (result.success) {
				$('.modal-backdrop').remove();
				self.continue_button = true
                                self.stop_drying = false
				self.check_compliance = true
					if (result.wash_order_data){
				   self.img_url = result.wash_order_data[0]['img_url']
				    self.barcode = result.wash_order_data[0]['barcode']
				    self.order_number = result.wash_order_data[0]['order_number']
				    self.order_type = result.wash_order_data[0]['type_of_order']
				    self.dangerous_char = result.wash_order_data[0]['dangerous_characteristics']
				    self.variants = result.wash_order_data[0]['variants']
				    self.ler = result.wash_order_data[0]['ler']
				    self.un_code = result.wash_order_data[0]['un_code']
				    self.recycled_product_name = result.wash_order_data[0]['recycled_product']
				    self.state = result.wash_order_data[0]['state']
				   console.log("OOOOOOOOOOOOOOOOOOOO",self)

					}
				$("#backto_wash_order").css("display", "inline");
				$('.modal-backdrop').remove();
				  return  self.$el.html(QWeb.render("ContainerDryingDisplay", {widget: self}));

				}
		else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

},

backto_wash_button: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	var barcode = $("#barcode_number").val(); 
        var number_of_barcode = ''
	if(barcode != undefined){
		var number_of_barcode = barcode
	}
	else{
		var number_of_barcode = self.barcode

	}
	var reason_text = $("#backorder_reason").val(); 
	var ctx = {};
	ctx['backto_wash_order']= "True";
	ctx['reason'] = reason_text;
	var emp = self.employee_id 
	$('.modal-backdrop').remove();
     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'search_barcode',
		context : ctx,
                args: [[],number_of_barcode,emp],
               }) 
		.then(function(result){
		if (result.warning) {
			self.do_warn(_("Warning"),_("Please enter reason for back to Wash!"));
			
				}
		if (result.success){
				$('.modal-backdrop').remove();
	            		 self.$el.html(QWeb.render("ConfirmWash", {widget: self}));
			setTimeout(function () {
				self.do_action('ballester_wash.action_ballester_container_drying_control_screen');
			    }, 2000);
	            	}

           
        });

},


repair_order_backscreen: function(event){
	var self = this;
	   	event.stopPropagation();
	   	event.preventDefault();
		var ctx = {};
		$('.modal-backdrop').remove();
		var wash_order = self.wash_order
		if (self.repair_state == 'under_repair'){
		       self.end_button =true}
		else if (self.repair_state == 'done')
					{
					self.compliance_button =true
					}
			
	        return self.$el.html(QWeb.render("RepairOrderDisplay", {widget: self}));

	
},
compliance_submit: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	var compliance_value = event.target.value;
	var survey_id = self.survey_id; 
	var wash_order = self.wash_order; 
	var emp_id = self.employee_id; 
        var page_id = self.page_id;
	var question_id = self.question_id
	var question_set = self.question_set
        var choice = []
	var answer_set = []
	var questions =[]
	$('.modal-backdrop').remove();
	if (question_set != undefined) {
			for(var i = 0; i < Object.keys(question_set).length  ; i++)
					{
					     var question_detail = question_set[i]
				            console.log(">>>>>lot_list>>>>>>>>>>>", question_detail['choice'] )
					    /** for(var i = 0; i < Object.keys(question_detail['choice']).length  ; i++)
						{
						var choice_detail = question_detail['choice'][i]
						console.log('UUUUUUUUUUUUUUUUUUUsassxsxsxs',choice_detail['answer'])
						choice.push(choice_detail['answer'])
						
						}**/
					console.log(">question_detail['question_id']>>>>>", question_detail['question_id'] )
					questions.push(question_detail['question_id'])
					}
		

	}

		if(questions ){
			for(var q = 0; q < Object.keys(questions).length; q++)
			{
			var rates = document.getElementsByName(questions[q]);
			var rate = $("input:radio[name="+questions[q] + "]:checked").val()
			if (rate != undefined)
				{
					answer_set.push({
						'question_id' : questions[q],
						'value': rate
					})
				}
			else
				{
					return self.do_warn(_("Warning"),_("Please answer all your questions!"));
				}
			
			}
		}
	var ctx = {};
	ctx['end_drying_wash_order']= "True";

	
	if (self.repair_order) {
		self.state = 'repair_create'
		var repair_order = self.repair_order 
		 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'compliance_repair_value',
		context : ctx,
                args: [[],answer_set,survey_id,repair_order,emp_id, page_id ,questions ],
               }) 
		.then(function(result){
		if (result.success) {
				$('.modal-backdrop').remove();
				return  self.$el.html(QWeb.render("ConfirmComplinaceWash", {widget: self}));

				}

		if (result.negative_success) {
				self.repait_negative_answer = true
				$('.modal-backdrop').remove();
				return  self.$el.html(QWeb.render("ConfirmComplinaceWash", {widget: self}));

				}

		if (result.warning){


	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

		    
        });

		}
	else  {


     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'compliance_value',
		context : ctx,
                args: [[],answer_set,survey_id,wash_order,emp_id, page_id ,questions ],
               }) 
		.then(function(result){
		if (result.success) {
				$('.modal-backdrop').remove();
				return  self.$el.html(QWeb.render("ConfirmComplinaceWash", {widget: self}));

				}

		if (result.negative_success) {
				self.transfer_button = true
				$('.modal-backdrop').remove();
				return  self.$el.html(QWeb.render("ConfirmComplinaceWash", {widget: self}));

				}

		if (result.warning){


	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

	}

},





/**compliance_value: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	console.log(">>>>>>compliance_value>>>>>>>>>>>>>", self)
	var compliance_value = event.target.value;
	var survey_id = self.survey_id; 
	var wash_order = self.wash_order; 
	var emp_id = self.emp_id; 
        var page_id = self.page_id;
	var question_id = self.question_id
	var ctx = {};
	console.log(">>>>>>compliance_value>>>>>>>>>>>>>", compliance_value)
	ctx['end_drying_wash_order']= "True";
	if (self.repair_order) {
		self.state = 'repair_create'
		var repair_order = self.repair_order 
		console.log("<Z#3333333333333333333333",repair_order)
		 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'compliance_repair_value',
		context : ctx,
                args: [[],compliance_value,survey_id,repair_order,emp_id, page_id ,question_id ],
               }) 
		.then(function(result){
		if (result.success) {
				return  self.$el.html(QWeb.render("ConfirmComplinaceWash", {widget: self}));

				}
		else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

		    
        });
		

		}
	else  {
		
		var answer =document.getElementById(compliance_value)
		console.log("wewwwwwwwwwwanswerwwwwwwwww",answer )
                $(".compliance_value").replace(" <span style='width: 25%;'>" + compliance_value+ "</span>");

		
     	self._rpc({
                model: 'operation.wash.dashboard',
                method: 'compliance_value',
		context : ctx,
                args: [[],compliance_value,survey_id,wash_order,emp_id, page_id ,question_id ],
               }) 
		.then(function(result){
		if (result.success) {
				return  self.$el.html(QWeb.render("ConfirmComplinaceWash", {widget: self}));

				}
		else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

	}

},**/


destructionwash_button: function(event){
	var self = this;
        event.stopPropagation();
        event.preventDefault();
	var barcode = $("#barcode_number").val(); 
        var number_of_barcode = ''
	if(barcode != undefined){
		var number_of_barcode = barcode
	}
	else{
		var number_of_barcode = self.barcode

	} 
	$('.modal-backdrop').remove();
        console.log("")
	var ctx = {};
	var emp = self.employee_id 
	ctx['destruction_wash_order']= "True";
     	 self._rpc({
                model: 'operation.wash.dashboard',
                method: 'search_barcode',
		context : ctx,
                args: [[],number_of_barcode,emp],
               }) 
		.then(function(result){
		if (result.success) {
			$('.modal-backdrop').remove();
			  self.$el.html(QWeb.render("ConfirmWash", {widget: self}));
			setTimeout(function () {
				self.do_action('ballester_wash.action_ballester_container_drying_control_screen');
			    }, 2000);

				}
		else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}

           
        });

},



    product_wash: function(event){
   	 var self = this;
        event.stopPropagation();
        event.preventDefault();
	var ctx = {};
	var product_id = $(".es-list li[value='" + $(".product_wash").val() + "']").attr('ids');
	var recycled_product_id = $(".es-list li[value='" + $(".product_recycled").val() + "']").attr('ids');
	var type_of_order = $(".select").val() ;
	ctx['product_id']= product_id
	if (recycled_product_id == undefined){
	$(".product_recycled").editableSelect();
     $('#my-wash-product')
		       .editableSelect()
		       .on('select.editable-select', function (e, li) {
		    	   var recycled_pro = event.target.getAttribute("recycled_product_id");
		           var product_id =  $(".es-list li[value='" + $(".product_wash").val() + "']").attr('ids');

		           var current_product_id = $(this).find('#my-wash-product').val();
			           if(current_product_id === product_id){
			        	   $(this).find('#my-recycled-product').val(recycled_pro)
		           }
})
                 $("#recycled").after(" <div class='col-md-3' style='width:350px'>"+ self.recycled_product + "</div>"

		);}
    },

// create wash order

	create_wash_order : function(event){
	   	var self = this;
	   	event.stopPropagation();
	   	event.preventDefault();
		var barcode_list = [];
		$('.modal-backdrop').remove();
	   	var location = $(".es-list li[value='" + $(".locations").val() + "']").attr('ids');
                var product_id = $(".es-list li[value='" + $(".product_wash").val() + "']").attr('ids');
                var recycled_product_id =  $(".es-list li[value='" + $(".product_recycled").val() + "']").attr('ids');
                var dest_location_id =  $(".es-list li[value='" + $(".dest_locations").val() + "']").attr('ids');
		var type_of_order = $(".select").val() ;
               var barcode_ids =  $("#barcode_wash").attr("ids");
		$("#barcode_wash :selected").each(function(){
			barcode_list.push(parseInt($(this).attr("ids")))
		    });
	   	var report_data = [];
	   	if (location != undefined &&  product_id != undefined   &&  recycled_product_id != undefined   && dest_location_id != undefined  &&  type_of_order != undefined){
		   	report_data.push({
				'location': location,
				'product_id': product_id,
				'recycled_product_id': recycled_product_id,
				'type_of_order': type_of_order,
				'dest_location_id': dest_location_id,
				'barcode_ids' :barcode_list,
 				});
			console.log(">>>>aseff>>>>>",location,product_id )
		        console.log(">>>>>report_data>>>>>",report_data)
			self._rpc({
			        model: 'operation.wash.dashboard',
			        method: 'create_wash_order_method',
			        args: [[],report_data ],
			    })
	            .then(function(result) {
	            	if (result.success) {
				$('.modal-backdrop').remove();
	            		return self.$el.html(QWeb.render("Confirm", {widget: self}));
	            	}else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}
	               });
        }else{
              self.do_warn(_("Warning"),_("Please Select Inventoried Location First!"));
  }
},


// Confirm main screen

	main_container_screen : function(event){
	   	var self = this;
	   	event.stopPropagation();
	   	event.preventDefault();
		$('.modal-backdrop').remove();
		self.repair_button = false
		self.transfer_button = false
	    return  self.do_action('ballester_wash.action_ballester_container_drying_control_screen');

},


// Confirm main screen

	container_compliance_screen : function(event){
	   	var self = this;
	   	event.stopPropagation();
	   	event.preventDefault();
		$('.modal-backdrop').remove();
		var ctx = {};
                console.log("fffffffffffffffffffffffff",self)
		var wash_order = self.wash_order
		self.repair_button = true
		self.continue_button = false
		if (wash_order != ''){
			   	//	 generating barcode
		        self._rpc({
		                model: 'operation.wash.dashboard',
		                method: 'display_order',
				context : ctx,
		                args: [[],wash_order],		            })
			
		.then(function(result) {
	            	if (result.success) {
				if (self.repair_order){
					self.state == 'repair_create'	
					self.transfer_button = true

					if (self.repair_negative_answer)
					{
						return  self.do_action('ballester_wash.action_ballester_container_drying_display_screen');

					}
				}
				self.state == 'quality_control'
				self.transfred_location =  result.wash_order_data[0]['transfer_location']
                                $('.modal-backdrop').remove();
	            		return self.$el.html(QWeb.render("ContainerDryingDisplay", {widget: self}));
	            	}else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}
	               });

				}

	
	
	
},




// cancel wash order

       cancel_wash_order : function(event){
	   	var self = this;
	   	event.stopPropagation();
	   	event.preventDefault();
		$('.modal-backdrop').remove();
    		// cancel all data
    		$("#image_container").css("display", "none");
		$("#table_detail").css("display", "none");
		$("#dryingtemplate").css("display", "none");
		$("#tr_detail").css("display", "none");
		$("#tr1_detail").css("display", "none");
		$("#tr4_detail").css("display", "none");
		$("#tr2_detail").css("display", "none");
		$("#tr3_detail").css("display", "none");
		$("#tr5_detail").css("display", "none");
		$("#tr6_detail").css("display", "none");
		$("#tr7_detail").css("display", "none");
	},


// onchnage wash product

       onchange_product : function(event){
	   	var self = this;
	   	event.stopPropagation();
	   	event.preventDefault();
                var product_id = $(".es-list li[value='" + $(".product_wash").val() + "']").attr('ids');
		var type_of_order = $(".select").val() ;
	   	var report_data = [];
		var barcode_list = [];
		var ctx = {};
		if ( product_id != undefined  ) {
			ctx['product_id']= product_id,
			ctx['type_of_order']=type_of_order
                        console.log("-----report_data-----------", ctx)
			self._rpc({
			         model: 'operation.wash.dashboard',
                                method: 'get_operation_info',
				 context : ctx,
				args :[]
                        })

	            .then(function(result) {
	               });
           }else{
              self.do_warn(_("Warning"),_("Please add wash product!!"));
  }
},



      validate_barcode: function(event){
	   	var self = this;
	   	event.stopPropagation();
	   	event.preventDefault();
	   	var location = $("#set_loction_id").attr('ids');
	   	var inventory_data = [];
		$('.modal-backdrop').remove();
	   	if (location != undefined){
		   	//	 append inventory id to validate barcode
		   	inventory_data.push(document.getElementById("created_inventory_id").value);
		   	//	 validating inventory adjustments
	        self._rpc({
	                model: 'operation.wash.dashboard',
	                method: 'validate_inventory_adjustments',
	                args: [[],inventory_data],
	            })
	            .then(function(result) {
	            	if (result.success) {
	            		self.do_warn(_("Success"),_("Successfully Validate the Barcode!"));
	            		// hide validate barcode button
	            		$("#edit_inventory_adjustments_button").css("display", "none");
	            		$("#validate_barcode_button").css("display", "none");
	            		// hide delete button
	            		$('#inventory_adjustments_table .btndelete').remove();
	            	}else{
	            		self.do_warn(_("Warning"),_("No Data Found!"));
	            	}
	            });
	    }else{
	    	   self.do_warn(_("Warning"),_("Please Select Inventoried Location First!"));
	       }
	    },
 	 btndelete: function(event){
		       var self = this;
		       event.stopPropagation();
		       event.preventDefault();
	    	       event.target.closest('tr').remove();
		       self.do_warn(_("Success remove"));
	    	   

	 },
	 
	   action_my_profile: function(event) {
	       var self = this;
	       event.stopPropagation();
	       event.preventDefault();
	       this.do_action({
	           name: _t("My Profile"),
	           type: 'ir.actions.act_window',
	           res_model: 'hr.employee',
	           res_id: self.employee_id,
	           view_mode: 'form',
	           view_type: 'form',
	           views: [[false, 'form']],
	           context: {},
	           domain: [],
	           target: 'inline'
	       },{on_reverse_breadcrumb: function(){ return self.reload();}})
	   },
});
core.action_registry.add('ballester_container_drying_display_screen_act', ContainerDryingDisplayScreen);

return ContainerDryingDisplayScreen;

});
