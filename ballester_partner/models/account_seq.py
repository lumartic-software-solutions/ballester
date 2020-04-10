# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Sales.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _


class Partner(models.Model):
    """Partner"""
    _inherit = "res.partner"
    

    @api.model
    def create(self,vals):
        partner = super(Partner, self).create(vals)
        sequence_obj = self.env['ir.sequence']
        customer_seq = sequence_obj.search([('name','=','Customer Sequence')])
        supplier_seq =   sequence_obj.search([('name','=','Supplier Sequence')])
        supplier_service_seq = sequence_obj.search([('name','=','Supplier service Sequence')])
        group_customer_id =self.env['account.group'].search([('name','=','430')])
        user_type_receivable_id= self.env['account.account.type'].search([('type',"=",'receivable')])
        group_supplier_id =self.env['account.group'].search([('name','=','400')])
        user_type_payable_id= self.env['account.account.type'].search([('type',"=",'payable')])
        group_service_id =self.env['account.group'].search([('name','=','410')])
        if vals.get('customer') and vals.get('entity'):
            account_code_customer_seq = customer_seq[0]._next()
            account_recievable_vals={
                'code':account_code_customer_seq,
                'name': partner.name,
                'user_type_id':user_type_receivable_id[0].id,
                'reconcile':True,
               # 'group_id':group_customer_id[0].id
            }
            account_recievable = self.env['account.account'].create(account_recievable_vals)
            partner.property_account_receivable_id = account_recievable[0].id
	
        if vals.get('supplier') and vals.get('entity'):
            account_code_supplier_seq = supplier_seq[0]._next()
            account_payable_vals={
                'code':account_code_supplier_seq,
                'name': partner.name,
                'user_type_id':user_type_payable_id[0].id,
                'reconcile':True,
              #  'group_id':group_supplier_id[0].id
            }
            account_payable = self.env['account.account'].create(account_payable_vals)
            partner.property_account_payable_id = account_payable[0].id
        if vals.get('is_vendor_service') and vals.get('entity'):
            account_code_service_seq = supplier_service_seq[0]._next()
            account_payable_vals={
                'code':account_code_service_seq,
                'name': partner.name,
                'user_type_id':user_type_payable_id[0].id,
                'reconcile':True,
              #  'group_id':group_service_id[0].id
            }
            account_payable = self.env['account.account'].create(account_payable_vals)
            partner.property_account_payable_id = account_payable[0].id
        return partner



    '''@api.multi
    def write(self,vals):
        partner = super(Partner, self).write(vals)
        sequence_obj = self.env['ir.sequence']
        customer_seq = sequence_obj.search([('name','=','Customer Sequence')])
        supplier_seq = sequence_obj.search([('name','=','Supplier Sequence')])
        supplier_service_seq = sequence_obj.search([('name','=','Supplier service Sequence')])
        account_code_customer_seq = customer_seq[0]._next()
        account_code_supplier_seq = supplier_seq[0]._next()
        account_code_service_seq = supplier_service_seq[0]._next()
        group_customer_id =self.env['account.group'].search([('code_prefix',"=",430)])
        user_type_receivable_id= self.env['account.account.type'].search([('type',"=",'receivable')])
        group_supplier_id =self.env['account.group'].search([('code_prefix',"=",400)])
        user_type_payable_id= self.env['account.account.type'].search([('type',"=",'payable')])
        group_service_id =self.env['account.group'].search([('code_prefix',"=",410)])
        if vals.get('customer'):
            account_recievable_vals={
                'code':account_code_customer_seq,
                'name': partner.name,
                'user_type_id':user_type_receivable_id[0].id,
                'reconcile':True,
                'group_id':group_customer_id[0].id
            }
            account_payable_vals={
                'code':account_code_supplier_seq,
                'name': partner.name,
                'user_type_id':user_type_payable_id[0].id,
                'reconcile':True,
                'group_id':group_supplier_id[0].id
            }
            account_payable = self.env['account.account'].create(account_payable_vals)
            account_recievable = self.env['account.account'].create(account_recievable_vals)
            partner.property_account_receivable_id = account_recievable[0].id
            partner.property_account_payable_id = account_payable[0].id
	
        if vals.get('supplier'):
            account_recievable_vals={
                'code':account_code_customer_seq,
                'name': partner.name,
                'user_type_id':user_type_receivable_id[0].id,
                'reconcile':True,
                'group_id':group_customer_id[0].id
            }
            account_payable_vals={
                'code':account_code_supplier_seq,
                'name': partner.name,
                'user_type_id':user_type_payable_id[0].id,
                'reconcile':True,
                'group_id':group_supplier_id[0].id
            }
            account_payable = self.env['account.account'].create(account_payable_vals)
            account_recievable  = self.env['account.account'].create(account_recievable_vals)
            partner.property_account_receivable_id = account_recievable[0].id
            partner.property_account_payable_id = account_payable[0].id
        if vals.get('is_vendor_service'):
            account_recievable_vals={
                'code':account_code_customer_seq,
                'name': partner.name,
                'user_type_id':user_type_receivable_id[0].id,
                'reconcile':True,
                'group_id':group_customer_id[0].id
            }
            account_payable_vals={
                'code':account_code_service_seq,
                'name': partner.name,
                'user_type_id':user_type_payable_id[0].id,
                'reconcile':True,
                'group_id':group_service_id[0].id
            }
            account_payable = self.env['account.account'].create(account_payable_vals)
            account_recievable  = self.env['account.account'].create(account_recievable_vals)
            partner.property_account_receivable_id = account_recievable[0].id
            partner.property_account_payable_id = account_payable[0].id
        return partner'''



