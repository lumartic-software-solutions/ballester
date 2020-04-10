# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Inventory.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api,_
from datetime import datetime
from odoo.tools.float_utils import float_compare


class StockProductionLot(models.Model):
    _inherit ='stock.production.lot'
    
    @api.model
    def default_get(self, fields):
        res = super(StockProductionLot, self).default_get(fields)
        print ("******res***************",res)
        return res


class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    '''manager_center_id = fields.Many2one('res.center',string="Manager Center", related="partner_id.manager_center_id")
    producer_center_id = fields.Many2one('res.center',string="Producer Center",related="partner_id.producer_center_id")
    cif_nif_nie = fields.Char(string="NIF/CIF/NIE",related="partner_id.cif_nif_nie")
    foreign_company_id = fields.Many2one('res.company',string="Foreign Company",related="partner_id.foreign_company_id")
    external_code = fields.Char(string="External Code",related="partner_id.external_code")
    association_type_code = fields.Char(string="Association Type Code",related="partner_id.association_type_code")
    tradename = fields.Char(string="Tradename",related="partner_id.tradename")
    business_name = fields.Char(string="Business Name",related="partner_id.business_name")
    lastname_1 = fields.Char(string="Lastname 1",related="partner_id.lastname_1")
    is_carrier = fields.Boolean(string="Is Carrier?",related="partner_id.is_carrier")
    carrier_center_id = fields.Many2one('res.center',string="Carrier Center",related="partner_id.carrier_center_id")
    transport_type_code = fields.Char(string="Transport Type Code",related="partner_id.transport_type_code")
    enrollment = fields.Char(string="Enrollment",related="partner_id.enrollment")
    com_autonomous_pass = fields.Char(string="Com Autonomous Pass",related="partner_id.com_autonomous_pass")
    itinerary = fields.Char(string="Itinerary",related="partner_id.itinerary")
    transport_form_code = fields.Char(string="Transport Form Code",related="partner_id.transport_form_code")
    product_id_1 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_id_1")
    product_id_2 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_id_2")
    product_id_3 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_id_3")
    product_id_4 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_id_4")
    product_id_5 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_id_5")
    expiry_date_1 = fields.Date(string="expiration date 1",related="partner_id.expiry_date_1")
    expiry_date_2 = fields.Date(string="expiration date 2",related="partner_id.expiry_date_2")
    expiry_date_3 = fields.Date(string="expiration date 3",related="partner_id.expiry_date_3")
    expiry_date_4 = fields.Date(string="expiration date 4",related="partner_id.expiry_date_4")
    expiry_date_5 = fields.Date(string="expiration date 5",related="partner_id.expiry_date_5")   
    teixo_response_1 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_1")
    teixo_response_2 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_2")
    teixo_response_3 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_3")
    teixo_response_4 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_4")
    teixo_response_5 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_5")
    product_ct_id_1 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_ct_id_1")
    product_ct_id_2 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_ct_id_2")
    product_ct_id_3 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_ct_id_3")
    product_ct_id_4 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_ct_id_4")
    product_ct_id_5 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_ct_id_5") 
    expiry_date_ct_1 = fields.Date(string="expiration date 1",related="partner_id.expiry_date_ct_1")
    expiry_date_ct_2 = fields.Date(string="expiration date 2",related="partner_id.expiry_date_ct_2")
    expiry_date_ct_3 = fields.Date(string="expiration date 3",related="partner_id.expiry_date_ct_3")
    expiry_date_ct_4 = fields.Date(string="expiration date 4",related="partner_id.expiry_date_ct_4")
    expiry_date_ct_5 = fields.Date(string="expiration date 5",related="partner_id.expiry_date_ct_5")
    teixo_response_ct_1 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_ct_1")
    teixo_response_ct_2 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_ct_2")
    teixo_response_ct_3 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_ct_3")
    teixo_response_ct_4 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_ct_4")
    teixo_response_ct_5 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_ct_5")
    product_di_id_1 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_di_id_1")
    product_di_id_2 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_di_id_2")
    product_di_id_3 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_di_id_3")
    product_di_id_4 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_di_id_4")
    product_di_id_5 = fields.Many2one('product.product',string="Select Product Residuo",related="partner_id.product_di_id_5")
    expiry_date_di_1 = fields.Date(string="expiration date 1",related="partner_id.expiry_date_di_1")
    expiry_date_di_2 = fields.Date(string="expiration date 2",related="partner_id.expiry_date_di_2")
    expiry_date_di_3 = fields.Date(string="expiration date 3",related="partner_id.expiry_date_di_3")
    expiry_date_di_4 = fields.Date(string="expiration date 4",related="partner_id.expiry_date_di_4")
    expiry_date_di_5 = fields.Date(string="expiration date 5",related="partner_id.expiry_date_di_5")                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      
    teixo_response_di_1 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_di_1")
    teixo_response_di_2 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_di_2")
    teixo_response_di_3 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_di_3")
    teixo_response_di_4 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_di_4")
    teixo_response_di_5 = fields.Char(string="Reply From Teixo",related="partner_id.teixo_response_di_5")
    state_di_1 = fields.Char(string="State From Teixo",related="partner_id.state_di_1")
    state_di_2 = fields.Char(string="State From Teixo",related="partner_id.state_di_2")
    state_di_3 = fields.Char(string="State From Teixo",related="partner_id.state_di_3")
    state_di_4 = fields.Char(string="State From Teixo",related="partner_id.state_di_4")
    state_di_5 = fields.Char(string="State From Teixo",related="partner_id.state_di_5")'''
    