# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Survey Extend.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).#
 
from odoo import models, fields, api
# new fields 

class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    purchase_order_id = fields.Many2one('purchase.order', 'Purchase Order')
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    wash_order_id = fields.Many2one('wash.order','Wash Order')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    repair_id = fields.Many2one('mrp.repair','Repair')
    
